"""
Sharia Screener — 전체 파이프라인 CLI 실행
MCP 서버를 사용하지 않고 직접 터미널에서 테스트할 때 사용
"""
from dotenv import load_dotenv
load_dotenv()

from src.pipeline.screener import ShariaScreener


def main():
    screener = ShariaScreener()

    print("=" * 60)
    print("  Sharia Screener — 샤리아 주식 심사 파이프라인")
    print("=" * 60)

    # 샘플 종목 심사 (data/ 폴더의 캐시된 JSON 활용)
    test_tickers = ["AAPL", "MSFT", "TSLA"]

    for ticker in test_tickers:
        print(f"\n{'=' * 60}")
        result = screener.screen(ticker)
        print(result.to_mcp_response())

    print("\n✅ 파이프라인 실행 완료")


if __name__ == "__main__":
    main()
