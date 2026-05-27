# Sharia Screener — 이슬람 금융(샤리아) 주식 심사 AI 파이프라인

> AAOIFI 기준 기반 정량·정성 복합 심사 + MCP 서버 통합 시스템

---

## 개요

이슬람 금융(샤리아) 원칙에 따라 주식 투자 가능 여부를 **자동으로 심사**하는 AI 파이프라인입니다.  
수치 기반 정량 심사(Quant)와 대형언어모델(LLM) 기반 정성 심사(Qual)를 결합하여,  
AAOIFI(이슬람금융기관회계감사기구) 국제 기준에 부합하는 샤리아 준수 여부를 판별합니다.

**MCP(Model Context Protocol) 서버**로 구현되어, Claude Desktop / Claude Code 등  
AI 에이전트가 직접 도구(Tool)로 호출할 수 있습니다.

---

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **정량 심사** | 부채비율, 이자수익 비율, 비할랄 수익 비율 자동 계산 |
| **정성 심사** | Google Gemini 2.5 Flash LLM으로 사업 모델 분석 |
| **복합 판정** | COMPLIANT / NON_COMPLIANT / QUESTIONABLE / ERROR |
| **MCP 서버** | Claude Desktop·Code에서 Tool로 직접 호출 가능 |
| **DB 캐시** | PostgreSQL 7일 캐시로 중복 API 호출 방지 |
| **벡터 검색** | ChromaDB로 심사 근거 유사 사례 검색 |

---

## 샤리아 심사 기준 (AAOIFI)

```
부채 / 시가총액    < 33%   (초과 시 FAIL)
이자수익 / 매출    < 5%    (초과 시 FAIL)
비할랄수익 / 매출  < 5%    (초과 시 FAIL)
```

**금지 업종 (하람):** 주류·담배, 도박·카지노, 포르노그래피, 무기·방산, 이자 기반 금융, 돼지고기

---

## 아키텍처

```
yfinance (실시간 주가·재무)
        │
        ▼
┌─────────────────────────────────────────┐
│           ShariaScreener Pipeline        │
│                                         │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  QuantEngine │  │   QualEngine     │ │
│  │  (수치 심사)  │  │ (Gemini LLM 심사) │ │
│  └──────┬───────┘  └────────┬─────────┘ │
│         └────────┬──────────┘           │
│              ┌───▼────┐                 │
│              │ Judge  │                 │
│              └───┬────┘                 │
└──────────────────┼──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   PostgreSQL              ChromaDB
   (결과 저장·캐시)        (근거 벡터 검색)
        │
        ▼
   FastMCP Server
   (Claude Desktop / Code에 Tool 노출)
```

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.11+ |
| 패키지 관리 | uv |
| 데이터 수집 | yfinance |
| LLM | Google Gemini 2.5 Flash (무료 티어) |
| LLM 프레임워크 | LangChain + langchain-google-genai |
| 벡터 DB | ChromaDB (PersistentClient) |
| 관계형 DB | PostgreSQL 14 + SQLAlchemy |
| MCP 서버 | FastMCP 2.0 |
| AI 에이전트 연동 | MCP (Model Context Protocol) |

---

## 설치 및 실행

