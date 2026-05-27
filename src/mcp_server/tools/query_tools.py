"""
결과 조회 도구들
이미 심사된 결과를 DB에서 조회
"""
from mcp.server.fastmcp import FastMCP
from src.storage.db_handler import DBHandler

_db = None


def get_db() -> DBHandler:
    global _db
    if _db is None:
        _db = DBHandler()
    return _db


def register_query_tools(mcp: FastMCP):

    @mcp.tool()
    def get_screening_result(ticker: str) -> str:
        """
        이미 심사된 종목의 최신 결과를 조회합니다.
        새로 심사하지 않고 DB에서 바로 가져옵니다.

        Args:
            ticker: 주식 티커

        Returns:
            가장 최근 심사 결과 또는 "심사 기록 없음" 메시지
        """
        result = get_db().get_latest_result(ticker.upper())
        if not result:
            return f"'{ticker}'의 심사 기록이 없습니다. screen_stock 도구로 새로 심사하세요."

        r = result["result"]
        return (
            f"## {ticker.upper()} 최근 심사 결과\n"
            f"- **판정**: {r['final_verdict']}\n"
            f"- **심사일**: {result.get('screened_at', '알 수 없음')}\n"
            f"- **신뢰도**: {r['confidence_score']:.0%}\n\n"
            f"{r.get('evidence_text', '')}"
        )

    @mcp.tool()
    def list_compliant_stocks(sector: str = None, limit: int = 20) -> str:
        """
        DB에 저장된 COMPLIANT(샤리아 준수) 종목 목록을 반환합니다.

        Args:
            sector: 특정 섹터로 필터링 (예: Technology, Healthcare)
                    None이면 전체 반환
            limit: 최대 반환 개수 (기본 20)

        Returns:
            COMPLIANT 종목 목록 및 기본 정보
        """
        stocks = get_db().list_compliant_stocks(sector=sector, limit=limit)
        if not stocks:
            return "저장된 COMPLIANT 종목이 없습니다."

        lines = [f"## ✅ 샤리아 준수 종목 목록 ({len(stocks)}개)"]
        if sector:
            lines[0] += f" — {sector} 섹터"

        lines += ["", "| 티커 | 섹터 | 신뢰도 | 심사일 |", "|------|------|--------|--------|"]
        for s in stocks:
            lines.append(
                f"| {s['ticker']} | {s.get('sector', '-')} "
                f"| {s.get('confidence', 0):.0%} | {s.get('screened_at', '-')} |"
            )

        return "\n".join(lines)

    @mcp.tool()
    def explain_screening_decision(ticker: str) -> str:
        """
        특정 종목의 심사 판단 근거를 상세히 설명합니다.
        왜 COMPLIANT/NON_COMPLIANT 판정을 받았는지 이해하고 싶을 때 사용.

        Args:
            ticker: 주식 티커

        Returns:
            판단 근거 전문 (정량 수치 해석 + LLM 정성 판단 내용)
        """
        result = get_db().get_latest_result(ticker.upper())
        if not result:
            return f"'{ticker}' 심사 기록 없음. screen_stock으로 먼저 심사하세요."

        r = result["result"]
        qual = r.get("qual_summary") or {}

        debt = r["quant_summary"].get("debt_ratio", 0) if r.get("quant_summary") else 0
        interest = r["quant_summary"].get("interest_income_ratio", 0) if r.get("quant_summary") else 0

        return (
            f"## {ticker.upper()} 심사 판단 근거\n\n"
            f"### 정량 분석\n"
            f"- 부채/시가총액: {debt:.2%} (기준: 33% 이하)\n"
            f"- 이자수익/매출: {interest:.2%} (기준: 5% 이하)\n\n"
            f"### 정성 분석 (GPT-4o 판단)\n"
            f"{qual.get('reasoning', '없음')}\n\n"
            f"### 발견된 위험요소\n"
            + "\n".join(f"- {risk}" for risk in qual.get("business_risks", ["없음"]))
        )
