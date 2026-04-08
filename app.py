import streamlit as st
import PyPDF2
from groq import Groq
import json
import time
import streamlit.components.v1 as components

# --- CONFIG AND STATE ---
st.set_page_config(page_title="LawLytics", page_icon="⚖️", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    selected_language = st.selectbox("🌐 AI Output Language", ["English", "Hindi", "Tamil", "Kannada"])
    with st.expander('🛠️ AI Agent Architecture'):
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({ startOnLoad: true });
            </script>
        </head>
        <body style="background-color: transparent; margin: 0; padding: 0;">
            <div class="mermaid" style="display: flex; justify-content: center; align-items: flex-start; font-family: sans-serif; padding-top: 10px;">
        graph TD
            Start --> Step0[Step 0: Preprocessing]
            Step0 --> Step1[Step 1: Understanding]
            Step1 --> Step2[Step 2: Simplification]
            Step2 --> Step2A[Step 2A: Fairness Analysis]
            Step2A --> Step3[Step 3: Risk Analysis]
            Step3 --> Step4[Step 4: Risk Scoring]
            Step4 --> Step5[Step 5: Decision Agent]
            Step5 --> Step6[Step 6: Advisory Agent]
            Step6 --> Step7[Step 7: Q&A Agent]
            
            style Step2A fill:#ffcc00,stroke:#333
            style Step4 fill:#ff4b4b,stroke:#333
            </div>
        </body>
        </html>
        """, height=600, scrolling=True)

# Hardcoded Groq Key
groq_key = "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"

# Inline Styling - Premium UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
/* Custom Container & Glassmorphism */
.metric-container { 
    background: rgba(255, 255, 255, 0.7); 
    padding: 30px; 
    border-radius: 20px; 
    box-shadow: 0 8px 32px rgba(15, 23, 42, 0.05); 
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.5); 
    text-align: center; 
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(15, 23, 42, 0.1);
}

/* Beautiful Status Badges */
.badge-safe { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: 800; font-size: 1rem; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }
.badge-moderate { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: 800; font-size: 1rem; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); }
.badge-risky { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: 800; font-size: 1rem; box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3); }

/* Score Typography */
.score-value { font-size: 4.5rem; font-weight: 900; line-height: 1; margin: 10px 0; }
.color-safe { color: #10b981; }
.color-moderate { color: #f59e0b; }
.color-risky { color: #ef4444; }

/* Risk Audit Tags */
.severity-high { background-color: #fef2f2; color: #991b1b; padding: 4px 10px; border-radius: 8px; font-weight: 700; display: inline-block; font-size: 0.8em; border: 1px solid #fecaca; margin-right: 8px; }
.severity-medium { background-color: #fffbeb; color: #b45309; padding: 4px 10px; border-radius: 8px; font-weight: 700; display: inline-block; font-size: 0.8em; border: 1px solid #fde68a; margin-right: 8px;}
.severity-low { background-color: #ecfdf5; color: #065f46; padding: 4px 10px; border-radius: 8px; font-weight: 700; display: inline-block; font-size: 0.8em; border: 1px solid #a7f3d0; margin-right: 8px;}

/* Agent Boxes */
.agent-box { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; padding: 30px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); border: 1px solid #334155; height: 100%; }
.agent-box h3 { color: #38bdf8 !important; margin-top: 0; font-weight: 800; letter-spacing: -0.5px; }
.agent-box .glow-text { color: #818cf8; font-weight: 600; }
.agent-box ul { margin-top: 15px; background: rgba(255,255,255,0.03); border-radius: 12px; padding: 20px 20px 20px 40px; border: 1px solid rgba(255,255,255,0.05); }
.agent-box li { margin-bottom: 12px; font-weight: 400; line-height: 1.7; color: #cbd5e1; }
.agent-box li::marker { color: #38bdf8; }

/* Custom Progress Bar for Risk */
.gauge-bg { width: 100%; height: 20px; background-color: #e2e8f0; border-radius: 10px; overflow: hidden; margin-top: 15px; position: relative; }
.gauge-fill { height: 100%; border-radius: 10px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
</style>
""", unsafe_allow_html=True)

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MAIN APP ---
col_title, col_logo = st.columns([8, 1])
with col_title:
    st.title("⚖️ LawLytics | Agentic AI Legal Platform")
    st.caption("Advanced NLP processing. Upload a contract for high-speed multi-stage reasoning (Extraction, Auditing, Classification).")

