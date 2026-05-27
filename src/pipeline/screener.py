"""
전체 파이프라인 오케스트레이터
MCP Tool들이 이 클래스를 통해 심사를 실행
"""
from dataclasses import dataclass, asdict, field
from typing import Literal
import json
from pathlib import Path

from src.collection.collector import DataCollector
from src.processing.quant_engine import QuantEngine, QuantResult
from src.processing.qual_engine import QualEngine, QualResult
from src.storage.db_handler import DBHandler
from src.storage.vector_handler import VectorHandler


@dataclass
class ScreeningResult:
    ticker: str
    final_verdict: Literal["COMPLIANT", "NON_COMPLIANT", "QUESTIONABLE", "ERROR"]
    confidence_score: float
    quant_summary: dict
    qual_summary: dict
    evidence_text: str
    needs_human_review: bool
    screening_standard: str = "AAOIFI"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_mcp_response(self) -> str:
        """MCP Tool 응답용 자연어 + 구조화 데이터 혼합 포맷"""
        verdict_emoji = {
            "COMPLIANT": "✅",
            "NON_COMPLIANT": "❌",
            "QUESTIONABLE": "⚠️",
            "ERROR": "🚫",
        }
        emoji = verdict_emoji.get(self.final_verdict, "?")

        lines = [
            f"## {emoji} {self.ticker} 샤리아 심사 결과: {self.final_verdict}",
            f"**신뢰도**: {self.confidence_score:.0%}  |  **기준**: {self.screening_standard}",
            "",
            "### 정량 심사",
            f"- 판정: {self.quant_summary.get('verdict')}",
            f"- 부채비율: {self.quant_summary.get('debt_ratio', 0):.1%}",
            f"- 이자수익 비율: {self.quant_summary.get('interest_income_ratio', 0):.1%}",
        ]

        if self.quant_summary.get("failed_criteria"):
            lines.append(f"- ❌ 실패 기준: {', '.join(self.quant_summary['failed_criteria'])}")
        if self.quant_summary.get("borderline_criteria"):
            lines.append(f"- ⚠️ 경계값 근접: {', '.join(self.quant_summary['borderline_criteria'])}")

        lines += [
            "",
            "### 정성 심사",
            f"- 판정: {self.qual_summary.get('verdict')}",
            f"- 업종 적합: {'✅' if self.qual_summary.get('sector_compliant') else '❌'}",
        ]

        if self.qual_summary.get("business_risks"):
            lines.append(f"- 위험요소: {', '.join(self.qual_summary['business_risks'])}")

        lines += [
            "",
            "### 종합 판단 근거",
            self.evidence_text,
        ]

        if self.needs_human_review:
            lines += [
                "",
                "> ⚠️ **전문가 검토 권고**: 경계값 케이스로 이슬람 금융 전문가의 추가 검토를 권장합니다.",
            ]

        return "\n".join(lines)


