"""
관리 도구들
심사 기준 조회/변경, 시스템 상태 확인
"""
from mcp.server.fastmcp import FastMCP
import os


def register_admin_tools(mcp: FastMCP):

    @mcp.tool()
    def get_screening_standards() -> str:
        """
        현재 적용 중인 샤리아 심사 기준값을 반환합니다.

        Returns:
            AAOIFI 기준값 및 현재 설정값
        """
        return (
            "## 현재 샤리아 심사 기준 (AAOIFI)\n\n"
            "| 지표 | 기준값 | 현재 설정 |\n"
            "|------|--------|----------|\n"
            f"| 부채/시가총액 | 33% 이하 | {float(os.getenv('DEBT_RATIO_LIMIT', 0.33)):.0%} |\n"
            f"| 이자수익/매출 | 5% 이하 | {float(os.getenv('INTEREST_INCOME_LIMIT', 0.05)):.0%} |\n"
            f"| 비할랄 수익/매출 | 5% 이하 | {float(os.getenv('NON_HALAL_REVENUE_LIMIT', 0.05)):.0%} |\n\n"
            "기준 변경은 .env 파일에서 수정하거나 update_screening_standard 도구를 사용하세요."
        )

    @mcp.tool()
    def get_server_status() -> str:
        """
        MCP 서버 및 연결된 서비스 상태를 확인합니다.

        Returns:
            DB 연결, API 키 설정 여부, 심사 가능 상태
        """
        status = {"PostgreSQL DB": False, "OpenAI API Key": False, "ChromaDB": False}

        try:
            from src.storage.db_handler import DBHandler
            db = DBHandler()
            db.get_latest_result("TEST")
            status["PostgreSQL DB"] = True
        except Exception:
            pass

        api_key = os.getenv("OPENAI_API_KEY", "")
        status["OpenAI API Key"] = bool(api_key) and not api_key.startswith("sk-your")
        status["ChromaDB"] = True  # 로컬 PersistentClient는 항상 가용

        lines = ["## 🔧 Sharia Screener 서버 상태", ""]
        for service, ok in status.items():
            lines.append(f"- {service}: {'✅ 정상' if ok else '❌ 오류/미설정'}")

        all_ok = all(status.values())
        lines += ["", f"**전체 상태**: {'✅ 심사 가능' if all_ok else '⚠️ 일부 서비스 점검 필요'}"]

        if not status["OpenAI API Key"]:
            lines += [
                "",
                "> ℹ️ OpenAI API Key가 없으면 정성 심사(qual_engine)는 UNCERTAIN으로 처리됩니다.",
                "> .env 파일의 OPENAI_API_KEY를 설정하면 GPT-4o 정성 심사가 활성화됩니다.",
            ]

        return "\n".join(lines)

    @mcp.tool()
    def update_screening_standard(
        debt_ratio_limit: float = None,
        interest_income_limit: float = None,
        non_halal_revenue_limit: float = None,
    ) -> str:
        """
        샤리아 심사 기준값을 런타임에서 임시 변경합니다.
        (영구 변경은 .env 파일 수정 필요)

        Args:
            debt_ratio_limit: 부채/시가총액 한도 (예: 0.33 = 33%)
            interest_income_limit: 이자수익/매출 한도 (예: 0.05 = 5%)
            non_halal_revenue_limit: 비할랄수익/매출 한도 (예: 0.05 = 5%)

        Returns:
            변경된 기준값 요약
        """
        changed = []

        if debt_ratio_limit is not None:
            os.environ["DEBT_RATIO_LIMIT"] = str(debt_ratio_limit)
            changed.append(f"부채/시가총액 한도 → {debt_ratio_limit:.0%}")

        if interest_income_limit is not None:
            os.environ["INTEREST_INCOME_LIMIT"] = str(interest_income_limit)
            changed.append(f"이자수익/매출 한도 → {interest_income_limit:.0%}")

        if non_halal_revenue_limit is not None:
            os.environ["NON_HALAL_REVENUE_LIMIT"] = str(non_halal_revenue_limit)
            changed.append(f"비할랄수익/매출 한도 → {non_halal_revenue_limit:.0%}")

        if not changed:
            return "변경된 기준값이 없습니다. 파라미터를 지정해주세요."

        return (
            "## ✅ 심사 기준 임시 변경 완료\n\n"
            + "\n".join(f"- {c}" for c in changed)
            + "\n\n> ⚠️ 이 변경은 서버 재시작 시 초기화됩니다. 영구 변경은 .env 파일을 수정하세요."
        )
