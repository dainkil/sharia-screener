"""
Sharia Screener — 전체 파이프라인 CLI 실행
MCP 서버를 사용하지 않고 직접 터미널에서 테스트할 때 사용
"""
from dotenv import load_dotenv
load_dotenv()

from src.pipeline.screener import ShariaScreener


# ── 심사 대상 종목 (섹터별 20개) ──────────────────────────────
TICKERS = [
    # 기술
    "AAPL",   # 애플
    "MSFT",   # 마이크로소프트
    "GOOGL",  # 구글
    "NVDA",   # 엔비디아
    "META",   # 메타
    # 전기차 / 이동수단
    "TSLA",   # 테슬라
    # 이커머스 / 클라우드
    "AMZN",   # 아마존
    # 금융 (이자 기반 — 대부분 FAIL 예상)
    "JPM",    # JP모건
    "BAC",    # 뱅크오브아메리카
    "V",      # 비자
    # 헬스케어
    "JNJ",    # 존슨앤존슨
    "PFE",    # 화이자
    "UNH",    # 유나이티드헬스
    # 소비재
    "MCD",    # 맥도날드 (돼지고기, 주류 판매)
    "COST",   # 코스트코
    "WMT",    # 월마트
    # 에너지
    "XOM",    # 엑슨모빌
    # 반도체
    "TSM",    # TSMC
    # 방산
    "LMT",    # 록히드마틴 (방산 — FAIL 예상)
    # 담배
    "MO",     # 알트리아 (담배 — FAIL 확실)
]


def main():
    screener = ShariaScreener()

    print("=" * 70)
    print("  Sharia Screener — 샤리아 주식 심사 파이프라인")
    print(f"  총 {len(TICKERS)}개 종목 심사")
    print("=" * 70)

    results = []
    for i, ticker in enumerate(TICKERS, 1):
        print(f"\n[{i}/{len(TICKERS)}] {ticker} 심사 중...")
        result = screener.screen(ticker)
        results.append(result)
        print(result.to_mcp_response())

    # ── 최종 요약 ──────────────────────────────────────────────
    compliant     = [r.ticker for r in results if r.final_verdict == "COMPLIANT"]
    non_compliant = [r.ticker for r in results if r.final_verdict == "NON_COMPLIANT"]
    questionable  = [r.ticker for r in results if r.final_verdict == "QUESTIONABLE"]
    errors        = [r.ticker for r in results if r.final_verdict == "ERROR"]

    print("\n" + "=" * 70)
    print("  최종 심사 요약")
    print("=" * 70)
    print(f"✅ COMPLIANT     ({len(compliant):2d}개): {', '.join(compliant) or '없음'}")
    print(f"❌ NON_COMPLIANT ({len(non_compliant):2d}개): {', '.join(non_compliant) or '없음'}")
    print(f"⚠️  QUESTIONABLE  ({len(questionable):2d}개): {', '.join(questionable) or '없음'}")
    if errors:
        print(f"🚫 ERROR         ({len(errors):2d}개): {', '.join(errors)}")
    print("=" * 70)
    print(f"\n✅ 파이프라인 실행 완료 ({len(results)}/{len(TICKERS)}개 성공)")


if __name__ == "__main__":
    main()
