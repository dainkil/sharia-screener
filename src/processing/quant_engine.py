"""
정량 심사 엔진 — 수치 기반 AAOIFI/DJIM 기준 체크
"""
from dataclasses import dataclass
from typing import Literal
import os


@dataclass
class QuantResult:
    ticker: str
    verdict: Literal["PASS", "FAIL", "UNCERTAIN"]
    debt_ratio: float              # 부채 / 시가총액
    interest_income_ratio: float   # 이자수익 / 총매출
    non_halal_revenue_ratio: float
    failed_criteria: list[str]     # 실패한 기준 목록
    borderline_criteria: list[str] # 경계값 근접 목록 (±2% 이내)
    raw_values: dict


class QuantEngine:
    def __init__(self):
        self.debt_limit = float(os.getenv("DEBT_RATIO_LIMIT", 0.33))
        self.interest_limit = float(os.getenv("INTEREST_INCOME_LIMIT", 0.05))
        self.non_halal_limit = float(os.getenv("NON_HALAL_REVENUE_LIMIT", 0.05))
        self.borderline_margin = 0.02  # 기준치 ±2% 이내면 UNCERTAIN

    def screen(self, ticker: str, financial_data: dict) -> QuantResult:
        """
        financial_data 구조:
        {
          "total_debt": float,
          "market_cap": float,
          "interest_income": float,
          "total_revenue": float,
          "non_halal_revenue": float  # 수집 가능하면, 없으면 None
        }
        """
        failed = []
        borderline = []

        # 1. 부채비율
        debt_ratio = self._safe_divide(
            financial_data.get("total_debt", 0),
            financial_data.get("market_cap", 1)
        )
        if debt_ratio > self.debt_limit:
            failed.append(f"debt_ratio {debt_ratio:.1%} > 기준 {self.debt_limit:.0%}")
        elif debt_ratio > self.debt_limit - self.borderline_margin:
            borderline.append(f"debt_ratio {debt_ratio:.1%} (기준 {self.debt_limit:.0%} 근접)")

        # 2. 이자수익 비율
        interest_ratio = self._safe_divide(
            financial_data.get("interest_income", 0),
            financial_data.get("total_revenue", 1)
        )
        if interest_ratio > self.interest_limit:
            failed.append(f"interest_income_ratio {interest_ratio:.1%} > 기준 {self.interest_limit:.0%}")
        elif interest_ratio > self.interest_limit - self.borderline_margin:
            borderline.append(f"interest_income_ratio {interest_ratio:.1%} (기준 근접)")

        # 3. 비할랄 수익 비율 (데이터 있을 때만)
        non_halal = financial_data.get("non_halal_revenue")
        non_halal_ratio = 0.0
        if non_halal is not None:
            non_halal_ratio = self._safe_divide(non_halal, financial_data.get("total_revenue", 1))
            if non_halal_ratio > self.non_halal_limit:
                failed.append(f"non_halal_revenue_ratio {non_halal_ratio:.1%} > 기준 {self.non_halal_limit:.0%}")

        # 판정
        if failed:
            verdict = "FAIL"
        elif borderline:
            verdict = "UNCERTAIN"
        else:
            verdict = "PASS"

        return QuantResult(
            ticker=ticker,
            verdict=verdict,
            debt_ratio=debt_ratio,
            interest_income_ratio=interest_ratio,
            non_halal_revenue_ratio=non_halal_ratio,
            failed_criteria=failed,
            borderline_criteria=borderline,
            raw_values=financial_data,
        )

    def _safe_divide(self, a: float, b: float) -> float:
        try:
            a = float(a) if a is not None else 0.0
            b = float(b) if b is not None else 0.0
            return a / b if b and b != 0 else 0.0
        except (TypeError, ValueError):
            return 0.0
