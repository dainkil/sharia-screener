"""
정량 심사 엔진 테스트
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.processing.quant_engine import QuantEngine, QuantResult


@pytest.fixture
def engine():
    return QuantEngine()


def test_pass_case(engine):
    """모든 기준 통과 케이스"""
    data = {
        "total_debt": 10_000_000,
        "market_cap": 100_000_000,
        "interest_income": 500_000,
        "total_revenue": 50_000_000,
        "non_halal_revenue": None,
    }
    result = engine.screen("TEST", data)
    assert result.verdict == "PASS"
    assert result.debt_ratio == pytest.approx(0.1)
    assert result.interest_income_ratio == pytest.approx(0.01)
    assert result.failed_criteria == []


def test_fail_debt(engine):
    """부채비율 초과 FAIL"""
    data = {
        "total_debt": 40_000_000,   # 40%
        "market_cap": 100_000_000,
        "interest_income": 0,
        "total_revenue": 50_000_000,
        "non_halal_revenue": None,
    }
    result = engine.screen("TEST", data)
    assert result.verdict == "FAIL"
    assert any("debt_ratio" in c for c in result.failed_criteria)


def test_fail_interest(engine):
    """이자수익 비율 초과 FAIL"""
    data = {
        "total_debt": 10_000_000,
        "market_cap": 100_000_000,
        "interest_income": 5_000_000,  # 10%
        "total_revenue": 50_000_000,
        "non_halal_revenue": None,
    }
    result = engine.screen("TEST", data)
    assert result.verdict == "FAIL"
    assert any("interest_income" in c for c in result.failed_criteria)


def test_uncertain_borderline(engine):
    """경계값 근접 UNCERTAIN"""
    data = {
        "total_debt": 31_500_000,   # 31.5% — 33% 기준 ±2% 이내
        "market_cap": 100_000_000,
        "interest_income": 0,
        "total_revenue": 50_000_000,
        "non_halal_revenue": None,
    }
    result = engine.screen("TEST", data)
    assert result.verdict == "UNCERTAIN"
    assert result.borderline_criteria != []


def test_non_halal_revenue_fail(engine):
    """비할랄 수익 초과 FAIL"""
    data = {
        "total_debt": 0,
        "market_cap": 100_000_000,
        "interest_income": 0,
        "total_revenue": 50_000_000,
        "non_halal_revenue": 5_000_000,  # 10%
    }
    result = engine.screen("TEST", data)
    assert result.verdict == "FAIL"


def test_zero_division_safe(engine):
    """0 나누기 안전 처리"""
    data = {
        "total_debt": 0,
        "market_cap": 0,
        "interest_income": 0,
        "total_revenue": 0,
        "non_halal_revenue": None,
    }
    result = engine.screen("TEST", data)
    assert result.verdict in ("PASS", "FAIL", "UNCERTAIN")
    assert result.debt_ratio == 0.0