uploaded_file = st.file_uploader("Upload Legal PDF", type="pdf")

if uploaded_file and not st.session_state.analysis_data:
    # Notice: Groq is initialized here
    client = Groq(api_key=groq_key)
    
    # Preprocessing (PyPDF2)
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted
    
    st.session_state.document_text = full_text

    if st.button("🚀 INITIATE AGENTIC AI PIPELINE", use_container_width=True, type="primary"):
        with st.status("Executing Multi-stage Reasoning Engine...", expanded=True) as status:
            st.write("📄 Document Upload & Processing [Complete]")
            time.sleep(0.4)
            st.write("🔍 Text Extraction & Cleaning [Complete]")
            time.sleep(0.4)
            st.write("⚖️ Legal Language Simplification & Fairness check running (Groq ultra-fast inference)...")
            try:
                # Multi-Agent Logic in Single LLM Call (JSON mode)
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
  "fairness_insights": "string explicitly identifying the victim (e.g., 'This document aggressively risks the Wife by favoring the Husband's rights')",
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
                status.update(label="Analysis Complete! Generating High-speed Output...", state="complete", expanded=False)
                st.rerun()

            except Exception as e:
                error_str = str(e)
                if "Failed to generate JSON" in error_str or "max completion tokens" in error_str:
                    msg = "⚠️ Invalid Document Type: The AI failed to generate a risk analysis. This usually happens if you upload non-legal documents (like class notes, recipes, or random text) that don't match standard contract structures. Please upload a valid legal agreement."
                else:
                    msg = f"⚠️ API Error: {error_str}"
                
                status.update(label="Processing Failed", state="error", expanded=True)
                st.error(msg)

