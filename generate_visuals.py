"""
학술제 포스터용 시각자료 3종 생성
  01 파이프라인 다이어그램
  02 20개 종목 히트맵
  03 MCP Tool 호출 시연
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

os.makedirs("assets", exist_ok=True)

import matplotlib.font_manager as fm
for c in ["/System/Library/Fonts/AppleSDGothicNeo.ttc",
          "/Library/Fonts/AppleGothic.ttf"]:
    if os.path.exists(c):
        fm.fontManager.addfont(c)
        plt.rcParams["font.family"] = fm.FontProperties(fname=c).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False


# ═══════════════════════════════════════════════════════════════════
# 공통 헬퍼
# ═══════════════════════════════════════════════════════════════════

# Color palette  (최소화)
_BG      = "#0D1117"
_BOX     = "#151C28"
_BLUE    = "#2563EB"   # data / storage / infra
_GREEN   = "#16A34A"   # pipeline / MCP
_PURPLE  = "#6D28D9"   # AI engine
_AMBER   = "#B45309"   # client
_GRAY    = "#374151"   # neutral border
_TXT     = "#E2E8F0"   # main text
_DIM     = "#6B7280"   # dim text
_ARR     = "#4B5563"   # arrow color


def make_ax(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def rbox(ax, cx, cy, w, h, line1, line2="", bc=_GRAY):
    """Rounded box centered at (cx, cy). line1 = bold label, line2 = dim sublabel."""
    x0, y0 = cx - w / 2, cy - h / 2
    p = FancyBboxPatch((x0, y0), w, h,
                       boxstyle="round,pad=0,rounding_size=0.15",
                       facecolor=_BOX, edgecolor=bc, linewidth=1.8, zorder=3)
    ax.add_patch(p)
    if line2:
        ax.text(cx, cy + h * 0.16, line1,
                ha="center", va="center", color=_TXT,
                fontsize=10, fontweight="bold", zorder=4)
        ax.text(cx, cy - h * 0.22, line2,
                ha="center", va="center", color=_DIM,
                fontsize=7.8, zorder=4)
    else:
        ax.text(cx, cy, line1,
                ha="center", va="center", color=_TXT,
                fontsize=10, fontweight="bold", zorder=4)


def arr(ax, x1, y1, x2, y2, c=_ARR):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=c,
                               lw=1.5, mutation_scale=13), zorder=2)


def seg(ax, x1, y1, x2, y2, c=_ARR):
    ax.plot([x1, x2], [y1, y2], color=c, lw=1.5, zorder=2, solid_capstyle="round")


def panel_box(ax, x, y, w, h, title, tc=_BLUE, title_h=0.45):
    """Panel with title bar on top."""
    # Main body
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0,rounding_size=0.15",
                       facecolor=_BOX, edgecolor=tc, linewidth=1.5, zorder=2)
    ax.add_patch(p)
    # Title bar
    tb = FancyBboxPatch((x + 0.03, y + h - title_h - 0.02),
                        w - 0.06, title_h,
                        boxstyle="round,pad=0,rounding_size=0.10",
                        facecolor=tc + "25", edgecolor="none", zorder=3)
    ax.add_patch(tb)
    ax.text(x + 0.22, y + h - title_h / 2 - 0.02, title,
            color=tc, fontsize=9.5, fontweight="bold", va="center", zorder=4)


# ═══════════════════════════════════════════════════════════════════
# 01. 파이프라인 다이어그램
# ═══════════════════════════════════════════════════════════════════

def draw_pipeline():
    W, H = 16, 9
    fig, ax = make_ax(W, H)

    # ── 레이아웃 상수 ───────────────────────────────────────────
    PCX = 4.0          # pipeline center x
    LX, RX = 2.15, 5.85  # left/right x for paired boxes
    W2  = 2.85         # paired box width  (LX±W2/2 = 0.725~3.575, 4.425~7.275)
    W1  = 5.20         # single box width  (PCX±W1/2 = 1.40~6.60)
    BH  = 0.72         # box height
    BHH = BH / 2

    # Y centers (top → bottom, 9 unit height)
    # Title area: 8.15 ~ 9
    YS = [7.60, 6.48, 5.28, 4.08, 2.88, 1.68]
    # Input, Collect, Engines, Judge, Storage, MCP

    # ── 제목 ────────────────────────────────────────────────────
    ax.text(PCX, 8.72, "Sharia Screener  —  전체 파이프라인",
            ha="center", color=_TXT, fontsize=14, fontweight="bold")
    ax.text(PCX, 8.30, "AAOIFI 기준  ·  정량 + 정성 복합 심사  ·  FastMCP 서버 연동",
            ha="center", color=_DIM, fontsize=9)

    # ── 박스 ─────────────────────────────────────────────────────
    rbox(ax, LX,  YS[0], W2, BH, "yfinance",      "실시간 주가·재무 수집",    _BLUE)
    rbox(ax, RX,  YS[0], W2, BH, "JSON Cache",    "7일 로컬 캐시",            _BLUE)
    rbox(ax, PCX, YS[1], W1, BH, "DataCollector", "재무 지표 정규화 (부채 / 매출 / 이자수익)", _GREEN)
    rbox(ax, LX,  YS[2], W2, BH, "QuantEngine",   "AAOIFI 수치 기준 비교",   _PURPLE)
    rbox(ax, RX,  YS[2], W2, BH, "QualEngine",    "Gemini 2.5 Flash LLM",    _PURPLE)
    rbox(ax, PCX, YS[3], W1, BH, "Judge",
         "COMPLIANT  ·  NON_COMPLIANT  ·  QUESTIONABLE", _AMBER)
    rbox(ax, LX,  YS[4], W2, BH, "PostgreSQL",    "결과 저장 · 7일 캐시",    _BLUE)
    rbox(ax, RX,  YS[4], W2, BH, "ChromaDB",      "근거 벡터 검색 (RAG)",    _BLUE)
    rbox(ax, PCX, YS[5], W1, BH, "FastMCP Server", "",                        _GREEN)

    # ── 화살표 ─────────────────────────────────────────────────
    # Input → Collect  (Y-merge: 두 박스 아래쪽 → 수평 바 → 세로 화살표)
    def ymrg(y_from, y_to):
        """Y-merge: two bottom points at (LX, y_from) and (RX, y_from) → single arrow to (PCX, y_to)"""
        my = (y_from + y_to) / 2
        seg(ax, LX, y_from, LX, my)
        seg(ax, RX, y_from, RX, my)
        seg(ax, LX, my,     RX, my)   # 수평 바
        arr(ax, PCX, my,    PCX, y_to)

    def yspl(y_from, y_to):
        """Y-split: single arrow down from (PCX, y_from) → fork → two top points at (LX, y_to) and (RX, y_to)"""
        my = (y_from + y_to) / 2
        seg(ax, PCX, y_from, PCX, my)
        arr(ax, PCX, my, LX, y_to)
        arr(ax, PCX, my, RX, y_to)

    ymrg(YS[0] - BHH, YS[1] + BHH)   # Input → Collect
    yspl(YS[1] - BHH, YS[2] + BHH)   # Collect → Engines
    ymrg(YS[2] - BHH, YS[3] + BHH)   # Engines → Judge
    yspl(YS[3] - BHH, YS[4] + BHH)   # Judge → Storage
    ymrg(YS[4] - BHH, YS[5] + BHH)   # Storage → MCP

    # ── 구분선 ──────────────────────────────────────────────────
    DVX = 8.1
    ax.plot([DVX, DVX], [0.45, 8.95], color="#2D3748", lw=1.0, ls="--")

    # ── 클라이언트 (오른쪽) ──────────────────────────────────────
    CX = 12.3
    CW = 7.3
    CY = [7.60, 6.20, 4.80]   # client box Y centers (same BH)

    rbox(ax, CX, CY[0], CW, BH, "Claude Desktop", "자연어 → Tool 자동 호출",      _AMBER)
    rbox(ax, CX, CY[1], CW, BH, "Claude Code",    "CLI 에이전트 연동",             _AMBER)
    rbox(ax, CX, CY[2], CW, BH, "외부 AI Agent",  "MCP 프로토콜 호환 클라이언트", _AMBER)

    # Tools 목록 박스
    TBX, TBY = DVX + 0.25, 0.45
    TBW, TBH_H = 7.3, 3.9
    p = FancyBboxPatch((TBX, TBY), TBW, TBH_H,
                       boxstyle="round,pad=0,rounding_size=0.12",
                       facecolor=_BOX, edgecolor=_GRAY, lw=1.2, zorder=2)
    ax.add_patch(p)
    ax.text(TBX + 0.2, TBY + TBH_H - 0.28, "MCP 도구 목록",
            color=_DIM, fontsize=8.5, fontweight="bold", va="center")
    tools = [
        "screen_stock(ticker)",
        "screen_multiple_stocks(tickers)",
        "list_compliant_stocks(sector)",
        "explain_screening_decision(ticker)",
        "get_screening_standards()",
        "get_server_status()",
    ]
    for i, t in enumerate(tools):
        ax.text(TBX + 0.2, TBY + TBH_H - 0.68 - i * 0.48, t,
                color="#86EFAC", fontsize=8.5, va="center", family="monospace")

    # FastMCP → 클라이언트 연결
    # FastMCP 오른쪽 끝 → 구분선 → 수직 바 → 각 클라이언트 좌측
    MCP_RX = PCX + W1 / 2
    MCP_Y  = YS[5]
    CL_LX  = CX - CW / 2

    arr(ax, MCP_RX, MCP_Y, DVX - 0.02, MCP_Y, c=_GREEN)   # 수평 화살표
    seg(ax, DVX, MCP_Y, DVX, CY[0], c=_GREEN)              # 수직 선

    for cy in CY:
        seg(ax, DVX, cy, DVX + 0.02, cy, c=_GREEN)
        arr(ax, DVX, cy, CL_LX, cy, c=_GREEN)

    # ── 범례 ──────────────────────────────────────────────────────
    patches = [
        mpatches.Patch(color=_BLUE,   label="데이터 · 저장소"),
        mpatches.Patch(color=_GREEN,  label="파이프라인 · MCP"),
        mpatches.Patch(color=_PURPLE, label="심사 엔진"),
        mpatches.Patch(color=_AMBER,  label="AI 클라이언트"),
    ]
    ax.legend(handles=patches, loc="lower left", bbox_to_anchor=(0.01, 0.01),
              ncol=4, fontsize=8, facecolor=_BOX, edgecolor=_GRAY,
              labelcolor=_TXT, framealpha=0.95)

    plt.savefig("assets/01_pipeline_diagram.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("01_pipeline_diagram.png 저장 완료")


# ═══════════════════════════════════════════════════════════════════
# 02. 히트맵
# ═══════════════════════════════════════════════════════════════════

def draw_heatmap():
    from matplotlib.colors import LinearSegmentedColormap

    rows = [
        ("AAPL",  "NON_COMPLIANT",  0.0252, "PASS", "FAIL"),
        ("MSFT",  "COMPLIANT",      0.0191, "PASS", "PASS"),
        ("GOOGL", "NON_COMPLIANT",  0.0126, "PASS", "FAIL"),
        ("NVDA",  "COMPLIANT",      0.0021, "PASS", "PASS"),
        ("META",  "QUESTIONABLE",   0.0540, "PASS", "UNCERTAIN"),
        ("TSLA",  "NON_COMPLIANT",  0.0104, "PASS", "FAIL"),
        ("AMZN",  "NON_COMPLIANT",  0.0536, "PASS", "FAIL"),
        ("JPM",   "NON_COMPLIANT",  0.6083, "FAIL", "FAIL"),
        ("BAC",   "NON_COMPLIANT",  0.9877, "FAIL", "FAIL"),
        ("V",     "NON_COMPLIANT",  0.0405, "PASS", "FAIL"),
        ("JNJ",   "COMPLIANT",      0.0865, "PASS", "PASS"),
        ("PFE",   "NON_COMPLIANT",  0.4341, "FAIL", "PASS"),
        ("UNH",   "NON_COMPLIANT",  0.2290, "PASS", "FAIL"),
        ("MCD",   "NON_COMPLIANT",  0.2763, "PASS", "FAIL"),
        ("COST",  "NON_COMPLIANT",  0.0184, "PASS", "FAIL"),
        ("WMT",   "NON_COMPLIANT",  0.0710, "PASS", "FAIL"),
        ("XOM",   "COMPLIANT",      0.0701, "PASS", "PASS"),
        ("TSM",   "NON_COMPLIANT",  0.4978, "FAIL", "PASS"),
        ("LMT",   "NON_COMPLIANT",  0.1766, "PASS", "FAIL"),
        ("MO",    "NON_COMPLIANT",  0.2127, "PASS", "FAIL"),
    ]
    sectors = {
        "AAPL":"기술","MSFT":"기술","GOOGL":"기술","NVDA":"기술","META":"기술",
        "TSLA":"전기차","AMZN":"이커머스",
        "JPM":"금융","BAC":"금융","V":"금융",
        "JNJ":"헬스케어","PFE":"헬스케어","UNH":"헬스케어",
        "MCD":"소비재","COST":"소비재","WMT":"소비재",
        "XOM":"에너지","TSM":"반도체","LMT":"방산","MO":"담배",
    }
    vmap = {"PASS":1.0,"FAIL":0.0,"UNCERTAIN":0.5,
            "COMPLIANT":1.0,"NON_COMPLIANT":0.0,"QUESTIONABLE":0.5}

    n = len(rows)
    matrix = np.zeros((n, 4))
    for i, (t, v, dr, qn, ql) in enumerate(rows):
        matrix[i, 0] = max(0.0, min(1.0, 1.0 - dr / 0.33))
        matrix[i, 1] = vmap[qn]
        matrix[i, 2] = vmap[ql]
        matrix[i, 3] = vmap[v]

    cmap = LinearSegmentedColormap.from_list(
        "halal", ["#EF4444", "#F59E0B", "#22C55E"], N=256)

    fig, ax = plt.subplots(figsize=(13, 12))
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)

    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1,
                   interpolation="nearest")

    col_labels = ["부채비율\n(기준 33%)", "정량 심사\n(Quant)", "정성 심사\n(Qual LLM)", "종합 판정"]
    ax.set_xticks(range(4))
    ax.set_xticklabels(col_labels, color=_TXT, fontsize=11, fontweight="bold")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    y_labels = [f"{t}  ({sectors[t]})" for t, *_ in rows]
    ax.set_yticks(range(n))
    ax.set_yticklabels(y_labels, color=_TXT, fontsize=10)
    ax.tick_params(colors=_TXT, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    verdict_short = {"COMPLIANT": "PASS", "NON_COMPLIANT": "FAIL", "QUESTIONABLE": "UNCERTAIN"}
    for i, (t, v, dr, qn, ql) in enumerate(rows):
        texts = [f"{dr:.1%}", qn, ql, verdict_short[v]]
        for j, txt in enumerate(texts):
            col = "#0F1117" if matrix[i, j] > 0.65 else _TXT
            ax.text(j, i, txt, ha="center", va="center",
                    color=col, fontsize=9, fontweight="bold")

    for i in range(1, n):
        if sectors[rows[i][0]] != sectors[rows[i-1][0]]:
            ax.axhline(i - 0.5, color="#334155", lw=1.5, zorder=5)

    cbar = plt.colorbar(im, ax=ax, orientation="horizontal",
                        pad=0.02, fraction=0.025, shrink=0.45)
    cbar.ax.tick_params(colors=_TXT, labelsize=8)
    cbar.ax.set_xlabel("<-- 위험 (FAIL)          안전 (PASS) -->",
                       color=_DIM, fontsize=8)
    cbar.outline.set_edgecolor("#334155")
    cbar.ax.set_facecolor(_BG)

    ax.set_title(
        "Sharia Screener  —  20개 종목 심사 결과 히트맵\n"
        "2025년 5월 기준  ·  AAOIFI 기준  ·  Google Gemini 2.5 Flash",
        color=_TXT, fontsize=13, fontweight="bold", pad=38)

    patches = [
        mpatches.Patch(color="#22C55E", label="COMPLIANT (준수)"),
        mpatches.Patch(color="#F59E0B", label="QUESTIONABLE (검토 필요)"),
        mpatches.Patch(color="#EF4444", label="NON_COMPLIANT (불준수)"),
    ]
    ax.legend(handles=patches, loc="lower right", bbox_to_anchor=(1.0, -0.08),
              ncol=3, facecolor=_BOX, edgecolor="#334155",
              labelcolor=_TXT, fontsize=9, framealpha=0.9)

    plt.tight_layout()
    plt.savefig("assets/02_heatmap.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("02_heatmap.png 저장 완료")


# ═══════════════════════════════════════════════════════════════════
# 03. MCP Tool 호출 시연
# ═══════════════════════════════════════════════════════════════════

def draw_mcp_demo():
    W, H = 17, 10
    fig, ax = make_ax(W, H)

    # ── 제목 ────────────────────────────────────────────────────
    ax.text(W / 2, 9.72, "MCP Tool 호출 시연  —  Claude Desktop  <->  Sharia Screener",
            ha="center", color=_TXT, fontsize=15, fontweight="bold")
    ax.text(W / 2, 9.38, "자연어 요청  ->  Tool 자동 선택  ->  파이프라인 실행  ->  결과 반환",
            ha="center", color=_DIM, fontsize=10)

    # ── 패널 좌표 ────────────────────────────────────────────────
    # 왼쪽: Claude Desktop 채팅창
    LPX, LPY, LPW, LPH = 0.25, 0.25, 7.30, 8.80
    # 오른쪽 위: FastMCP Server
    RTP_X, RTP_Y, RTP_W, RTP_H = 7.80, 4.90, 8.95, 4.15
    # 오른쪽 아래 왼쪽: PostgreSQL
    RBL_X, RBL_Y, RBL_W, RBL_H = 7.80, 0.25, 4.35, 4.40
    # 오른쪽 아래 오른쪽: ChromaDB
    RBR_X, RBR_Y, RBR_W, RBR_H = 12.40, 0.25, 4.35, 4.40

    # ── 패널 그리기 ──────────────────────────────────────────────
    panel_box(ax, LPX, LPY, LPW, LPH, "Claude Desktop",
              tc=_BLUE, title_h=0.40)
    panel_box(ax, RTP_X, RTP_Y, RTP_W, RTP_H, "FastMCP Server  —  Tool 처리",
              tc=_GREEN, title_h=0.40)
    panel_box(ax, RBL_X, RBL_Y, RBL_W, RBL_H, "PostgreSQL  —  결과 저장",
              tc=_BLUE, title_h=0.40)
    panel_box(ax, RBR_X, RBR_Y, RBR_W, RBR_H, "ChromaDB  —  벡터 검색",
              tc=_BLUE, title_h=0.40)

    # ── 채팅 헬퍼 ────────────────────────────────────────────────
    CHAT_X  = LPX + 0.20          # 채팅 텍스트 시작 x
    CHAT_RX = LPX + LPW - 0.20   # 채팅 텍스트 끝 x
    CHAT_W  = CHAT_RX - CHAT_X

    def role_tag(y, who="User"):
        c = "#93C5FD" if who == "User" else "#6EE7B7"
        ax.text(CHAT_X, y, who, color=c, fontsize=8,
                fontweight="bold", va="top", zorder=4)

    def chat_line(y, text, col=_TXT, size=8.5, indent=0.0, mono=False):
        ax.text(CHAT_X + indent, y, text, color=col, fontsize=size,
                va="top", family="monospace" if mono else None, zorder=4)

    def tool_chip(y, call_text):
        """초록 점선 박스: Tool 호출 표시"""
        h = 0.40
        bw = CHAT_W
        p = FancyBboxPatch((CHAT_X, y - h), bw, h,
                           boxstyle="round,pad=0,rounding_size=0.08",
                           facecolor="#0A1F0E", edgecolor=_GREEN,
                           lw=1.2, ls="dashed", zorder=3)
        ax.add_patch(p)
        ax.text(CHAT_X + 0.12, y - h / 2, "Tool:",
                color=_GREEN, fontsize=7.5, fontweight="bold", va="center", zorder=4)
        ax.text(CHAT_X + 0.68, y - h / 2, call_text,
                color="#86EFAC", fontsize=7.8, va="center",
                family="monospace", zorder=4)

    def hdiv(y):
        ax.plot([CHAT_X, CHAT_RX], [y, y], color="#1E2D45", lw=0.8, zorder=3)

    # ─── 채팅 내용 (위 → 아래) ───────────────────────────────────
    # 모든 y 값은 각 텍스트의 top 기준

    # 1. 사용자 질문
    cy = LPY + LPH - 0.60
    role_tag(cy, "User");                    cy -= 0.30
    chat_line(cy, "AAPL, MSFT, JPM 샤리아 심사 결과 알려줘.");  cy -= 0.28
    chat_line(cy, "이슬람 투자자 기준으로 사도 되는 종목만.", col=_DIM); cy -= 0.18

    # 2. Tool 호출
    cy -= 0.05
    tool_chip(cy, 'screen_multiple_stocks(["AAPL", "MSFT", "JPM"])'); cy -= 0.52

    hdiv(cy); cy -= 0.15

    # 3. Claude 응답
    role_tag(cy, "Claude");                  cy -= 0.30
    chat_line(cy, "3종목 심사 완료 (2025-05):"); cy -= 0.30
    chat_line(cy, "COMPLIANT     MSFT", col="#4ADE80", indent=0.2, mono=True); cy -= 0.26
    chat_line(cy, "  부채 1.9%  |  소프트웨어·클라우드 사업 적합", col=_DIM, indent=0.2); cy -= 0.28
    chat_line(cy, "NON_COMPLIANT AAPL", col="#F87171", indent=0.2, mono=True); cy -= 0.26
    chat_line(cy, "  광고·앱스토어 수수료 수익 -> 할랄 위반", col=_DIM, indent=0.2); cy -= 0.28
    chat_line(cy, "NON_COMPLIANT JPM",  col="#F87171", indent=0.2, mono=True); cy -= 0.26
    chat_line(cy, "  부채비율 60.8% 초과  |  이자 기반 금융업", col=_DIM, indent=0.2); cy -= 0.28
    chat_line(cy, "=> MSFT 만 샤리아 기준에 적합합니다.", col="#FDE68A", indent=0.2); cy -= 0.22

    hdiv(cy); cy -= 0.18

    # 4. 사용자 후속 질문
    role_tag(cy, "User");                    cy -= 0.30
    chat_line(cy, "기술 섹터 할랄 주식 목록 더 알려줘.");  cy -= 0.18

    # 5. Tool 호출
    cy -= 0.05
    tool_chip(cy, 'list_compliant_stocks(sector="Technology")');  cy -= 0.52

    hdiv(cy); cy -= 0.15

    # 6. Claude 응답
    role_tag(cy, "Claude");                  cy -= 0.30
    chat_line(cy, "기술 섹터 COMPLIANT 종목 (2025-05):"); cy -= 0.30
    chat_line(cy, "  MSFT — 소프트웨어·클라우드", col="#4ADE80"); cy -= 0.26
    chat_line(cy, "  NVDA — 반도체 설계", col="#4ADE80"); cy -= 0.26
    chat_line(cy, "  AAPL·GOOGL·META 는 부적합 판정.", col=_DIM); cy -= 0.10

    # ─── FastMCP Server 내용 ─────────────────────────────────────
    SX  = RTP_X + 0.22
    SY0 = RTP_Y + RTP_H - 0.62   # 첫 줄 y

    def srv(dy_offset, text, col=_TXT, size=8.0, bold=False):
        ax.text(SX, SY0 - dy_offset, text, color=col, fontsize=size,
                va="top", family="monospace", fontweight="bold" if bold else "normal", zorder=4)

    def srv_section(dy, title):
        ax.text(SX, SY0 - dy, title, color=_DIM, fontsize=7.5, va="top", zorder=4)

    srv_section(0.00, "# 수신된 MCP 요청")
    srv(0.28, 'tool:  "screen_multiple_stocks"',         col="#A5B4FC")
    srv(0.54, 'args:  {"tickers": ["AAPL","MSFT","JPM"]}', col=_TXT)

    srv_section(0.92, "# 파이프라인 실행  (AAPL 예시)")
    srv(1.20, "DataCollector.collect('AAPL')   ->  OK",       col="#6EE7B7")
    srv(1.46, "QuantEngine.screen('AAPL')       ->  PASS",     col="#86EFAC")
    srv(1.72, "QualEngine.screen('AAPL')        ->  FAIL",     col="#FCA5A5")
    srv(1.98, "Judge()                          ->  NON_COMPLIANT", col="#FCA5A5")
    srv(2.24, "DBHandler.save()                 ->  OK",       col="#6EE7B7")

    srv_section(2.62, "# 반환값  (ScreeningResult)")
    srv(2.90, 'final_verdict:  "NON_COMPLIANT"',   col="#FCA5A5")
    srv(3.16, "debt_ratio:      2.52%  (PASS)",    col="#86EFAC")
    srv(3.42, "qual_verdict:    FAIL",              col="#FCA5A5")

    # ─── PostgreSQL ──────────────────────────────────────────────
    DBX  = RBL_X + 0.22
    DBY0 = RBL_Y + RBL_H - 0.62

    def db(dy, text, col=_TXT, size=8.0):
        ax.text(DBX, DBY0 - dy, text, color=col, fontsize=size,
                va="top", family="monospace", zorder=4)

    db(0.00, "# screening_results",          col=_DIM)
    db(0.28, "AAPL  NON_COMPLIANT  2025-05", col="#F87171")
    db(0.54, "MSFT  COMPLIANT      2025-05", col="#4ADE80")
    db(0.80, "JPM   NON_COMPLIANT  2025-05", col="#F87171")
    db(1.06, "NVDA  COMPLIANT      2025-05", col="#4ADE80")
    db(1.44, "# 캐시",                       col=_DIM)
    db(1.72, "TTL: 7일",                     col="#94A3B8")
    db(1.98, "HIT -> 즉시 반환 (LLM skip)", col="#94A3B8")
    db(2.36, "# 재무 지표",                  col=_DIM)
    db(2.64, "debt_ratio",                   col="#94A3B8")
    db(2.90, "interest_income_ratio",        col="#94A3B8")
    db(3.16, "non_halal_revenue_ratio",      col="#94A3B8")

    # ─── ChromaDB ────────────────────────────────────────────────
    VX  = RBR_X + 0.22
    VY0 = RBR_Y + RBR_H - 0.62

    def vdb(dy, text, col=_TXT, size=8.0):
        ax.text(VX, VY0 - dy, text, color=col, fontsize=size,
                va="top", family="monospace", zorder=4)

    vdb(0.00, "# embedding model",             col=_DIM)
    vdb(0.28, "all-MiniLM-L6-v2",             col="#94A3B8")
    vdb(0.66, "# 저장된 근거 텍스트",          col=_DIM)
    vdb(0.94, "AAPL: 광고·앱 수수료 수익...", col=_TXT)
    vdb(1.20, "JPM:  이자 수입 60% 초과...",  col=_TXT)
    vdb(1.46, "MO:   담배 제조·판매 전업...", col=_TXT)
    vdb(1.84, "# RAG 활용",                    col=_DIM)
    vdb(2.12, "explain_screening_decision()",  col="#86EFAC")
    vdb(2.38, "  -> 코사인 유사도 검색",       col="#94A3B8")
    vdb(2.64, "  -> 자연어 근거 생성",         col="#94A3B8")

    # ── 연결 화살표 (왼쪽 패널 <-> 오른쪽 상단 패널) ───────────────
    # Claude Desktop 오른쪽 끝 → FastMCP 왼쪽 끝
    CLD_RX = LPX + LPW
    FMC_LX = RTP_X
    MID_Y  = (RTP_Y + RTP_Y + RTP_H) / 2

    arr(ax, CLD_RX, MID_Y + 0.25, FMC_LX, MID_Y + 0.25, c=_GREEN)   # 요청
    arr(ax, FMC_LX, MID_Y - 0.25, CLD_RX, MID_Y - 0.25, c=_BLUE)    # 응답

    ax.text((CLD_RX + FMC_LX) / 2, MID_Y + 0.42, "요청",
            ha="center", color=_GREEN, fontsize=7.5, fontweight="bold")
    ax.text((CLD_RX + FMC_LX) / 2, MID_Y - 0.50, "결과",
            ha="center", color=_BLUE, fontsize=7.5, fontweight="bold")

    # FastMCP → DB 화살표
    FMC_BY = RTP_Y
    arr(ax, RBL_X + RBL_W / 2, FMC_BY, RBL_X + RBL_W / 2, RBL_Y + RBL_H, c=_ARR)
    arr(ax, RBR_X + RBR_W / 2, FMC_BY, RBR_X + RBR_W / 2, RBR_Y + RBR_H, c=_ARR)

    # ── 하단 흐름 설명 ────────────────────────────────────────────
    steps = ("1. 사용자 자연어 입력   "
             "->  2. Claude 가 MCP Tool 자동 선택·호출   "
             "->  3. FastMCP 파이프라인 실행   "
             "->  4. 결과 자연어로 요약 반환")
    ax.text(W / 2, 0.12, steps,
            ha="center", color=_DIM, fontsize=8.2, va="bottom")

    plt.savefig("assets/03_mcp_demo.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("03_mcp_demo.png 저장 완료")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    draw_pipeline()
    draw_heatmap()
    draw_mcp_demo()
    print("\nassets/ 에 시각자료 3종 저장 완료")
