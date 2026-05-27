"""
심사 실행 도구들
Claude가 "AAPL 샤리아 심사해줘"라고 하면 이 도구들이 호출됨
"""
from mcp.server.fastmcp import FastMCP
from src.pipeline.screener import ShariaScreener

_screener = None


def get_screener() -> ShariaScreener:
    global _screener
    if _screener is None:
        _screener = ShariaScreener()
    return _screener


def register_screen_tools(mcp: FastMCP):

    @mcp.tool()
    def screen_stock(ticker: str) -> str:
        """
        단일 주식의 샤리아(이슬람 금융) 준수 여부를 심사합니다.

        Args:
            ticker: 주식 티커 (예: AAPL, MSFT, TSLA, 005930.KS)

        Returns:
            심사 결과 (COMPLIANT/NON_COMPLIANT/QUESTIONABLE),
            수치 근거, 업종 판단, 전문가 검토 필요 여부 포함
        """
        result = get_screener().screen(ticker)
        return result.to_mcp_response()

    @mcp.tool()
    def screen_multiple_stocks(tickers: list[str]) -> str:
        """
        여러 주식을 한 번에 샤리아 심사합니다.

        Args:
            tickers: 티커 목록 (예: ["AAPL", "MSFT", "TSLA"])
                     최대 20개 권장

        Returns:
            각 종목의 심사 결과 요약 및 COMPLIANT 종목 목록
        """
        if len(tickers) > 20:
            return "❌ 한 번에 최대 20개 종목만 심사 가능합니다."

        results = get_screener().screen_batch(tickers)

        compliant = [r.ticker for r in results if r.final_verdict == "COMPLIANT"]
        non_compliant = [r.ticker for r in results if r.final_verdict == "NON_COMPLIANT"]
        questionable = [r.ticker for r in results if r.final_verdict == "QUESTIONABLE"]
        errors = [r.ticker for r in results if r.final_verdict == "ERROR"]

        lines = [
            f"## 배치 심사 결과 ({len(tickers)}개 종목)",
            "",
            f"✅ **COMPLIANT** ({len(compliant)}개): {', '.join(compliant) or '없음'}",
            f"❌ **NON_COMPLIANT** ({len(non_compliant)}개): {', '.join(non_compliant) or '없음'}",
            f"⚠️ **QUESTIONABLE** ({len(questionable)}개): {', '.join(questionable) or '없음'}",
        ]

        if errors:
            lines.append(f"🚫 **오류** ({len(errors)}개): {', '.join(errors)}")

        lines += ["", "---", "### 상세 결과"]
        for r in results:
            lines.append(f"\n{r.to_mcp_response()}")

        return "\n".join(lines)

    @mcp.tool()
    def compare_stocks_halal(tickers: list[str], criteria: str = "AAOIFI") -> str:
        """
        여러 주식의 샤리아 준수 여부를 비교 분석합니다.
        투자 포트폴리오 구성 시 활용합니다.

        Args:
            tickers: 비교할 티커 목록
            criteria: 적용 기준 (AAOIFI | DJIM | SP_SHARIA), 기본값 AAOIFI

        Returns:
            비교 표 형식의 심사 결과 및 추천 종목
        """
        results = get_screener().screen_batch(tickers)

        lines = [
            f"## 샤리아 준수 여부 비교 ({criteria} 기준)",
            "",
            "| 티커 | 판정 | 부채비율 | 이자수익비율 | 업종적합 | 신뢰도 |",
            "|------|------|---------|------------|---------|--------|",
        ]

        for r in results:
            verdict_icon = {
                "COMPLIANT": "✅",
                "NON_COMPLIANT": "❌",
                "QUESTIONABLE": "⚠️",
            }.get(r.final_verdict, "🚫")
            lines.append(
                f"| {r.ticker} "
                f"| {verdict_icon} {r.final_verdict} "
                f"| {r.quant_summary.get('debt_ratio', 0):.1%} "
                f"| {r.quant_summary.get('interest_income_ratio', 0):.1%} "
                f"| {'✅' if r.qual_summary.get('sector_compliant') else '❌'} "
                f"| {r.confidence_score:.0%} |"
            )

        compliant = [r.ticker for r in results if r.final_verdict == "COMPLIANT"]
        if compliant:
            lines += ["", f"**추천 가능 종목**: {', '.join(compliant)}"]

        return "\n".join(lines)
