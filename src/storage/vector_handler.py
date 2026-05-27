"""
ChromaDB 벡터 스토어 핸들러
LLM 정성 심사 근거 텍스트를 임베딩하여 저장 및 유사도 검색
"""
import chromadb
from chromadb.config import Settings
import os


CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma_db")


class VectorHandler:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="sharia_evidence",
            metadata={"hnsw:space": "cosine"}
        )

    def save_evidence(self, ticker: str, evidence_text: str, metadata: dict = None) -> str:
        """
        심사 근거 텍스트를 벡터 스토어에 저장합니다.

        Args:
            ticker: 종목 티커
            evidence_text: 저장할 근거 텍스트
            metadata: 추가 메타데이터 (예: verdict, screened_at)

        Returns:
            저장된 벡터 ID
        """
        from datetime import datetime
        vector_id = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        meta = {"ticker": ticker, "screened_at": datetime.now().isoformat()}
        if metadata:
            meta.update(metadata)

        self.collection.add(
            documents=[evidence_text],
            metadatas=[meta],
            ids=[vector_id]
        )

        return vector_id

    def search_similar(self, query: str, n_results: int = 5, ticker_filter: str = None) -> list[dict]:
        """
        유사한 심사 근거를 검색합니다 (RAG 활용).

        Args:
            query: 검색 쿼리 텍스트
            n_results: 반환할 최대 결과 수
            ticker_filter: 특정 티커로 필터링 (None이면 전체)

        Returns:
            유사 근거 목록 [{"text": ..., "ticker": ..., "distance": ...}]
        """
        where = {"ticker": ticker_filter} if ticker_filter else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        output = []
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            output.append({
                "text": doc,
                "ticker": meta.get("ticker"),
                "screened_at": meta.get("screened_at"),
                "distance": dist,
            })

        return output

    def get_ticker_evidences(self, ticker: str) -> list[dict]:
        """특정 티커의 모든 저장된 근거를 반환합니다."""
        results = self.collection.get(
            where={"ticker": ticker},
            include=["documents", "metadatas"],
        )

        return [
            {"text": doc, "meta": meta}
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]