### 1. 사전 요구사항

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 패키지 매니저
- PostgreSQL 14+
- Google AI Studio API 키 ([무료 발급](https://aistudio.google.com/app/apikey))

### 2. 설치

```bash
git clone https://github.com/dainkil/sharia-screener.git
cd sharia-screener
uv sync
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 열어서 키 입력
```

```env
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/sharia_db
DEBT_RATIO_LIMIT=0.33
INTEREST_INCOME_LIMIT=0.05
NON_HALAL_REVENUE_LIMIT=0.05
PURIFICATION_LIMIT=0.05
```

### 4. DB 초기화

```bash
uv run python -c "from src.storage.db_handler import DBHandler; DBHandler().init_tables()"
```

### 5. CLI 실행 (20개 종목 심사)

```bash
uv run python main.py
```

### 6. MCP 서버 실행

```bash
uv run sharia-mcp
```

---

## Claude Desktop 연동

`~/Library/Application Support/Claude/claude_desktop_config.json` 에 아래 항목 추가:

```json
{
  "mcpServers": {
    "sharia-screener": {
      "command": "uv",
      "args": ["--directory", "/path/to/sharia-screener", "run", "sharia-mcp"],
      "env": {
        "GOOGLE_API_KEY": "your_google_api_key_here"
      }
    }
  }
}
```

Claude Desktop 재시작 후 대화에서 바로 사용 가능:

> "AAPL이 샤리아 기준에 맞는지 심사해줘"  
> "할랄 IT 주식 목록 알려줘"  
> "테슬라가 왜 NON_COMPLIANT인지 설명해줘"

---

## MCP 도구 목록

| 도구명 | 설명 |
|--------|------|
| `screen_stock` | 단일 종목 샤리아 심사 |
| `screen_multiple_stocks` | 복수 종목 일괄 심사 (최대 20개) |
| `compare_stocks_halal` | 종목 간 할랄 기준 비교 |
| `get_screening_result` | 기존 심사 결과 조회 |
| `list_compliant_stocks` | 준수 종목 목록 조회 (섹터 필터 가능) |
| `explain_screening_decision` | 심사 판단 근거 상세 설명 |
| `get_screening_standards` | 현재 적용 기준 조회 |
| `get_server_status` | 서버 상태 확인 |
| `update_screening_standard` | 심사 기준값 변경 |

---

## 20개 종목 심사 결과 (2025년 5월 기준)

| 판정 | 종목 수 | 종목 |
|------|---------|------|
| ✅ COMPLIANT | 4 | MSFT, NVDA, JNJ, XOM |
| ❌ NON_COMPLIANT | 15 | AAPL, GOOGL, TSLA, AMZN, JPM, BAC, V, PFE, UNH, MCD, COST, WMT, TSM, LMT, MO |
| ⚠️ QUESTIONABLE | 1 | META |

> **참고:** 심사 결과는 수집 시점 재무 데이터에 따라 달라질 수 있으며,  
> 실제 투자 판단에는 공인 샤리아 위원회 검토가 필요합니다.

---

## 프로젝트 구조

```
sharia-screener/
├── main.py                        # CLI 실행 진입점
├── pyproject.toml                 # uv 프로젝트 설정
├── .env.example                   # 환경 변수 예시
├── src/
│   ├── pipeline/
│   │   └── screener.py            # 메인 파이프라인 오케스트레이터
│   ├── processing/
│   │   ├── quant_engine.py        # 정량 심사 (AAOIFI 수치 기준)
│   │   └── qual_engine.py         # 정성 심사 (Gemini LLM)
│   ├── collection/
│   │   └── data_collector.py      # yfinance 데이터 수집
│   ├── storage/
│   │   ├── db_handler.py          # PostgreSQL 저장·캐시
│   │   └── vector_handler.py      # ChromaDB 벡터 검색
│   └── mcp_server/
│       ├── server.py              # FastMCP 서버
│       └── tools/
│           ├── screen_tools.py    # 심사 도구
│           ├── query_tools.py     # 조회 도구
│           └── admin_tools.py     # 관리 도구
├── tests/
│   ├── test_quant_engine.py
│   ├── test_qual_engine.py
│   └── test_mcp_tools.py
└── data/                          # 수집 데이터 캐시 (gitignore)
```

---

## 테스트

```bash
uv run pytest tests/ -v
```

---

## 라이선스

MIT License

---

## 참고 문헌

- AAOIFI Sharia Standards No. 21 — Financial Paper (Shares)
- [Dow Jones Islamic Market Index Methodology](https://www.spglobal.com/spdji/en/documents/methodologies/methodology-dj-islamic-market-indexes.pdf)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
