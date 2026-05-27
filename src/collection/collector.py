import yfinance as yf
import json
import os
import pandas as pd

class DataCollector:
    """
    yfinance API를 활용하여 기업의 재무 및 개요 데이터를 수집하고
    원시 데이터(Raw Data) 형태로 버퍼(data/ 폴더)에 저장하는 클래스입니다.
    """
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_and_save(self, ticker_symbol: str) -> bool:
        """
        특정 Ticker의 데이터를 수집하여 JSON 파일로 저장합니다.

        Args:
            ticker_symbol (str): 종목 티커 (예: 'AAPL')

        Returns:
            bool: 성공 여부
        """
        print(f"[{ticker_symbol}] 데이터 수집 시작...")

        try:
            ticker = yf.Ticker(ticker_symbol)
            info_data = ticker.info

            balance_sheet_df = ticker.balance_sheet
            bs_dict = {}

            if not balance_sheet_df.empty:
                for col_date, col_data in balance_sheet_df.items():
                    date_str = str(col_date.date())
                    bs_dict[date_str] = col_data.where(pd.notnull(col_data), None).to_dict()

            raw_data = {
                "ticker": ticker_symbol,
                "info": info_data,
                "balance_sheet": bs_dict
            }

            file_path = os.path.join(self.output_dir, f"{ticker_symbol}_raw.json")
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(raw_data, json_file, ensure_ascii=False, indent=4)

            print(f"[{ticker_symbol}] 데이터 저장 완료: {file_path}")
            return True

        except Exception as e:
            print(f"[{ticker_symbol}] 데이터 수집 실패: {e}")
            return False

    def collect(self, ticker_symbol: str) -> dict:
        """
        단일 Ticker 데이터를 수집하여 dict로 반환합니다 (파일 저장 없이).

        Args:
            ticker_symbol (str): 종목 티커

        Returns:
            dict: 수집된 원시 데이터
        """
        ticker = yf.Ticker(ticker_symbol)
        info_data = ticker.info

        balance_sheet_df = ticker.balance_sheet
        bs_dict = {}

        if not balance_sheet_df.empty:
            for col_date, col_data in balance_sheet_df.items():
                date_str = str(col_date.date())
                bs_dict[date_str] = col_data.where(pd.notnull(col_data), None).to_dict()

        return {
            "ticker": ticker_symbol,
            "info": info_data,
            "balance_sheet": bs_dict
        }

    def run_collection(self, ticker_list: list):
        """
        목록으로 전달받은 다수의 Ticker에 대해 일괄 수집을 진행합니다.
        """
        print(f"총 {len(ticker_list)}개 종목에 대한 데이터 수집 파이프라인을 가동합니다.")
        success_count = 0

        for t in ticker_list:
            if self.fetch_and_save(t):
                success_count += 1

        print(f"수집 파이프라인 종료 (성공: {success_count}/{len(ticker_list)})")


# 단독 실행 및 테스트용 코드
if __name__ == "__main__":
    collector = DataCollector(output_dir="../../data")
    sample_tickers = ["AAPL", "MSFT", "TSLA"]
    collector.run_collection(sample_tickers)
