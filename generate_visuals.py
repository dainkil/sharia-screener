"""
학술제 포스터용 시각자료 3종 생성
1. 전체 파이프라인 다이어그램
2. 20개 종목 심사 결과 히트맵
3. MCP Tool 호출 시연 목업
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

os.makedirs("assets", exist_ok=True)

# ── 공통 폰트 설정 (한글) ─────────────────────────────────────────
import matplotlib.font_manager as fm

candidates = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/AppleGothic.ttf",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
]
korean_font = None
for c in candidates:
    if os.path.exists(c):
        fm.fontManager.addfont(c)
        prop = fm.FontProperties(fname=c)
        korean_font = prop.get_name()
        break

if korean_font:
    plt.rcParams["font.family"] = korean_font
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10


# ══════════════════════════════════════════════════════════════════
# 1. 전체 파이프라인 다이어그램
# ══════════════════════════════════════════════════════════════════
def draw_pipeline():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#0F1117")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    def box(x, y, w, h, label, sublabel="", color="#1E293B", text_color="white",
            border_color="#334155", fontsize=11, subfontsize=8.5, radius=0.3):
        p = FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle=f"round,pad=0.05,rounding_size={radius}",
            facecolor=color, edgecolor=border_color, linewidth=2.0, zorder=3
        )
        ax.add_patch(p)
        if sublabel:
            ax.text(x, y + 0.10, label, ha="center", va="center",
                    color=text_color, fontsize=fontsize, fontweight="bold", zorder=4)
            ax.text(x, y - 0.32, sublabel, ha="center", va="center",
                    color="#94A3B8", fontsize=subfontsize, zorder=4)
        else:
            ax.text(x, y, label, ha="center", va="center",
                    color=text_color, fontsize=fontsize, fontweight="bold", zorder=4)

    def arrow(x1, y1, x2, y2, color="#64748B"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=2.0, mutation_scale=18), zorder=2)

    def lbl(x, y, text, color="#94A3B8"):
        ax.text(x, y, text, ha="center", va="center", color=color,
                fontsize=7.5, style="italic", zorder=5)

    # 제목
    ax.text(8, 8.6, "Sharia Screener — 전체 파이프라인",
            ha="center", va="center", color="white", fontsize=17, fontweight="bold")
    ax.text(8, 8.2, "AAOIFI 기준  |  정량 + 정성 복합 심사  |  MCP 서버 연동",
            ha="center", va="center", color="#94A3B8", fontsize=10)

    # Layer 0: 데이터 소스
    box(2.0, 7.0, 2.8, 0.8, "[ yfinance ]", "실시간 주가 · 재무 수집",
        color="#1E3A5F", border_color="#3B82F6")
    box(5.5, 7.0, 2.6, 0.8, "[ JSON Cache ]", "7일 로컬 캐시",
        color="#1E3A5F", border_color="#3B82F6")

    # Layer 1: DataCollector
    box(3.6, 5.7, 4.6, 0.82, "DataCollector",
        "재무 지표 정규화  (부채 / 매출 / 이자수익)",
        color="#1E3A2F", border_color="#22C55E")
    arrow(2.0, 6.60, 2.9, 6.11); lbl(2.3, 6.36, "Live")
    arrow(5.5, 6.60, 4.4, 6.11); lbl(5.2, 6.36, "Cache")

    # Layer 2: 심사 엔진
    box(2.0, 4.35, 3.2, 0.9, "QuantEngine",
        "부채비율 · 이자수익 · 비할랄수익\nAAOIFI 임계값 비교",
        color="#2D1B4E", border_color="#A855F7", subfontsize=7.5)
    box(5.5, 4.35, 3.2, 0.9, "QualEngine",
        "Gemini 2.5 Flash LLM\n사업모델 할랄 여부 판단",
        color="#2D1B4E", border_color="#A855F7", subfontsize=7.5)
    arrow(3.6, 5.29, 2.2, 4.80)
    arrow(3.6, 5.29, 5.3, 4.80)

    # Layer 3: Judge
    box(3.7, 3.0, 4.0, 0.85, "Judge (판정 결합)",
        "COMPLIANT  /  NON_COMPLIANT  /  QUESTIONABLE",
        color="#3B1A1A", border_color="#EF4444", subfontsize=8)
    arrow(2.0, 3.90, 2.8, 3.43)
    arrow(5.5, 3.90, 4.6, 3.43)

    # Layer 4: 저장소
    box(2.0, 1.75, 2.9, 0.85, "PostgreSQL", "결과 저장 · 7일 캐시",
        color="#1A2A3B", border_color="#38BDF8", subfontsize=8.5)
    box(5.5, 1.75, 2.9, 0.85, "ChromaDB", "근거 벡터 검색 (RAG)",
        color="#1A2A3B", border_color="#38BDF8", subfontsize=8.5)
    arrow(3.7, 2.57, 2.2, 2.18)
    arrow(3.7, 2.57, 5.2, 2.18)

    # Layer 5: MCP 서버
    box(3.7, 0.78, 4.6, 0.76, "FastMCP Server",
        color="#1A3B2A", border_color="#10B981", fontsize=12)
    arrow(2.0, 1.32, 2.85, 1.15)
    arrow(5.5, 1.32, 4.55, 1.15)

    # 우측: 클라이언트
    ax.plot([9.0, 9.0], [0.3, 8.5], color="#334155", lw=1.2, ls="--", zorder=1)
    ax.text(9.2, 8.5, "AI 클라이언트", color="#64748B", fontsize=9, va="top")

    box(11.5, 7.0, 3.8, 0.82, "Claude Desktop", "자연어 → Tool 자동 호출",
        color="#1A2A3B", border_color="#F59E0B")
    box(11.5, 5.5, 3.8, 0.82, "Claude Code", "CLI 에이전트 연동",
        color="#1A2A3B", border_color="#F59E0B")
    box(11.5, 4.0, 3.8, 0.82, "외부 AI Agent", "MCP 프로토콜 호환 클라이언트",
        color="#1A2A3B", border_color="#F59E0B")

    # MCP <-> 클라이언트 화살표
    for cy, rad in [(7.0, 0.10), (5.5, 0.05), (4.0, -0.05)]:
        ax.annotate("", xy=(9.5, cy), xytext=(5.95, 0.78),
                    arrowprops=dict(arrowstyle="<->", color="#10B981",
                                   lw=1.8, mutation_scale=14,
                                   connectionstyle=f"arc3,rad={rad}"), zorder=2)

    # MCP 도구 목록
    tools = ["screen_stock(ticker)",
             "screen_multiple_stocks(tickers)",
             "list_compliant_stocks(sector)",
             "explain_screening_decision(ticker)",
             "get_server_status()"]
    for i, t in enumerate(tools):
        ax.text(9.35, 7.45 - i * 0.48, f"  {t}", color="#6EE7B7",
                fontsize=7.8, va="center", family="monospace", zorder=5)

    # 범례
    patches = [
        mpatches.Patch(color="#3B82F6", label="데이터 소스"),
        mpatches.Patch(color="#22C55E", label="데이터 수집"),
        mpatches.Patch(color="#A855F7", label="심사 엔진"),
        mpatches.Patch(color="#EF4444", label="판정"),
        mpatches.Patch(color="#38BDF8", label="저장소"),
        mpatches.Patch(color="#10B981", label="MCP 서버"),
    ]
    ax.legend(handles=patches, loc="lower left", bbox_to_anchor=(0.0, 0.0),
              ncol=6, fontsize=8, facecolor="#1E293B", edgecolor="#334155",
              labelcolor="white", framealpha=0.9)

    plt.tight_layout(pad=0.3)
    plt.savefig("assets/01_pipeline_diagram.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("01_pipeline_diagram.png 저장 완료")


# ══════════════════════════════════════════════════════════════════
# 2. 20개 종목 심사 결과 히트맵
# ══════════════════════════════════════════════════════════════════
def draw_heatmap():
    from matplotlib.colors import LinearSegmentedColormap

    # 실제 DB 데이터
    rows = [
        # ticker,      final_verdict,   debt_ratio, quant, qual
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
        "AAPL":"기술", "MSFT":"기술", "GOOGL":"기술", "NVDA":"기술", "META":"기술",
        "TSLA":"전기차", "AMZN":"이커머스",
        "JPM":"금융", "BAC":"금융", "V":"금융",
        "JNJ":"헬스케어", "PFE":"헬스케어", "UNH":"헬스케어",
        "MCD":"소비재", "COST":"소비재", "WMT":"소비재",
        "XOM":"에너지", "TSM":"반도체", "LMT":"방산", "MO":"담배",
    }

    vmap = {"PASS":1.0, "FAIL":0.0, "UNCERTAIN":0.5,
            "COMPLIANT":1.0, "NON_COMPLIANT":0.0, "QUESTIONABLE":0.5}
    verdict_lbl = {"COMPLIANT":"COMPLIANT", "NON_COMPLIANT":"NON_COMPLIANT",
                   "QUESTIONABLE":"QUESTIONABLE"}

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
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#0F1117")

    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1,
                   interpolation="nearest")

    # 축
    col_labels = ["부채비율\n(기준: 33%)", "정량 심사\n(Quant)", "정성 심사\n(Qual LLM)", "종합 판정"]
    ax.set_xticks(range(4))
    ax.set_xticklabels(col_labels, color="white", fontsize=11, fontweight="bold")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    y_labels = [f"{t}  ({sectors[t]})" for t, *_ in rows]
    ax.set_yticks(range(n))
    ax.set_yticklabels(y_labels, color="white", fontsize=10)
    ax.tick_params(colors="white", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 셀 텍스트
    verdict_icon_text = {"COMPLIANT": "PASS", "NON_COMPLIANT": "FAIL", "QUESTIONABLE": "?"}
    for i, (t, v, dr, qn, ql) in enumerate(rows):
        texts = [f"{dr:.1%}", qn, ql, verdict_lbl[v]]
        bright = [matrix[i,j] > 0.65 for j in range(4)]
        for j, txt in enumerate(texts):
            col = "#0F1117" if bright[j] else "white"
            ax.text(j, i, txt, ha="center", va="center",
                    color=col, fontsize=9, fontweight="bold")

    # 섹터 구분선
    for i in range(1, n):
        s_cur  = sectors[rows[i][0]]
        s_prev = sectors[rows[i-1][0]]
        if s_cur != s_prev:
            ax.axhline(i - 0.5, color="#334155", linewidth=1.5, zorder=5)

    # 컬러바
    cbar = plt.colorbar(im, ax=ax, orientation="horizontal",
                        pad=0.02, fraction=0.025, shrink=0.45)
    cbar.ax.tick_params(colors="white", labelsize=8)
    cbar.ax.set_xlabel("<-- 위험 (FAIL)            안전 (PASS) -->",
                       color="#94A3B8", fontsize=8)
    cbar.outline.set_edgecolor("#334155")
    cbar.ax.set_facecolor("#0F1117")

    # 제목
    ax.set_title(
        "Sharia Screener — 20개 종목 심사 결과 히트맵\n"
        "2025년 5월 기준  |  AAOIFI 기준 적용  |  Google Gemini 2.5 Flash",
        color="white", fontsize=13, fontweight="bold", pad=38)

    # 범례
    patches = [
        mpatches.Patch(color="#22C55E", label="COMPLIANT (샤리아 준수)"),
        mpatches.Patch(color="#F59E0B", label="QUESTIONABLE (검토 필요)"),
        mpatches.Patch(color="#EF4444", label="NON_COMPLIANT (불준수)"),
    ]
    ax.legend(handles=patches, loc="lower right", bbox_to_anchor=(1.0, -0.08),
              ncol=3, facecolor="#1E293B", edgecolor="#334155",
              labelcolor="white", fontsize=9, framealpha=0.9)

    plt.tight_layout()
    plt.savefig("assets/02_heatmap.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("02_heatmap.png 저장 완료")


# ══════════════════════════════════════════════════════════════════
# 3. MCP Tool 호출 시연 목업
# ══════════════════════════════════════════════════════════════════
def draw_mcp_demo():
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor("#0A0E1A")
    ax.set_facecolor("#0A0E1A")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # 제목
    ax.text(8.0, 9.65, "MCP Tool 호출 시연  —  Claude Desktop <-> Sharia Screener",
            ha="center", va="center", color="white", fontsize=15, fontweight="bold")
    ax.text(8.0, 9.28, "자연어 요청  ->  MCP Tool 자동 선택  ->  파이프라인 실행  ->  결과 반환",
            ha="center", va="center", color="#94A3B8", fontsize=10)

    # ── 유틸 ──────────────────────────────────────────────────────
    def panel(x, y, w, h, title, tc="#3B82F6", bg="#1A2235", bc="#2D4070"):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.18",
                           facecolor=bg, edgecolor=bc, linewidth=1.8, zorder=2)
        ax.add_patch(p)
        tb = FancyBboxPatch((x + 0.02, y + h - 0.42), w - 0.04, 0.40,
                            boxstyle="round,pad=0.0,rounding_size=0.15",
                            facecolor=tc + "28", edgecolor="none", zorder=3)
        ax.add_patch(tb)
        # traffic lights
        for di, dc in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
            cx = x + 0.22 + di * 0.22
            cy = y + h - 0.22
            circ = plt.Circle((cx, cy), 0.07, color=dc, zorder=4)
            ax.add_patch(circ)
        ax.text(x + 1.0, y + h - 0.22, title, color=tc, fontsize=9.5,
                fontweight="bold", va="center", zorder=4)

    def chat_bubble(x, y, w, h, lines, role="user"):
        bg = "#1A3060" if role == "user" else "#0F3020"
        bc = "#3B82F6" if role == "user" else "#10B981"
        tag = "User" if role == "user" else "Claude"
        tag_col = "#93C5FD" if role == "user" else "#6EE7B7"
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.14",
                           facecolor=bg, edgecolor=bc, linewidth=1.2, zorder=3)
        ax.add_patch(p)
        ax.text(x + 0.18, y + h - 0.22, tag, color=tag_col,
                fontsize=7.5, fontweight="bold", va="center", zorder=4)
        for i, (txt, col, mono) in enumerate(lines):
            if not txt or not col:
                continue
            ax.text(x + 0.18, y + h - 0.50 - i * 0.285,
                    txt, color=col, fontsize=8.3, va="center",
                    family="monospace" if mono else None, zorder=4)

    def tool_call_box(x, y, w, call_text):
        p = FancyBboxPatch((x, y), w, 0.48, boxstyle="round,pad=0.04,rounding_size=0.10",
                           facecolor="#0B2010", edgecolor="#22C55E",
                           linewidth=1.3, ls="dashed", zorder=3)
        ax.add_patch(p)
        ax.text(x + 0.18, y + 0.24, "[ Tool ]", color="#22C55E",
                fontsize=8, fontweight="bold", va="center", zorder=4)
        ax.text(x + 0.82, y + 0.24, call_text, color="#6EE7B7",
                fontsize=8, va="center", family="monospace", zorder=4)

    def code_line(x, y, text, col="#E2E8F0", size=8.0, mono=True):
        if not text or not col:
            return
        ax.text(x, y, text, color=col, fontsize=size, va="center",
                family="monospace" if mono else None, zorder=4)

    # ══ 왼쪽: Claude Desktop 채팅창 ══════════════════════════════
    panel(0.3, 0.4, 7.0, 8.6, "Claude Desktop", tc="#3B82F6",
          bg="#0E1528", bc="#1E3A6E")

    # 대화 1: 사용자 질문
    chat_bubble(0.6, 7.3, 6.4, 1.3,
        [("AAPL, MSFT, JPM 중 이슬람 투자자가", "white", False),
         ("사도 되는 주식이 어떤 건지 알려줘.", "white", False),
         ("근거도 같이 설명해줘.", "#93C5FD", False)],
        role="user")

    # Tool 호출 박스
    tool_call_box(0.6, 6.76, 6.4,
                  'screen_multiple_stocks(["AAPL","MSFT","JPM"])')

    # 대화 2: Claude 응답
    chat_bubble(0.6, 3.65, 6.4, 2.95,
        [("심사 결과를 안내드릴게요.", "white", False),
         ("", "", False),
         ("[COMPLIANT]  MSFT", "#4ADE80", True),
         ("  부채비율 1.9%  /  사업 모델 적합 (소프트웨어·클라우드)", "#94A3B8", False),
         ("[NON_COMPLIANT]  AAPL", "#F87171", True),
         ("  광고·앱스토어 수수료 수익 -> 할랄 위반", "#94A3B8", False),
         ("[NON_COMPLIANT]  JPM", "#F87171", True),
         ("  부채비율 60.8% 초과  /  이자 기반 금융업", "#94A3B8", False),
         ("=> MSFT 만 샤리아 기준 충족합니다.", "#FDE68A", False)],
        role="ai")

    # 대화 3: 추가 질문
    chat_bubble(0.6, 2.95, 6.4, 0.58,
        [("기술 섹터 할랄 주식 목록 더 알려줘.", "white", False)],
        role="user")

    tool_call_box(0.6, 2.43, 6.4,
                  'list_compliant_stocks(sector="Technology")')

    chat_bubble(0.6, 0.85, 6.4, 1.45,
        [("기술 섹터 COMPLIANT 종목 (2025-05):", "#6EE7B7", False),
         ("  MSFT — 부채 1.9%, 소프트웨어 / 클라우드", "#4ADE80", False),
         ("  NVDA — 부채 0.2%, 반도체 설계", "#4ADE80", False),
         ("  AAPL / GOOGL / META 는 부적합 판정.", "#94A3B8", False)],
        role="ai")

    # ══ 오른쪽 위: FastMCP 서버 패널 ═════════════════════════════
    panel(7.7, 5.2, 7.9, 3.7, "FastMCP Server  —  Tool 처리",
          tc="#10B981", bg="#091A10", bc="#0B4D23")

    srv_lines = [
        ("# 수신된 MCP 요청",                           "#4B5563"),
        ('tool:  "screen_multiple_stocks"',              "#E2E8F0"),
        ('args:  {"tickers": ["AAPL","MSFT","JPM"]}',   "#E2E8F0"),
        ("",                                             ""),
        ("# 파이프라인 실행 (AAPL 예시)",               "#4B5563"),
        ("DataCollector.collect('AAPL')   OK",           "#6EE7B7"),
        ("QuantEngine.screen('AAPL')      OK  -> PASS",  "#6EE7B7"),
        ("QualEngine.screen('AAPL')       OK  -> FAIL",  "#F87171"),
        ("Judge()                         -> NON_COMPLIANT", "#F87171"),
        ("DBHandler.save()                OK",           "#6EE7B7"),
        ("",                                             ""),
        ("# 반환값 (ScreeningResult)",                  "#4B5563"),
        ('final_verdict:  "NON_COMPLIANT"',              "#FCA5A5"),
        ('debt_ratio:     2.52%  (PASS)',                "#86EFAC"),
        ('qual_verdict:   FAIL   (광고·앱수수료)',       "#FCA5A5"),
    ]
    for i, (txt, col) in enumerate(srv_lines):
        code_line(7.95, 8.50 - i * 0.285, txt, col=col, size=7.9)

    # ══ 오른쪽 아래 왼쪽: PostgreSQL ════════════════════════════
    panel(7.7, 0.4, 3.8, 4.6, "PostgreSQL  —  결과 저장",
          tc="#38BDF8", bg="#080F1E", bc="#0E2A4A")

    db_lines = [
        ("screening_results:",               "#64748B"),
        ("  AAPL  NON_COMPLIANT  2025-05",   "#F87171"),
        ("  MSFT  COMPLIANT      2025-05",   "#4ADE80"),
        ("  JPM   NON_COMPLIANT  2025-05",   "#F87171"),
        ("  NVDA  COMPLIANT      2025-05",   "#4ADE80"),
        ("",                                 ""),
        ("캐시 TTL: 7일",                    "#64748B"),
        ("캐시 HIT 시 즉시 반환 (no LLM)",  "#94A3B8"),
        ("",                                 ""),
        ("financial_data:",                  "#64748B"),
        ("  debt_ratio, interest_income,",   "#94A3B8"),
        ("  non_halal_revenue, market_cap",  "#94A3B8"),
    ]
    for i, (txt, col) in enumerate(db_lines):
        code_line(7.95, 4.60 - i * 0.305, txt, col=col, size=7.6)

    # ══ 오른쪽 아래 오른쪽: ChromaDB ════════════════════════════
    panel(11.7, 0.4, 3.8, 4.6, "ChromaDB  —  벡터 검색",
          tc="#38BDF8", bg="#080F1E", bc="#0E2A4A")

    chroma_lines = [
        ("embedding model:",                    "#64748B"),
        ("  all-MiniLM-L6-v2",                 "#94A3B8"),
        ("",                                    ""),
        ("저장된 근거 텍스트:",                  "#64748B"),
        ("  AAPL: 광고 수익 기반 수익구조...", "#E2E8F0"),
        ("  JPM:  이자 수입 60% 초과...",       "#E2E8F0"),
        ("  MO:   담배 제조·판매 전업...",      "#E2E8F0"),
        ("",                                    ""),
        ("RAG 활용:",                           "#64748B"),
        ("  explain_screening_decision()",      "#94A3B8"),
        ("  -> 유사 근거 코사인 검색",          "#94A3B8"),
        ("  -> 자연어 설명 생성",               "#94A3B8"),
    ]
    for i, (txt, col) in enumerate(chroma_lines):
        code_line(11.9, 4.60 - i * 0.305, txt, col=col, size=7.6)

    # 연결 화살표 (Claude Desktop <-> FastMCP)
    ax.annotate("", xy=(7.7, 7.1), xytext=(7.0, 6.9),
                arrowprops=dict(arrowstyle="-|>", color="#10B981", lw=2.2, mutation_scale=16))
    ax.annotate("", xy=(7.0, 6.6), xytext=(7.7, 6.4),
                arrowprops=dict(arrowstyle="-|>", color="#3B82F6", lw=2.2, mutation_scale=16))
    ax.text(7.35, 7.05, "요청", color="#10B981", fontsize=8, ha="center", fontweight="bold")
    ax.text(7.35, 6.35, "결과", color="#3B82F6", fontsize=8, ha="center", fontweight="bold")

    # FastMCP -> DB 화살표
    ax.annotate("", xy=(9.6, 5.2), xytext=(9.6, 5.0),
                arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.5, mutation_scale=12))
    ax.annotate("", xy=(13.6, 5.2), xytext=(13.6, 5.0),
                arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.5, mutation_scale=12))

    # 하단 흐름 설명
    ax.text(0.4, 0.15,
            "1. 사용자 자연어 입력  ->  2. Claude 가 MCP Tool 자동 선택·호출  ->  "
            "3. FastMCP 파이프라인 실행  ->  4. 결과를 자연어로 요약 반환",
            color="#64748B", fontsize=8.5, va="center")

    plt.tight_layout(pad=0.3)
    plt.savefig("assets/03_mcp_demo.png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("03_mcp_demo.png 저장 완료")


if __name__ == "__main__":
    draw_pipeline()
    draw_heatmap()
    draw_mcp_demo()
    print("\nassets/ 폴더에 시각자료 3종 저장 완료")
