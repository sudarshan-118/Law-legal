import streamlit as st
import PyPDF2
from groq import Groq
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

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
.page-header { margin-bottom:2rem; padding-bottom:1.5rem; border-bottom:1px solid rgba(148,163,184,0.15); text-align:center; padding-top: 1rem; }
.page-header h1 { 
    font-size:3.2rem; 
    font-weight:900; 
    letter-spacing:-1px; 
    margin:0 0 8px 0; 
    background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 30px rgba(129, 140, 248, 0.25);
}
.page-header h2 { font-size:1.4rem; font-weight:600; color:#475569; margin:0 0 10px 0; letter-spacing:-0.2px; }
.page-header p { font-size:1.05rem; color:#94a3b8; margin:0; font-weight:500; text-transform:uppercase; letter-spacing:0.05em; }

/* primary button */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; font-size:0.92rem !important;
    padding:0.7rem 1.4rem !important; box-shadow:0 4px 14px rgba(99,102,241,0.35) !important;
    transition:all 0.2s ease !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover { transform:translateY(-1px); box-shadow:0 8px 22px rgba(99,102,241,0.45) !important; }

/* ═══ VERDICT BANNER ═══ */
.verdict-banner {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}
.verdict-title { font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; color: #64748b; margin-bottom: 8px; }
.verdict-item { display: flex; flex-direction: column; gap: 4px; }
.verdict-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; }
.verdict-value { font-size: 1.1rem; font-weight: 700; color: #f8fafc; }
.verdict-high { color: #fca5a5; }
.verdict-medium { color: #fbbf24; }
.verdict-low { color: #6ee7b7; }

/* classification tag */
.doc-class-tag { display:inline-flex; align-items:center; justify-content:center; gap:8px; background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.3); color:#818cf8; border-radius:8px; padding:6px 16px; font-weight:600; font-size:0.85rem; margin-bottom:1.5rem; width: 100%; text-align: center; }

/* tabs */
[data-testid="stTabs"] [role="tab"] { font-size:0.83rem !important; font-weight:600 !important; padding:10px 18px !important; border-radius:0 !important; border-bottom:2px solid transparent !important; transition:all 0.2s; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color:#818cf8 !important; border-bottom:2px solid #818cf8 !important; background:transparent !important; }

/* ═══ RISK CARD — dark always ═══ */
.risk-card { background:#0d1117; border:1px solid #21262d; border-radius:18px; padding:28px 24px; box-shadow:0 2px 20px rgba(0,0,0,0.4); text-align:center; display: flex; flex-direction: column; justify-content: center; }
.risk-card-label { font-size:0.69rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#4b5563; margin-bottom:10px; }
.risk-score-num { font-size:4.5rem; font-weight:900; line-height:1; font-family:'JetBrains Mono',monospace; margin-bottom:4px; }
.risk-score-denom { font-size:1.3rem; font-weight:400; color:#374151; }
.risk-badge { display:inline-block; border-radius:999px; padding:5px 18px; font-size:0.77rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin:14px 0 12px 0; }
.badge-safe     { background:#064e3b; color:#6ee7b7; border:1px solid #065f46; }
.badge-moderate { background:#451a03; color:#fbbf24; border:1px solid #78350f; }
.badge-risky    { background:#450a0a; color:#fca5a5; border:1px solid #7f1d1d; }
.party-tag { font-size:0.75rem; color:#64748b; margin-bottom:12px; font-weight:500; }
.party-tag strong { color:#e2e8f0; }

.gauge-track { width:100%; height:7px; background:#161b22; border-radius:999px; overflow:hidden; margin-bottom: 20px; }
.gauge-fill  { height:100%; border-radius:999px; transition:width 0.8s cubic-bezier(0.4,0,0.2,1); }

.risk-reasons-box { background: #161b22; border-radius: 12px; padding: 16px; text-align: left; border: 1px solid #30363d; margin-top: auto; }
.risk-reason-title { font-size: 0.75rem; font-weight: 700; color: #818cf8; margin-bottom: 8px; text-transform: uppercase; }
.risk-reason-list { margin: 0; padding-left: 18px; font-size: 0.85rem; color: #c9d1d9; line-height: 1.5; }

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
.tsec { font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#475569; margin:24px 0 12px 0; border-bottom: 1px solid rgba(148,163,184,0.15); padding-bottom: 8px; }
.tsec:first-child { margin-top:4px; }

/* ═══ INFO CARDS — adapts to theme ═══ */
.info-card { background:rgba(99,102,241,0.06); border-left:3px solid #6366f1; border-radius:0 12px 12px 0; padding:16px 20px; font-size:0.92rem; color:#94a3b8; line-height:1.7; border-top:1px solid rgba(99,102,241,0.1); border-right:1px solid rgba(99,102,241,0.1); border-bottom:1px solid rgba(99,102,241,0.1); }
.info-card-green { border-left-color:#10b981; border-top-color:rgba(16,185,129,0.1); border-right-color:rgba(16,185,129,0.1); border-bottom-color:rgba(16,185,129,0.1); background:rgba(16,185,129,0.06); }

/* ═══ CLAUSE CHIPS — dark ═══ */
.clause-chip { background:#1c1a0e; border:1px solid #3a3010; border-radius:10px; padding:14px 18px; font-size:0.9rem; color:#fde68a; margin-bottom:12px; line-height:1.6; }
.clause-num  { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#fbbf24; font-weight:700; margin-bottom:6px; display: inline-block; background: rgba(251,191,36,0.1); padding: 2px 8px; border-radius: 4px; }

/* ═══ ADVISORY CARD — always dark ═══ */
.advisory-card { background:#0d1117; border-radius:18px; padding:32px; color:#e2e8f0; border:1px solid #21262d; box-shadow:0 8px 32px rgba(0,0,0,0.4); }
.advisory-card h2 { font-size:1.1rem; font-weight:700; color:#a5b4fc; margin:0 0 26px 0; letter-spacing:-0.3px; }
.adv-label { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#818cf8; margin-bottom:10px; }
.adv-body  { font-size:0.92rem; line-height:1.7; color:#94a3b8; margin-bottom:26px; }
.adv-divider { border:none; border-top:1px solid #21262d; margin:26px 0; }
.tip-item { display:flex; align-items:flex-start; gap:12px; margin-bottom:16px; }
.tip-num  { width:24px; height:24px; background:#161b22; border-radius:6px; font-size:0.75rem; color:#818cf8; display:flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0; margin-top:2px; }
.tip-text { font-size:0.92rem; color:#94a3b8; line-height:1.6; }

/* ═══ CHAT DIVIDER ═══ */
.chat-sep { font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#64748b; margin:2.5rem 0 1.5rem 0; display:flex; align-items:center; gap:12px; }
.chat-sep::before, .chat-sep::after { content:''; flex:1; height:1px; background:rgba(148,163,184,0.15); }

/* ═══ FILE UPLOADER ═══ */
@keyframes floatIcon {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

@keyframes shimmerGlow {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

[data-testid="stFileUploader"] > section {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    border: 2px dashed rgba(99, 102, 241, 0.5) !important;
    border-radius: 20px !important;
    padding: 36px 24px !important;
    text-align: center !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    position: relative;
    overflow: hidden;
}

[data-testid="stFileUploader"] > section:hover {
    border-color: rgba(167, 139, 250, 0.9) !important;
    background: rgba(15, 23, 42, 0.7) !important;
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.25), inset 0 0 20px rgba(167, 139, 250, 0.1) !important;
    transform: scale(1.015);
}

[data-testid="stFileUploader"] > section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.08), transparent);
    background-size: 200% auto;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}
[data-testid="stFileUploader"] > section:hover::before {
    opacity: 1;
    animation: shimmerGlow 2.5s infinite linear;
}

[data-testid="stFileUploader"] svg {
    color: #818cf8 !important;
    width: 48px !important;
    height: 48px !important;
    margin-bottom: 16px;
    filter: drop-shadow(0 4px 6px rgba(99,102,241,0.4));
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"] > section:hover svg {
    color: #a78bfa !important;
    animation: floatIcon 2s ease-in-out infinite;
    filter: drop-shadow(0 8px 15px rgba(167,139,250,0.6));
}

[data-testid="stFileUploader"] span {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #f1f5f9 !important;
    letter-spacing: -0.3px;
    transition: color 0.3s ease;
}

[data-testid="stFileUploader"] > section:hover span {
    color: #fff !important;
}

[data-testid="stFileUploader"] small {
    font-size: 0.88rem !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

[data-testid="stFileUploader"] button {
    transition: transform 0.2s ease !important;
}
[data-testid="stFileUploader"] button:active {
    transform: scale(0.95) !important;
}
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

    if st.session_state.analysis_data:
        st.markdown('<div class="sidebar-label" style="margin-top: 30px;">Session Control</div>', unsafe_allow_html=True)
        if st.button("↩ Start New Analysis", use_container_width=True):
            st.session_state.analysis_data = None
            st.session_state.document_text = ""
            st.session_state.messages = []
            st.rerun()

# ── GROQ KEY (backend) ────────────────────────────────────────────────────────
groq_key = os.environ.get("GROQ_API_KEY", "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")

# ── MAIN HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
<h1>AI Legal Document Analyzer</h1>
<h2>Understand Risks, Bias & Legal Impact in Seconds</h2>
<p>Upload a contract → Get summary, risks & negotiation insights instantly</p>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD + PIPELINE ─────────────────────────────────────────────────────────
def clear_state():
    st.session_state.analysis_data = None
    st.session_state.document_text = ""
    st.session_state.messages = []

uploaded_file = st.file_uploader("Drop your legal PDF here", type="pdf", on_change=clear_state)

if uploaded_file and not st.session_state.analysis_data:
    client = Groq(api_key=groq_key)
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted
    st.session_state.document_text = full_text

    if st.button("⚡ Run AI Analysis Pipeline", use_container_width=True, type="primary"):
        with st.status("Analyzing legal document...", expanded=True) as status:
            st.write("📄 Document Upload & Processing — done")
            time.sleep(0.3)
            st.write("🔍 Text Extraction & Cleaning — done")
            time.sleep(0.3)
            st.write("🧠 Legal reasoning, risk scoring & fairness check running...")
            try:
                sys_prompt = f"""You are an elite AI legal document analyzer.
Perform internal processing and output strictly a JSON object.
CRITICAL: All generated output text in the JSON MUST be written natively in {selected_language}, except for the severity levels.

Task Requirements:
1. Classification: Identify the exact type of legal document. IF text is NOT a contract/policy, classify as 'Non-Legal Document / Unreadable' and set risk_score to 0.
2. Simplification: Provide a highly structured, easy-to-read summary of the key terms.
3. Fairness Analysis: Identify immediately who holds the power and who is disadvantaged. CRITICAL ALIGNMENT: Your `fairness_insights` MUST logically match the `party_at_risk`. If Party A is the `party_at_risk`, your `fairness_insights` must explicitly state that Party A is disadvantaged and Party B holds the power. Never contradict yourself.
4. Risk Audit: Extract critical risks and one-sided clauses.
5. Risk Metrics: Provide an overall risk score (0-100), a confidence score for your analysis (0-100), and 3 bullet points explaining EXACTLY why this risk score was given.
6. Advisory: Provide worst-case scenarios and highly actionable, professional recommended actions (e.g., 'Revise section X to mandate mutual notice', 'Balance financial liability clauses'). Do NOT be generic.

Output JSON Schema:
{{
  "classification": "string",
  "simplification": "string",
  "party_1_name": "string",
  "party_2_name": "string",
  "fairness_insights": "string",
  "party_at_risk": "string",
  "risk_score": 0,
  "confidence_score": 0,
  "risk_reasons": ["string", "string", "string"],
  "recommended_action": "High-level directive, e.g. 'Renegotiate Immediately' or 'Safe to Sign'",
  "risk_audit": [
     {{"severity": "Strictly ONLY 'High', 'Medium', or 'Low' in ENGLISH", "finding": "string"}}
  ],
  "advisory": {{"worst_case": "string", "negotiation_tips": ["string", "string"]}}
}}"""
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"Document Text:\n{full_text[:15000]}"}
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                response_content = completion.choices[0].message.content
                st.session_state.analysis_data = json.loads(response_content)
                status.update(label="Analysis complete ✓", state="complete", expanded=False)
                st.rerun()

            except Exception as e:
                error_str = str(e)
                if "Failed to generate JSON" in error_str or "max completion tokens" in error_str:
                    msg = "⚠️ Invalid Document Type: The AI could not analyse this file. Please upload a valid legal document."
                else:
                    msg = f"⚠️ API Error: {error_str}"
                status.update(label="Processing failed", state="error", expanded=True)
                st.error(msg)

# ── RESULTS DASHBOARD ─────────────────────────────────────────────────────────
if st.session_state.analysis_data:
    data = st.session_state.analysis_data

    score = data.get('risk_score', 0)
    score_color   = "#10b981" if score < 40 else "#fbbf24" if score < 75 else "#f87171"
    badge_class   = "badge-safe" if score < 40 else "badge-moderate" if score < 75 else "badge-risky"
    decision_text = "Safe to Proceed" if score < 40 else "Moderate Risk" if score < 75 else "Unsafe - High Risk"
    
    verdict_emoji = "🟢" if score < 40 else "🟠" if score < 75 else "🔴"
    risk_level_str = "LOW" if score < 40 else "MEDIUM" if score < 75 else "HIGH"
    
    # ── FINAL VERDICT BANNER ──
    st.markdown(f'<div class="doc-class-tag">📄 Document Auto-Classification: {data.get("classification","Unknown Document")}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="verdict-banner" style="margin-bottom: 1rem; align-items: flex-start; flex-direction: column;">
        <div class="verdict-title" style="margin-bottom: 12px; color: #818cf8; display: flex; align-items: center; gap: 8px;">
            <svg width="16" height="16" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
            Executive Summary
        </div>
        <div style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.6; font-weight: 500;">
            {data.get('simplification', 'No summary generated.')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="verdict-banner">
        <div>
            <div class="verdict-title">Final Verdict</div>
            <div style="font-size: 0.85rem; color: #cbd5e1; max-width: 500px;">Review the high-level decision below, then explore tabs for deep analysis.</div>
        </div>
        <div style="display: flex; gap: 40px; text-align: left;">
            <div class="verdict-item">
                <span class="verdict-label">Risk Level</span>
                <span class="verdict-value {'verdict-low' if score < 40 else 'verdict-medium' if score < 75 else 'verdict-high'}">{risk_level_str} {verdict_emoji}</span>
            </div>
            <div class="verdict-item">
                <span class="verdict-label">Affected Party</span>
                <span class="verdict-value">{data.get('party_at_risk', 'None')}</span>
            </div>
            <div class="verdict-item">
                <span class="verdict-label">Recommended Action</span>
                <span class="verdict-value">{data.get('recommended_action', 'Proceed with Caution')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Risk Overview", "Deep Analysis", "Strategy & Advisory"])

    # ════════════════ TAB 1 — RISK OVERVIEW ════════════════
    with tab1:
        col_score, col_risks = st.columns([1, 1.8], gap="large")

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
    <div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase;">Confidence Score: <span style="color: #f1f5f9;">{data.get('confidence_score', 90)}%</span></div>
</div>
""", unsafe_allow_html=True)

        with col_risks:
            st.markdown('<div class="tsec">🚩 Core Risk Findings</div>', unsafe_allow_html=True)
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
                
            reasons = data.get('risk_reasons', [])
            reasons_html = "".join([f"<li>{r}</li>" for r in reasons])
            st.markdown(f"""
<div class="risk-reasons-box" style="margin-top: 16px;">
    <div class="risk-reason-title">Why this score?</div>
    <ul class="risk-reason-list">
        {reasons_html}
    </ul>
</div>
""", unsafe_allow_html=True)

    # ════════════════ TAB 2 — DEEP ANALYSIS ════════════════
    with tab2:
        st.markdown('<div class="tsec">📝 Plain-Language Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card">{data.get("simplification","No summary available.")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="tsec">⚖️ Fairness & Bias Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-card info-card-green">{data.get("fairness_insights","No insights available.")}</div>', unsafe_allow_html=True)

        flagged = [r for r in data.get('risk_audit', []) if r.get('severity') in ['High', 'Medium']]
        if flagged:
            st.markdown('<div class="tsec">🔍 Directly Flagged Clauses</div>', unsafe_allow_html=True)
            for idx, risk in enumerate(flagged):
                st.markdown(f'<div class="clause-chip"><span class="clause-num">CLAUSE {idx+1}</span><br>{risk.get("finding","")}</div>', unsafe_allow_html=True)

    # ════════════════ TAB 3 — STRATEGY ════════════════
    with tab3:
        adv  = data.get('advisory', {})
        tips = adv.get('negotiation_tips', [])
        tips_html = "".join([f'<div class="tip-item"><div class="tip-num">{i+1}</div><div class="tip-text">{tip}</div></div>' for i, tip in enumerate(tips)])

        st.markdown(f"""
<div class="advisory-card">
<h2>🤖 Actionable Strategic Advisory</h2>
<div class="adv-label">🚨 Worst-Case Scenario</div>
<div class="adv-body">{adv.get('worst_case','N/A')}</div>
<hr class="adv-divider"/>
<div class="adv-label">💡 Recommended Remediation Actions</div>
{tips_html}
</div>
""", unsafe_allow_html=True)

    # ════════════════ Q&A CHAT ════════════════
    st.markdown('<div class="chat-sep">Q&A Chat Agent</div>', unsafe_allow_html=True)

    party1 = data.get("party_1_name", "Party 1")
    party2 = data.get("party_2_name", "Party 2")
    
    chat_roles = [
        "Lawyer / Legal Counsel",
        f"Party 1 ({party1})",
        f"Party 2 ({party2})",
        "Judge / Arbiter",
        "Third Party / Neutral Observer"
    ]
    st.markdown('<div class="adv-label" style="margin-bottom: 8px;">Select Your Persona / Perspective:</div>', unsafe_allow_html=True)
    selected_role = st.selectbox("Role", chat_roles, label_visibility="collapsed")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input('Ask anything (e.g., "Is this clause legally valid?")'):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                chat_client = Groq(api_key=groq_key)
                context_text = st.session_state.document_text[:10000]
                chat_context = [
                    {"role": "system", "content": f"You are a legal AI assistant holding a Q&A session about the following document. You MUST reply natively in {selected_language}. The user you are speaking to is acting in the role of: {selected_role}. Tailor your legal advice, tone, and perspective strictly to this role.\nDocument Context:\n{context_text}"}
                ]
                for msg in st.session_state.messages[-10:]:
                    chat_context.append(msg)
                chat_completion = chat_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=chat_context,
                    temperature=0.0
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Chat Exception: {e}")
