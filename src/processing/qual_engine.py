"""
정성 심사 엔진 — GPT-4o로 업종/사업모델 할랄 여부 판단
"""
from dataclasses import dataclass
from typing import Literal
import json
import os


@dataclass
class QualResult:
    ticker: str
    verdict: Literal["PASS", "FAIL", "UNCERTAIN"]
    sector_compliant: bool
    business_risks: list[str]   # 발견된 위험 요소
    reasoning: str              # LLM 판단 근거 전문
    confidence: float           # 0.0 ~ 1.0
    needs_human_review: bool    # 판단 불가 케이스 플래그


SHARIA_SYSTEM_PROMPT = """
당신은 이슬람 금융(샤리아) 전문 심사관입니다.
AAOIFI(이슬람금융기관회계감사기구) 기준을 적용합니다.

## 금지 업종 (하람)
- 주류/담배 제조 및 유통
- 도박/카지노
- 포르노그래피
- 무기/방산 (논쟁적, 명시된 경우만)
- 이자 기반 금융 (은행, 보험, 리츠 일부)
- 돼지고기 관련

## 판단 지침
1. 사업 요약에서 위 업종 관련 수익 여부를 판단
2. 간접 수익(클라우드 서비스 제공 등)은 5% 이하 시 허용
3. 판단이 불가능한 경우 UNCERTAIN 반환, needs_human_review=true

## 응답 형식 (JSON만 반환, 마크다운 없이)
{
  "sector_compliant": true/false,
  "verdict": "PASS" | "FAIL" | "UNCERTAIN",
  "business_risks": ["위험요소1", "위험요소2"],
  "reasoning": "판단 근거 상세 설명",
  "confidence": 0.0~1.0,
  "needs_human_review": true/false
}
"""


class QualEngine:
    def __init__(self):
        self._llm = None
        self._prompt = None

    def _get_chain(self):
        """OpenAI API 키가 설정될 때까지 LLM 초기화를 지연"""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate

            self._llm = ChatOpenAI(model="gpt-4o", temperature=0)
            self._prompt = ChatPromptTemplate.from_messages([
                ("system", SHARIA_SYSTEM_PROMPT),
                ("human", """
다음 기업을 심사해주세요.

티커: {ticker}
섹터: {sector}
사업 요약: {business_summary}
주요 제품/서비스: {products}
""")
            ])

        return self._prompt | self._llm

    def screen(self, ticker: str, company_info: dict) -> QualResult:
        """
        company_info 구조:
        {
          "sector": str,
          "business_summary": str,
          "products": str  (없으면 "")
        }
        """
        # OpenAI API 키 없으면 UNCERTAIN 반환
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "").startswith("sk-your"):
            return QualResult(
                ticker=ticker,
                verdict="UNCERTAIN",
                sector_compliant=False,
                business_risks=["OPENAI_API_KEY 미설정 — 정성 심사 생략됨"],
                reasoning="OPENAI_API_KEY가 설정되지 않아 LLM 정성 심사를 수행할 수 없습니다. .env에 실제 키를 입력해주세요.",
                confidence=0.0,
                needs_human_review=True,
            )

        try:
            chain = self._get_chain()
            response = chain.invoke({
                "ticker": ticker,
                "sector": company_info.get("sector", "Unknown"),
                "business_summary": company_info.get("business_summary", ""),
                "products": company_info.get("products", ""),
            })

            result = json.loads(response.content)

        except json.JSONDecodeError:
            return QualResult(
                ticker=ticker,
                verdict="UNCERTAIN",
                sector_compliant=False,
                business_risks=["LLM 응답 파싱 실패"],
                reasoning=response.content if "response" in dir() else "응답 없음",
                confidence=0.0,
                needs_human_review=True,
            )
        except Exception as e:
            return QualResult(
                ticker=ticker,
                verdict="UNCERTAIN",
                sector_compliant=False,
                business_risks=[f"LLM 호출 오류: {str(e)}"],
                reasoning=f"오류 발생: {str(e)}",
                confidence=0.0,
                needs_human_review=True,
            )

        return QualResult(
            ticker=ticker,
            verdict=result["verdict"],
            sector_compliant=result["sector_compliant"],
            business_risks=result.get("business_risks", []),
            reasoning=result["reasoning"],
            confidence=result.get("confidence", 0.5),
            needs_human_review=result.get("needs_human_review", False),
        )
