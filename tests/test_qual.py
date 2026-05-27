"""
정성 심사 엔진 테스트 (OpenAI API 없이 stub 동작 확인)
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# API 키 없는 환경에서 테스트
os.environ.pop("OPENAI_API_KEY", None)

from src.processing.qual_engine import QualEngine, QualResult


@pytest.fixture
def engine():
    return QualEngine()


def test_no_api_key_returns_uncertain(engine):
    """API 키 없을 때 UNCERTAIN 반환 확인"""
    result = engine.screen("AAPL", {
        "sector": "Technology",
        "business_summary": "Apple Inc. designs and manufactures consumer electronics.",
        "products": "Apple Inc.",
    })
    assert result.verdict == "UNCERTAIN"
    assert result.needs_human_review is True
    assert isinstance(result.business_risks, list)
    assert len(result.business_risks) > 0


def test_result_structure(engine):
    """QualResult 구조 검증"""
    result = engine.screen("TEST", {
        "sector": "Finance",
        "business_summary": "A test bank that provides interest-based loans.",
        "products": "Test Bank",
    })
    assert hasattr(result, "ticker")
    assert hasattr(result, "verdict")
    assert hasattr(result, "sector_compliant")
    assert hasattr(result, "business_risks")
    assert hasattr(result, "reasoning")
    assert hasattr(result, "confidence")
    assert hasattr(result, "needs_human_review")
    assert result.ticker == "TEST"
    assert result.verdict in ("PASS", "FAIL", "UNCERTAIN")
    assert 0.0 <= result.confidence <= 1.0
