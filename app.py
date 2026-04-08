import streamlit as st
import PyPDF2
from groq import Groq
import json
import time
import streamlit.components.v1 as components

# --- CONFIG ---
st.set_page_config(page_title="LawLytics", page_icon="⚖️", layout="wide")

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ═══ SIDEBAR — always dark ═══ */
[data-testid="stSidebar"] { background: #090b14 !important; border-right: 1px solid #1a1d2e; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox > div { background: #111827 !important; border: 1px solid #2d3148 !important; border-radius: 8px !important; }

.law-logo { display:flex; align-items:center; gap:14px; padding:24px 0 20px 0; border-bottom:1px solid #1a1d2e; margin-bottom:18px; }
.law-logo-icon { width:40px; height:40px; background:linear-gradient(135deg,#6366f1,#8b5cf6); border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:18px; box-shadow:0 4px 14px rgba(99,102,241,0.4); flex-shrink:0; }
.law-logo-text { font-size:1.1rem; font-weight:700; color:#f1f5f9 !important; letter-spacing:-0.4px; }
.law-logo-sub  { font-size:0.67rem; color:#374151 !important; letter-spacing:0.04em; margin-top:2px; }
.sidebar-label { font-size:0.6rem !important; text-transform:uppercase; letter-spacing:0.14em; color:#374151 !important; font-weight:700; margin:16px 0 7px 0; }

/* ═══ MAIN ═══ */
.main .block-container { padding: 2rem 2.5rem; max-width: 1180px; }

/* page header */
.page-header { margin-bottom:1.8rem; padding-bottom:1.4rem; border-bottom:1px solid rgba(148,163,184,0.15); }
.page-header h1 { font-size:1.7rem; font-weight:700; letter-spacing:-0.5px; margin:0 0 4px 0; }
.page-header p  { font-size:0.86rem; color:#94a3b8; margin:0; }

/* primary button */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; font-size:0.92rem !important;
    padding:0.7rem 1.4rem !important; box-shadow:0 4px 14px rgba(99,102,241,0.35) !important;
    transition:all 0.2s ease !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover { transform:translateY(-1px); box-shadow:0 8px 22px rgba(99,102,241,0.45) !important; }

/* secondary button */
[data-testid="stButton"] > button:not([kind="primary"]) {
    border-radius:9px !important; font-weight:600 !important; font-size:0.88rem !important;
    border:1px solid rgba(148,163,184,0.3) !important;
}

/* classification tag */
.doc-class-tag { display:inline-flex; align-items:center; gap:8px; background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.3); color:#818cf8; border-radius:8px; padding:5px 13px; font-weight:600; font-size:0.82rem; margin-bottom:1.3rem; }

/* tabs */
[data-testid="stTabs"] [role="tab"] { font-size:0.83rem !important; font-weight:600 !important; padding:10px 18px !important; border-radius:0 !important; border-bottom:2px solid transparent !important; transition:all 0.2s; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color:#818cf8 !important; border-bottom:2px solid #818cf8 !important; background:transparent !important; }

/* ═══ RISK CARD — dark always ═══ */
.risk-card { background:#0d1117; border:1px solid #21262d; border-radius:18px; padding:28px 24px; box-shadow:0 2px 20px rgba(0,0,0,0.4); text-align:center; }
.risk-card-label { font-size:0.69rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#4b5563; margin-bottom:10px; }
.risk-score-num { font-size:5rem; font-weight:900; line-height:1; font-family:'JetBrains Mono',monospace; margin-bottom:4px; }
.risk-score-denom { font-size:1.5rem; font-weight:400; color:#374151; }
.risk-badge { display:inline-block; border-radius:999px; padding:5px 18px; font-size:0.77rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin:14px 0 12px 0; }
.badge-safe     { background:#064e3b; color:#6ee7b7; border:1px solid #065f46; }
.badge-moderate { background:#451a03; color:#fbbf24; border:1px solid #78350f; }
.badge-risky    { background:#450a0a; color:#fca5a5; border:1px solid #7f1d1d; }
.party-tag { font-size:0.79rem; color:#64748b; margin-bottom:16px; font-weight:500; }
.party-tag strong { color:#e2e8f0; }
.gauge-track { width:100%; height:7px; background:#161b22; border-radius:999px; overflow:hidden; }
.gauge-fill  { height:100%; border-radius:999px; transition:width 0.8s cubic-bezier(0.4,0,0.2,1); }

/* ═══ RISK ROWS — dark always ═══ */
.risk-rows-wrap { border:1px solid #21262d; border-radius:14px; padding:4px 14px; background:#0d1117; }
.risk-row { display:flex; align-items:flex-start; gap:12px; padding:13px 0; border-bottom:1px solid #161b22; }
.risk-row:last-child { border-bottom:none; }
.sev-pill { flex-shrink:0; font-size:0.65rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; border-radius:6px; padding:3px 9px; border:1px solid; }
.sev-high   { background:#450a0a; color:#fca5a5; border-color:#7f1d1d; }
.sev-medium { background:#451a03; color:#fbbf24; border-color:#78350f; }
.sev-low    { background:#064e3b; color:#6ee7b7; border-color:#065f46; }
.risk-text  { font-size:0.88rem; color:#94a3b8; line-height:1.6; }

/* ═══ TAB SECTION TITLES ═══ */
.tsec { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; margin:20px 0 9px 0; }
.tsec:first-child { margin-top:4px; }

/* ═══ INFO CARDS — adapts to theme ═══ */
.info-card { background:rgba(99,102,241,0.06); border-left:3px solid #6366f1; border-radius:0 12px 12px 0; padding:14px 18px; font-size:0.9rem; color:#94a3b8; line-height:1.75; border-top:1px solid rgba(99,102,241,0.1); border-right:1px solid rgba(99,102,241,0.1); border-bottom:1px solid rgba(99,102,241,0.1); }
.info-card-green { border-left-color:#10b981; border-top-color:rgba(16,185,129,0.1); border-right-color:rgba(16,185,129,0.1); border-bottom-color:rgba(16,185,129,0.1); background:rgba(16,185,129,0.06); }

/* ═══ CLAUSE CHIPS — dark ═══ */
.clause-chip { background:#1c1a0e; border:1px solid #3a3010; border-radius:10px; padding:11px 15px; font-size:0.87rem; color:#fde68a; margin-bottom:9px; line-height:1.6; }
.clause-num  { font-family:'JetBrains Mono',monospace; font-size:0.66rem; color:#fbbf24; font-weight:700; margin-bottom:3px; }

/* ═══ ADVISORY CARD — always dark ═══ */
.advisory-card { background:#0d1117; border-radius:18px; padding:30px; color:#e2e8f0; border:1px solid #21262d; box-shadow:0 8px 32px rgba(0,0,0,0.4); }
.advisory-card h2 { font-size:1.05rem; font-weight:700; color:#a5b4fc; margin:0 0 22px 0; letter-spacing:-0.3px; }
.adv-label { font-size:0.67rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#818cf8; margin-bottom:7px; }
.adv-body  { font-size:0.9rem; line-height:1.75; color:#94a3b8; margin-bottom:22px; }
.adv-divider { border:none; border-top:1px solid #21262d; margin:22px 0; }
.tip-item { display:flex; align-items:flex-start; gap:11px; margin-bottom:12px; }
.tip-num  { width:22px; height:22px; background:#161b22; border-radius:6px; font-size:0.72rem; color:#818cf8; display:flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0; margin-top:2px; }
.tip-text { font-size:0.88rem; color:#94a3b8; line-height:1.65; }

/* ═══ CHAT DIVIDER ═══ */
.chat-sep { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; margin:2rem 0 1rem 0; display:flex; align-items:center; gap:10px; }
.chat-sep::before, .chat-sep::after { content:''; flex:1; height:1px; background:rgba(148,163,184,0.15); }

/* ═══ FILE UPLOADER ═══ */
[data-testid="stFileUploader"] { border-radius:13px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div class="law-logo">
<div class="law-logo-icon">⚖️</div>
<div>
<div class="law-logo-text">LawLytics</div>
<div class="law-logo-sub">Agentic AI · Legal Platform</div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Output Language</div>', unsafe_allow_html=True)
    selected_language = st.selectbox("", ["English", "Hindi", "Tamil", "Kannada"], label_visibility="collapsed")

    st.markdown('<div class="sidebar-label">AI Agent Pipeline</div>', unsafe_allow_html=True)

    # Fixed Mermaid — no indentation inside the mermaid div
    components.html("""<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({
startOnLoad: true,
theme: 'dark',
themeVariables: {
  primaryColor: '#1e293b',
  primaryTextColor: '#e2e8f0',
  primaryBorderColor: '#334155',
  lineColor: '#818cf8',
  secondaryColor: '#0f172a',
  background: '#090b14',
  nodeBorder: '#334155',
  clusterBkg: '#111827',
  titleColor: '#e2e8f0',
  edgeLabelBackground: '#1e293b',
  fontFamily: 'Inter, sans-serif'
}
});
</script>
<style>
body { margin:0; padding:6px 4px; background:#090b14; }
.mermaid svg { max-width:100%; }
</style>
</head>
<body>
<div class="mermaid">
graph TD
A([Start]) --> B[Preprocessing]
B --> C[Understanding]
C --> D[Simplification]
D --> E[Fairness Analysis]
E --> F[Risk Analysis]
F --> G[Risk Scoring]
G --> H[Decision Agent]
H --> I[Advisory Agent]
I --> J[Q&A Agent]
style A fill:#6366f1,stroke:#6366f1,color:#fff
style E fill:#b45309,stroke:#b45309,color:#fff
style G fill:#b91c1c,stroke:#b91c1c,color:#fff
style J fill:#065f46,stroke:#065f46,color:#fff
</div>
</body>
</html>""", height=540, scrolling=False)

    if st.session_state.analysis_data:
        st.markdown('<div class="sidebar-label">Session</div>', unsafe_allow_html=True)
        if st.button("↩ New Analysis", use_container_width=True):
            st.session_state.analysis_data = None
            st.session_state.document_text = ""
            st.session_state.messages = []
            st.rerun()

# ── GROQ KEY (backend — unchanged) ────────────────────────────────────────────
groq_key = "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"

# ── MAIN HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<h1>Legal Document Analyzer</h1>
<p>Upload a contract or agreement — the AI pipeline extracts, audits, and scores it instantly.</p>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD + PIPELINE ─────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Drop your legal PDF here", type="pdf")

if uploaded_file and not st.session_state.analysis_data:
    # ── BACKEND (unchanged) ──────────────────────────────────
    client = Groq(api_key=groq_key)
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted
    st.session_state.document_text = full_text
    # ── END BACKEND ──────────────────────────────────────────

    if st.button("⚡ Run AI Analysis Pipeline", use_container_width=True, type="primary"):
        with st.status("Running multi-stage reasoning engine…", expanded=True) as status:
            st.write("📄 Document Upload & Processing — done")
            time.sleep(0.4)
            st.write("🔍 Text Extraction & Cleaning — done")
            time.sleep(0.4)
            st.write("🧠 Legal reasoning & fairness check in progress (Groq)…")
            try:
                # ── BACKEND PROMPT (unchanged) ──────────────────────────
                sys_prompt = f"""You are a multi-agent AI legal system.
Perform internal processing and output strictly a JSON object.
CRITICAL: All generated output text in the JSON MUST be written natively in {selected_language}, except for the severity levels.

Task Requirements:
1. Classification: Identify the type of legal document. IF the text is empty OR is NOT a legal document/contract/policy (e.g. recipe, random text), you MUST classify it as 'Non-Legal Document / Unreadable', return an empty array for risk_audit [], and set risk_score to 0. DO NOT hallucinate risks.
2. Simplification: Provide a concise summary (or note it's not a legal doc).
3. Fairness Analysis & Risk Audit: Identify critical risks, strongly checking for one-sided clauses.
4. Risk Score: Overall risk score 0-100 (100 = extremely bad/risky).
5. Advisory: Provide worst-case scenario & negotiation tips.

Output JSON Schema:
{{
  "classification": "string naturally written in {selected_language}",
  "simplification": "string naturally written in {selected_language}",
  "fairness_insights": "string explicitly identifying the victim (e.g., 'This document aggressively risks the Wife by favoring the Husband')",
  "party_at_risk": "string identifying who is primarily disadvantaged (e.g. 'The Wife', 'The Tenant', 'The Employer', or 'Mutual')",
  "risk_score": 0,
  "risk_audit": [
     {{"severity": "Strictly ONLY 'High', 'Medium', or 'Low' in ENGLISH", "finding": "string naturally written in {selected_language}"}}
  ],
  "advisory": {{"worst_case": "string naturally written in {selected_language}", "negotiation_tips": ["string", "string"]}}
}}"""
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"Document Text:\n{full_text[:15000]}"}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                response_content = completion.choices[0].message.content
                st.session_state.analysis_data = json.loads(response_content)
                status.update(label="Analysis complete ✓", state="complete", expanded=False)
                st.rerun()
                # ── END BACKEND ──────────────────────────────────────────

            except Exception as e:
                error_str = str(e)
                if "Failed to generate JSON" in error_str or "max completion tokens" in error_str:
                    msg = "⚠️ Invalid Document Type: The AI could not analyse this file. Please upload a valid legal document (contract, agreement, policy, etc.)."
                else:
                    msg = f"⚠️ API Error: {error_str}"
                status.update(label="Processing failed", state="error", expanded=True)
                st.error(msg)

# ── RESULTS DASHBOARD ─────────────────────────────────────────────────────────
if st.session_state.analysis_data:
    data = st.session_state.analysis_data

    # ── Score helpers (logic unchanged) ─────────────────────────────────────
    score = data.get('risk_score', 0)
    score_color   = "#10b981" if score < 40 else "#f59e0b" if score < 75 else "#ef4444"
    badge_class   = "badge-safe" if score < 40 else "badge-moderate" if score < 75 else "badge-risky"
    decision_text = "Safe to Proceed" if score < 40 else "Moderate Risk" if score < 75 else "Highly Risky"

    if score < 40:
        case_strength = ("**Strong Case Strength**: This document is well-balanced. In a dispute, "
                     "a court would likely view the terms as fair and mutual. Minimal hidden liabilities.")
    elif score < 75:
        case_strength = ("**Moderate Case Strength**: There are some one-sided aspects. In a dispute, "
                     "ambiguities might be interpreted against the drafting party, but key clauses remain enforceable. "
                     "Renegotiating highlighted risks is advised before signing.")
    else:
        case_strength = ("**Weak Case Strength (Dispute Warning)**: Highly skewed terms detected. Courts in many jurisdictions "
                     "might strike down such aggressively one-sided clauses (unconscionability), but engaging in a dispute "
                     "would be costly. Strong recommendation to halt and renegotiate.")
    # ── End score helpers ────────────────────────────────────────────────────

    # Classification tag
    st.markdown(f'<div class="doc-class-tag">📂 {data.get("classification","Unknown Document")}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Risk Overview", "Deep Analysis", "Strategy & Advisory"])

    # ════════════════ TAB 1 — RISK OVERVIEW ════════════════
    with tab1:
        col_score, col_risks = st.columns([1, 1.65], gap="large")

        with col_score:
            st.markdown(f"""
<div class="risk-card">
<div class="risk-card-label">Overall Risk Score</div>
<div class="risk-score-num" style="color:{score_color};">{score}<span class="risk-score-denom">/100</span></div>
<div class="risk-badge {badge_class}">{decision_text}</div>
<div class="party-tag">Risk primarily affects: <strong>{data.get('party_at_risk','—')}</strong></div>
<div class="gauge-track">
<div class="gauge-fill" style="width:{score}%; background:{score_color};"></div>
</div>
</div>
""", unsafe_allow_html=True)

        with col_risks:
            st.markdown('<div class="tsec">🚩 Risk Findings</div>', unsafe_allow_html=True)
            risks = data.get('risk_audit', [])
            if not risks:
                st.success("No significant risks detected. The document appears balanced.")
            else:
                rows_html = ""
                for risk in risks:
                    sev = str(risk.get('severity', 'Low')).capitalize()
                    sev_cls = f"sev-{sev.lower()}" if sev in ['High','Medium','Low'] else "sev-low"
                    rows_html += f'<div class="risk-row"><span class="sev-pill {sev_cls}">{sev}</span><span class="risk-text">{risk.get("finding","")}</span></div>'
                st.markdown(f'<div class="risk-rows-wrap">{rows_html}</div>', unsafe_allow_html=True)

    # ════════════════ TAB 2 — DEEP ANALYSIS ════════════════
    with tab2:
        st.markdown('<div class="tsec">📝 Plain-Language Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card">{data.get("simplification","No summary available.")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="tsec" style="margin-top:24px;">⚖️ Fairness & Bias Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card info-card-green">{data.get("fairness_insights","No insights available.")}</div>', unsafe_allow_html=True)

        flagged = [r for r in data.get('risk_audit', []) if r.get('severity') in ['High', 'Medium']]
        if flagged:
            st.markdown('<div class="tsec" style="margin-top:24px;">🔍 Flagged Clauses</div>', unsafe_allow_html=True)
            for idx, risk in enumerate(flagged):
                st.markdown(f'<div class="clause-chip"><div class="clause-num">CLAUSE FLAG {idx+1}</div>{risk.get("finding","")}</div>', unsafe_allow_html=True)

    # ════════════════ TAB 3 — STRATEGY ════════════════
    with tab3:
        adv  = data.get('advisory', {})
        tips = adv.get('negotiation_tips', [])
        tips_html = "".join([f'<div class="tip-item"><div class="tip-num">{i+1}</div><div class="tip-text">{tip}</div></div>' for i, tip in enumerate(tips)])

        st.markdown(f"""
<div class="advisory-card">
<h2>🤖 Strategic Advisory &nbsp;·&nbsp; <span style="color:#475569;font-weight:400;font-size:0.85em;">Dispute Mode</span></h2>
<div class="adv-label">🚨 Worst-Case Scenario</div>
<div class="adv-body">{adv.get('worst_case','N/A')}</div>
<hr class="adv-divider"/>
<div class="adv-label">⚖️ Case Strength Assessment</div>
<div class="adv-body">{case_strength}</div>
<hr class="adv-divider"/>
<div class="adv-label">💡 Negotiation Suggestions</div>
{tips_html}
</div>
""", unsafe_allow_html=True)

    # ════════════════ Q&A CHAT (backend unchanged) ════════════════
    st.markdown('<div class="chat-sep">Q&A Chat Agent</div>', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about the document…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                chat_client = Groq(api_key=groq_key)
                context_text = st.session_state.document_text[:10000]
                chat_context = [
                    {"role": "system", "content": f"You are a legal AI assistant holding a Q&A session about the following document. You MUST reply natively in {selected_language}.\nDocument Context:\n{context_text}"}
                ]
                for msg in st.session_state.messages[-10:]:
                    chat_context.append(msg)
                chat_completion = chat_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=chat_context,
                    temperature=0.3
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Chat Exception: {e}")