# --- DASHBOARD & AGENTS ---
if st.session_state.analysis_data:
    data = st.session_state.analysis_data
    
    st.markdown("---")
    
    # 1. Header with Badge Document Classification
    col_class, col_space = st.columns([7, 3])
    with col_class:
        st.markdown(f"### 📂 Document Auto-Classification: <span style='color: #475569; font-weight: 600;'>{data.get('classification', 'Unknown')}</span>", unsafe_allow_html=True)
    
    # 2. Main Tabbed Interface
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Risk", "🔎 Deep Analysis & Clauses", "⚖️ Strategy & Case Strength"])
    
    score = data.get('risk_score', 0)
    score_class = "color-safe" if score < 40 else "color-moderate" if score < 75 else "color-risky"
    badge_class = "badge-safe" if score < 40 else "badge-moderate" if score < 75 else "badge-risky"
    decision_text = "SAFE TO PROCEED" if score < 40 else "MODERATE RISK" if score < 75 else "HIGHLY RISKY"
    gauge_color = "#10b981" if score < 40 else "#f59e0b" if score < 75 else "#ef4444"

    # Derive Case Strength
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

    with tab1:
        st.markdown("<br/>", unsafe_allow_html=True)
        rc1, rc2 = st.columns([1, 1.5])
        
        with rc1:
            st.markdown(f"""
<div class="metric-container">
<h4 style="margin-top:0; color:#64748b; font-weight:600; text-transform:uppercase; font-size:0.9rem;">Overall Risk Score</h4>
<div class="score-value {score_class}">{score}<span style="font-size:2rem; color:#cbd5e1;">/100</span></div>
<div class="{badge_class}">{decision_text}</div>
<div style="margin-top: 15px; color:#64748b; font-size:0.95rem; font-weight: 600;">Risk primarily affects: <span style="color:#0f172a;">{data.get('party_at_risk', 'Unknown/Mutual')}</span></div>
<div class="gauge-bg">
<div class="gauge-fill" style="width: {score}%; background-color: {gauge_color};"></div>
</div>
</div>
""", unsafe_allow_html=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🔄 Start New Session", use_container_width=True):
                st.session_state.analysis_data = None
                st.session_state.document_text = ""
                st.session_state.messages = []
                st.rerun()

        with rc2:
            st.markdown("<h4 style='margin-bottom: 20px;'>🚩 High-Priority Risk Detection</h4>", unsafe_allow_html=True)
            risks = data.get('risk_audit', [])
            if not risks:
                st.success("No significant risks detected. The document appears balanced.")
            else:
                for risk in risks:
                    sev = str(risk.get('severity', 'Low')).capitalize()
                    sev_class = f"severity-{sev.lower()}" if sev in ['High', 'Medium', 'Low'] else "severity-low"
                    finding = risk.get("finding", "")
                    
                    st.markdown(f"""
<div style="background: white; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #f1f5f9; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
<span class="{sev_class}">{sev.upper()} RISK</span>
<span style="color: #334155; font-size: 0.95rem;">{finding}</span>
</div>
""", unsafe_allow_html=True)

    with tab2:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("### 📝 Legal Language Simplification")
        st.info(data.get('simplification', 'No summary provided.'))
        
        st.markdown("---")
        st.markdown("### ⚖️ Fairness & Bias Analysis")
        st.success(data.get('fairness_insights', 'No fairness insights provided.'))

        st.markdown("---")
        st.markdown("### 🔍 Extracted Clause Highlights")
        st.caption("Clauses flagged by the Risk Agent for review:")
        for idx, risk in enumerate(data.get('risk_audit', [])):
            if risk.get('severity') in ['High', 'Medium']:
                st.markdown(f"**Clause Flag {idx+1}**: {risk.get('finding')}")
            
    with tab3:
        st.markdown("<br/>", unsafe_allow_html=True)
        adv = data.get('advisory', {})
        tips_html = "".join([f"<li>{tip}</li>" for tip in adv.get('negotiation_tips', [])])
        
        st.markdown(f"""
<div class="agent-box">
<h3>🤖 Strategic Advisory Agent \\ <span style="font-size: 0.7em; color: #94a3b8;">DISPUTE MODE</span></h3>
<p style="font-size:1.1em; line-height: 1.6; margin-top: 25px;">
<span class="glow-text">🚨 Worst-Case Scenario:</span><br/> 
<span style="color:#e2e8f0;">{adv.get('worst_case', 'N/A')}</span>
</p>
<p style="font-size:1.1em; line-height: 1.6; margin-top: 20px;">
<span class="glow-text">⚖️ Case Strength:</span><br/> 
<span style="color:#e2e8f0;">{case_strength}</span>
</p>
<p style="font-size:1.1em; margin-top:25px; margin-bottom:10px;">
<span class="glow-text">💡 Actionable Negotiation Suggestions:</span>
</p>
<ul>
{tips_html}
</ul>
</div>
""", unsafe_allow_html=True)



    # --- Q&A CHAT INTERFACE ---
    st.markdown("---")
    st.subheader("💬 Q&A Chat Agent")
    st.caption("Ask specific questions about the processed document.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about the document..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                chat_client = Groq(api_key=groq_key)
                # Keep lightweight context up to 10k chars
                context_text = st.session_state.document_text[:10000]
                
                chat_context = [
                    {"role": "system", "content": f"You are a legal AI assistant holding a Q&A session about the following document. You MUST reply natively in {selected_language}.\nDocument Context:\n{context_text}"}
                ]
                # Pass larger recent history for better memory recall (last 10 turns)
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