"""
PostgreSQL 데이터베이스 핸들러
테이블 초기화, 심사 결과 저장/조회
"""
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sharia_user:sharia_pass@localhost:5432/sharia_db")


class DBHandler:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self._ensure_tables()

    def _ensure_tables(self):
        """앱 시작 시 테이블이 없으면 자동 생성"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS companies (
                ticker VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255),
                sector VARCHAR(100),
                industry VARCHAR(100),
                summary TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS financial_data (
                ticker VARCHAR(20) REFERENCES companies(ticker),
                fiscal_date DATE,
                market_cap NUMERIC(20, 4),
                total_debt NUMERIC(20, 4),
                interest_income NUMERIC(20, 4),
                non_halal_revenue NUMERIC(20, 4),
                revenue NUMERIC(20, 4),
                currency VARCHAR(10),
                PRIMARY KEY (ticker, fiscal_date)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS screening_results (
                res_id SERIAL PRIMARY KEY,
                ticker VARCHAR(20),
                final_verdict VARCHAR(30),
                confidence_score NUMERIC(5, 4),
                quant_summary JSONB,
                qual_summary JSONB,
                evidence_text TEXT,
                needs_human_review BOOLEAN,
                screening_standard VARCHAR(20) DEFAULT 'AAOIFI',
                screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
        ]

        with self.engine.connect() as conn:
            for query in queries:
                conn.execute(text(query))
            conn.commit()

    def save_screening_result(self, result) -> int:
        """ScreeningResult 객체를 DB에 저장하고 res_id를 반환"""
        with self.engine.connect() as conn:
            row = conn.execute(
                text("""
                    INSERT INTO screening_results
                        (ticker, final_verdict, confidence_score, quant_summary,
                         qual_summary, evidence_text, needs_human_review, screening_standard)
                    VALUES
                        (:ticker, :final_verdict, :confidence_score, :quant_summary::jsonb,
                         :qual_summary::jsonb, :evidence_text, :needs_human_review, :screening_standard)
                    RETURNING res_id
                """),
                {
                    "ticker": result.ticker,
                    "final_verdict": result.final_verdict,
                    "confidence_score": result.confidence_score,
                    "quant_summary": json.dumps(result.quant_summary, ensure_ascii=False),
                    "qual_summary": json.dumps(result.qual_summary, ensure_ascii=False),
                    "evidence_text": result.evidence_text,
                    "needs_human_review": result.needs_human_review,
                    "screening_standard": result.screening_standard,
                }
            )
            conn.commit()
            return row.fetchone()[0]

    def get_latest_result(self, ticker: str) -> dict | None:
        """특정 ticker의 가장 최근 심사 결과를 반환"""
        with self.engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT
                        ticker, final_verdict, confidence_score,
                        quant_summary, qual_summary, evidence_text,
                        needs_human_review, screening_standard, screened_at,
                        EXTRACT(DAY FROM NOW() - screened_at)::int AS age_days
                    FROM screening_results
                    WHERE ticker = :ticker
                    ORDER BY screened_at DESC
                    LIMIT 1
                """),
                {"ticker": ticker}
            ).fetchone()

        if not row:
            return None

        return {
            "age_days": row.age_days,
            "screened_at": str(row.screened_at),
            "result": {
                "ticker": row.ticker,
                "final_verdict": row.final_verdict,
                "confidence_score": float(row.confidence_score),
                "quant_summary": row.quant_summary,
                "qual_summary": row.qual_summary,
                "evidence_text": row.evidence_text,
                "needs_human_review": row.needs_human_review,
                "screening_standard": row.screening_standard,
            }
        }

    def list_compliant_stocks(self, sector: str = None, limit: int = 20) -> list[dict]:
        """COMPLIANT 판정 종목 목록 반환"""
        with self.engine.connect() as conn:
            if sector:
                rows = conn.execute(
                    text("""
                        SELECT DISTINCT ON (sr.ticker)
                            sr.ticker,
                            sr.confidence_score,
                            sr.screened_at,
                            (sr.qual_summary->>'sector') AS sector
                        FROM screening_results sr
                        WHERE sr.final_verdict = 'COMPLIANT'
                          AND sr.qual_summary->>'sector' ILIKE :sector
                        ORDER BY sr.ticker, sr.screened_at DESC
                        LIMIT :limit
                    """),
                    {"sector": f"%{sector}%", "limit": limit}
                ).fetchall()
            else:
                rows = conn.execute(
                    text("""
                        SELECT DISTINCT ON (ticker)
                            ticker, confidence_score, screened_at,
                            (qual_summary->>'sector') AS sector
                        FROM screening_results
                        WHERE final_verdict = 'COMPLIANT'
                        ORDER BY ticker, screened_at DESC
                        LIMIT :limit
                    """),
                    {"limit": limit}
                ).fetchall()

        return [
            {
                "ticker": r.ticker,
                "confidence": float(r.confidence_score),
                "screened_at": str(r.screened_at)[:10],
                "sector": r.sector or "-",
            }
            for r in rows
        ]


def init_db():
    """독립 실행용 DB 초기화 (테이블 강제 재생성)"""
    db = DBHandler()
    print("✅ 모든 테이블이 성공적으로 생성되었습니다!")


if __name__ == "__main__":
    init_db()