class ShariaScreener:
    """파이프라인 오케스트레이터 — MCP 서버의 모든 Tool이 이 클래스 사용"""

    def __init__(self):
        self.collector = DataCollector()
        self.quant = QuantEngine()
        self.qual = QualEngine()
        self.db = DBHandler()
        self.vector = VectorHandler()

    def screen(self, ticker: str, use_cache: bool = True) -> ScreeningResult:
        """단일 종목 심사 — 핵심 파이프라인"""
        ticker = ticker.upper().strip()

        # 0. 캐시 확인 (7일 이내 심사 결과)
        if use_cache:
            cached = self.db.get_latest_result(ticker)
            if cached and cached.get("age_days", 999) < 7:
                r = cached["result"]
                return ScreeningResult(
                    ticker=r["ticker"],
                    final_verdict=r["final_verdict"],
                    confidence_score=r["confidence_score"],
                    quant_summary=r["quant_summary"] or {},
                    qual_summary=r["qual_summary"] or {},
                    evidence_text=r["evidence_text"] or "",
                    needs_human_review=r["needs_human_review"],
                    screening_standard=r["screening_standard"],
                )

        try:
            # 1. 데이터 수집
            raw = self._load_or_collect(ticker)
            financial_data = self._extract_financial(raw)
            company_info = self._extract_company_info(raw)

            # 2. 정량 심사
            quant_result: QuantResult = self.quant.screen(ticker, financial_data)

            # 3. 정성 심사 (Quant FAIL이어도 근거 생성 위해 실행)
            qual_result: QualResult = self.qual.screen(ticker, company_info)

            # 4. 최종 판정
            final_verdict, confidence, evidence = self._judge(quant_result, qual_result)

            result = ScreeningResult(
                ticker=ticker,
                final_verdict=final_verdict,
                confidence_score=confidence,
                quant_summary={
                    "verdict": quant_result.verdict,
                    "debt_ratio": quant_result.debt_ratio,
                    "interest_income_ratio": quant_result.interest_income_ratio,
                    "non_halal_revenue_ratio": quant_result.non_halal_revenue_ratio,
                    "failed_criteria": quant_result.failed_criteria,
                    "borderline_criteria": quant_result.borderline_criteria,
                },
                qual_summary={
                    "verdict": qual_result.verdict,
                    "sector_compliant": qual_result.sector_compliant,
                    "business_risks": qual_result.business_risks,
                    "reasoning": qual_result.reasoning,
                    "confidence": qual_result.confidence,
                },
                evidence_text=evidence,
                needs_human_review=(
                    qual_result.needs_human_review or bool(quant_result.borderline_criteria)
                ),
            )

            # 5. 저장
            self.db.save_screening_result(result)
            self.vector.save_evidence(
                ticker, evidence,
                metadata={"verdict": final_verdict, "confidence": str(confidence)}
            )

            return result

        except Exception as e:
            return ScreeningResult(
                ticker=ticker,
                final_verdict="ERROR",
                confidence_score=0.0,
                quant_summary={},
                qual_summary={},
                evidence_text=f"심사 중 오류 발생: {str(e)}",
                needs_human_review=True,
            )

    def screen_batch(self, tickers: list[str]) -> list[ScreeningResult]:
        """복수 종목 배치 심사"""
        return [self.screen(t) for t in tickers]

    def _judge(
        self, quant: QuantResult, qual: QualResult
    ) -> tuple[str, float, str]:
        """Quant + Qual 결과 종합 판정"""
        # 명확한 FAIL
        if quant.verdict == "FAIL" or qual.verdict == "FAIL":
            verdict = "NON_COMPLIANT"
            confidence = 0.9 if quant.verdict == "FAIL" else qual.confidence

        # 둘 다 PASS
        elif quant.verdict == "PASS" and qual.verdict == "PASS":
            verdict = "COMPLIANT"
            confidence = min(0.95, 0.7 + qual.confidence * 0.3)

        # 하나라도 UNCERTAIN
        else:
            verdict = "QUESTIONABLE"
            confidence = 0.5

        # 근거 텍스트 조합
        quant_details = (
            ", ".join(quant.failed_criteria + quant.borderline_criteria)
            or "모든 수치 기준 통과"
        )
        evidence = f"[정량] {quant_details}\n\n[정성] {qual.reasoning}"

        return verdict, confidence, evidence

    def _load_or_collect(self, ticker: str) -> dict:
        """캐시된 JSON 또는 실시간 수집"""
        json_path = Path(f"data/{ticker}_raw.json")
        if json_path.exists():
            return json.loads(json_path.read_text(encoding="utf-8"))
        return self.collector.collect(ticker)

    def _extract_financial(self, raw: dict) -> dict:
        """raw JSON → 정량 심사용 재무 데이터"""
        bs = raw.get("balance_sheet", {})
        info = raw.get("info", {})

        # 대차대조표에서 가장 최근 날짜의 Total Debt 추출
        total_debt = 0
        if bs:
            latest_date = sorted(bs.keys(), reverse=True)[0] if bs else None
            if latest_date:
                total_debt = bs[latest_date].get("Total Debt") or 0

        return {
            "total_debt": total_debt or 0,
            "market_cap": info.get("marketCap") or 1,
            "interest_income": info.get("netInterestIncome") or 0,
            "total_revenue": info.get("totalRevenue") or 1,
            "non_halal_revenue": None,  # yfinance로 직접 분리 불가
        }

    def _extract_company_info(self, raw: dict) -> dict:
        """raw JSON → 정성 심사용 기업 정보"""
        info = raw.get("info", {})
        return {
            "sector": info.get("sector", ""),
            "business_summary": info.get("longBusinessSummary", ""),
            "products": info.get("longName", ""),
        }
