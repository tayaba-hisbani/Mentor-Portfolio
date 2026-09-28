"""
Portfolio & Gig Mentor — a Streamlit front end over a small CrewAI crew,
powered by Google Gemini, that helps freelancers build a
portfolio, get it reviewed, write Fiverr/Upwork gigs, and check current
market facts before making claims.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from crew_setup import (
    get_llm,
    run_portfolio_review,
    run_portfolio_builder,
    run_gig_creator,
    run_market_research,
    run_mentor_chat,
)
from utils import extract_text

load_dotenv()

st.set_page_config(
    page_title="Portfolio & Gig Mentor",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500&display=swap');

    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; }

    .hero {
        padding: 2rem 2rem 1.6rem 2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #7C3AED 0%, #4F46E5 55%, #0EA5E9 100%);
        color: white;
        margin-bottom: 1.6rem;
    }
    .hero h1 { margin: 0 0 .35rem 0; font-size: 2.1rem; }
    .hero p { margin: 0; opacity: 0.92; font-size: 1.02rem; }

    .card {
        background: #1A1D27;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
    }
    .result-box {
        background: #12141C;
        border-left: 3px solid #7C3AED;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🧭 Portfolio & Gig Mentor</h1>
        <p>Your AI mentor for building a standout freelance portfolio and
        writing gigs that actually convert — grounded in real, current
        market research, not guesswork.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Sidebar — API key & session state
# --------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def get_secret(name: str, default: str = "") -> str:
    """Reads from Streamlit secrets first, then falls back to environment variables."""
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


api_key = get_secret("GEMINI_API_KEY")
model_name = get_secret("GEMINI_MODEL", "gemini/gemini-3.1-flash-lite")

with st.sidebar:
    st.markdown("### ⚙️ Setup")
    if api_key:
        st.success("Gemini API key loaded from secrets.", icon="✅")
    else:
        st.error(
            "No Gemini API key found. Add `GEMINI_API_KEY` to "
            "`.streamlit/secrets.toml` (local) or your app's Settings → "
            "Secrets (Streamlit Cloud).",
            icon="🔑",
        )
    st.caption(f"Model: `{model_name}`")
    st.divider()
    st.markdown("### 📎 What this app does")
    st.caption(
        "- 💬 Chat with a career mentor\n"
        "- 📄 Get your portfolio/resume reviewed\n"
        "- 🧱 Draft portfolio website copy\n"
        "- 💼 Write Fiverr/Upwork gig content\n"
        "- 🔍 Check current market facts"
    )
    st.divider()
    if st.button("🗑️ Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

llm = get_llm(api_key, model_name) if api_key else None


def require_key():
    if not api_key:
        st.warning(
            "Add your Gemini API key to `.streamlit/secrets.toml` (or your "
            "deployed app's Secrets settings) to use this feature.",
            icon="🔑",
        )
        return False
    return True


# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_chat, tab_review, tab_builder, tab_gig, tab_research = st.tabs(
    ["💬 Mentor Chat", "📄 Portfolio Review", "🧱 Portfolio Builder", "💼 Gig Creator", "🔍 Market Research"]
)

# --- Mentor Chat ----------------------------------------------------------
with tab_chat:
    st.caption("Ask anything about portfolios, gigs, pricing, or getting started freelancing.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask your mentor...")
    if question:
        if require_key():
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            history_summary = "\n".join(
                f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-8:-1]
            )

            with st.chat_message("assistant"):
                with st.spinner("Thinking it through..."):
                    try:
                        reply = run_mentor_chat(llm, question, history_summary)
                    except Exception as exc:
                        reply = f"Something went wrong reaching the model: {exc}"
                st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

# --- Portfolio Review -------------------------------------------------------
with tab_review:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Get your portfolio or resume reviewed")
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader(
            "Upload your portfolio/resume (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt", "md"],
        )
        notes = st.text_area(
            "Anything specific you want feedback on? (optional)",
            placeholder="e.g. Not sure my project descriptions sound professional enough",
        )
    with col2:
        field = st.text_input("Your field / niche", placeholder="e.g. graphic design, web development")

    if st.button("Review my portfolio", type="primary", disabled=not uploaded):
        if require_key():
            with st.spinner("Reading your document and checking current portfolio standards..."):
                text = extract_text(uploaded)
                try:
                    result = run_portfolio_review(llm, text, field or "general freelancing", notes)
                except Exception as exc:
                    result = f"Something went wrong: {exc}"
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Portfolio Builder ------------------------------------------------------
with tab_builder:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧱 Build your portfolio content")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Your name / brand")
        b_field = st.text_input("Field / niche", key="builder_field")
        experience = st.text_input("Years of experience", placeholder="e.g. 2 years")
        tone = st.selectbox("Tone", ["Professional but approachable", "Bold & confident", "Warm & friendly", "Minimal & technical"])
    with c2:
        skills = st.text_area("Key skills (comma-separated)", placeholder="Figma, UI design, prototyping")
        target_clients = st.text_input("Who are you trying to attract?", placeholder="e.g. early-stage startups")
        projects_raw = st.text_area(
            "Real projects to feature (one per line)",
            placeholder="Redesigned checkout flow for an e-commerce app, reduced drop-off\nBuilt a landing page for a local bakery",
            height=110,
        )

    if st.button("Generate portfolio content", type="primary"):
        if require_key():
            profile = {
                "name": name,
                "field": b_field or "freelancing",
                "experience": experience,
                "skills": skills,
                "target_clients": target_clients,
                "tone": tone,
                "projects": [p.strip() for p in projects_raw.splitlines() if p.strip()],
            }
            with st.spinner("Researching current portfolio conventions and drafting your content..."):
                try:
                    result = run_portfolio_builder(llm, profile)
                except Exception as exc:
                    result = f"Something went wrong: {exc}"
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Gig Creator -------------------------------------------------------------
with tab_gig:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💼 Write your gig")
    c1, c2 = st.columns(2)
    with c1:
        platform = st.selectbox("Platform", ["Fiverr", "Upwork", "LinkedIn Services"])
        service = st.text_input("Service you offer", placeholder="e.g. logo design, WordPress site setup")
        level = st.selectbox("Your skill level", ["Beginner", "Intermediate", "Advanced / Expert"])
    with c2:
        turnaround = st.text_input("Realistic turnaround time", placeholder="e.g. 3 days")
        budget = st.text_input("Rough pricing comfort", placeholder="e.g. $25-75 per project")

    if st.button("Generate gig content", type="primary", disabled=not service):
        if require_key():
            gig_profile = {
                "platform": platform,
                "service": service,
                "level": level,
                "turnaround": turnaround,
                "budget": budget,
            }
            with st.spinner(f"Checking current {platform} norms and drafting your gig..."):
                try:
                    result = run_gig_creator(llm, gig_profile)
                except Exception as exc:
                    result = f"Something went wrong: {exc}"
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Market Research ----------------------------------------------------------
with tab_research:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 Check a current market fact")
    st.caption("e.g. \"average Upwork rate for beginner video editors\" or \"is AI content writing still in demand on Fiverr\"")
    query = st.text_input("What do you want to check?")
    r_field = st.text_input("Field (optional, sharpens the search)", key="research_field")

    if st.button("Research this", type="primary", disabled=not query):
        if require_key():
            with st.spinner("Searching..."):
                try:
                    result = run_market_research(llm, query, r_field)
                except Exception as exc:
                    result = f"Something went wrong: {exc}"
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
