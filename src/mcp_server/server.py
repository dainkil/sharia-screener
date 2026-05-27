"""
Sharia Screener MCP 서버 진입점
Claude Desktop / Claude Code / 외부 Agent가 여기에 연결
"""
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

load_dotenv()

# FastMCP 인스턴스 생성
mcp = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "sharia-screener"),
    instructions="주식의 이슬람 금융(샤리아) 준수 여부를 심사하는 도구 모음입니다. "
                 "screen_stock으로 개별 종목을 심사하고, screen_multiple_stocks로 여러 종목을 한 번에 심사할 수 있습니다.",
)

# 도구 등록
from src.mcp_server.tools.screen_tools import register_screen_tools
from src.mcp_server.tools.query_tools import register_query_tools
from src.mcp_server.tools.admin_tools import register_admin_tools

register_screen_tools(mcp)
register_query_tools(mcp)
register_admin_tools(mcp)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
