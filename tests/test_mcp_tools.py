"""
MCP 도구 기본 동작 테스트
실제 DB/API 없이 도구 임포트 및 등록 확인
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP


def test_mcp_server_import():
    """MCP 서버 임포트 확인"""
    from src.mcp_server.server import mcp
    assert mcp is not None
    assert mcp.name == "sharia-screener"


def test_tools_registered():
    """도구 등록 확인"""
    from src.mcp_server.server import mcp
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "screen_stock" in tool_names
    assert "screen_multiple_stocks" in tool_names
    assert "compare_stocks_halal" in tool_names
    assert "get_screening_result" in tool_names
    assert "list_compliant_stocks" in tool_names
    assert "explain_screening_decision" in tool_names
    assert "get_screening_standards" in tool_names
    assert "get_server_status" in tool_names
    assert "update_screening_standard" in tool_names


def test_get_screening_standards():
    """기준값 조회 도구 동작"""
    os.environ["DEBT_RATIO_LIMIT"] = "0.33"
    os.environ["INTEREST_INCOME_LIMIT"] = "0.05"
    os.environ["NON_HALAL_REVENUE_LIMIT"] = "0.05"

    from src.mcp_server.tools.admin_tools import register_admin_tools
    # 직접 함수 호출 대신 등록 확인
    mcp = FastMCP(name="test")
    register_admin_tools(mcp)
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "get_screening_standards" in tool_names
