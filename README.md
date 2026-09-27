# 🧭 Portfolio & Gig Mentor

An AI mentor, built with **CrewAI** + **Groq** (`openai/gpt-oss-120b`) + **Streamlit**,
that helps freelancers:

- 💬 Chat with a career mentor about portfolios, gigs, and pricing
- 📄 Get an uploaded portfolio/resume reviewed (PDF, DOCX, TXT)
- 🧱 Draft portfolio website copy + structure from their real skills/projects
- 💼 Write Fiverr/Upwork gig titles, descriptions, tags, and pricing tiers
- 🔍 Check current market facts (rates, trends, platform norms) via live
  DuckDuckGo search, instead of the model guessing

A dedicated **Researcher agent** with a DuckDuckGo search tool feeds sourced,
current findings to the other agents, and every agent is instructed never to
invent clients, stats, or reviews that weren't given to it or found through
search.

---

## 1. Project structure

```
portfolio-mentor-ai/
├── app.py                  # Streamlit UI — all 5 tabs live here
├── agents.py                # CrewAI Agent definitions (Researcher, Reviewer,
│                             #   Builder, Gig Strategist, Mentor)
├── tasks.py                  # Task descriptions/prompts for each feature
├── crew_setup.py             # Wires agents+tasks into Crews, one fn per feature
├── tools/
│   ├── __init__.py
│   └── duckduckgo_tool.py    # Custom CrewAI tool wrapping duckduckgo_search
├── utils/
│   ├── __init__.py
│   └── file_parser.py        # Extracts text from uploaded PDF/DOCX/TXT
├── .streamlit/
│   └── config.toml           # Dark theme colors
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 2. Prerequisites

- Python 3.10–3.12
- A free **Groq API key** → https://console.groq.com/keys
- A GitHub account (for deployment)

---

## 3. Run it locally

```bash
# 1. Get the code into a folder called portfolio-mentor-ai, then:
cd portfolio-mentor-ai

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# then open .env and paste your real GROQ_API_KEY

# 5. Run the app
streamlit run app.py
```

It opens at `http://localhost:8501`. You can also paste the key directly
into the sidebar in the UI instead of using `.env` — either works.

---

## 4. Push it to GitHub

```bash
cd portfolio-mentor-ai
git init
git add .
git commit -m "Initial commit: Portfolio & Gig Mentor"
git branch -M main
git remote add origin https://github.com/<your-username>/portfolio-mentor-ai.git
git push -u origin main
```

`.env` is already in `.gitignore` — your API key will **not** be pushed.

---

## 5. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **"New app"** → pick the `portfolio-mentor-ai` repo → branch `main`
   → main file path `app.py`.
3. Before/after deploying, open **Settings → Secrets** and add:
   ```toml
   GROQ_API_KEY = "your_real_groq_api_key"
   ```
   This makes `os.getenv("GROQ_API_KEY")` work as the sidebar's default —
   users can still override it with their own key in the UI.
4. Click **Deploy**. First build takes a few minutes (installing CrewAI +
   dependencies).

Your app will be live at a `https://<something>.streamlit.app` URL you can
share on LinkedIn, or link to from the Fiverr/Upwork profiles it helps
people build.

---

## 6. How the "no fabrication" behavior works

- The **Researcher** agent is the only one with the DuckDuckGo tool. It runs
  first in every crew and produces a short, sourced briefing.
- Every other agent's `backstory` includes an explicit instruction never to
  invent statistics, clients, testimonials, or achievements, and to say
  "I don't know / this couldn't be verified" instead of guessing.
- Task prompts for the Reviewer/Builder/Gig Strategist explicitly say to use
  **only** what the user provided for their own portfolio/projects, and to
  flag unrealistic pricing/turnaround rather than rubber-stamping it.
- If a DuckDuckGo search fails or returns nothing, the tool itself returns a
  message telling the agent not to fill the gap with a guess.

This reduces hallucination but doesn't eliminate it completely — treat AI
output as a strong first draft, not a final answer, especially for numbers.

---

## 7. Troubleshooting

**`GroqException: is_litellm is unsupported` or similar LLM errors**
Some CrewAI/LiteLLM version combinations choke on extra kwargs passed to the
`LLM(...)` call (e.g. `reasoning_effort`, `top_p`, `stop`). `crew_setup.py`
keeps the config to just `model`, `api_key`, `temperature`, and `max_retries`
on purpose. If you still hit this:
- Confirm you're on the pinned versions in `requirements.txt`.
- Try upgrading `crewai` to the latest release (`pip install -U crewai`) —
  Groq support has been actively improving.

**`ModuleNotFoundError: duckduckgo_search`**
Run `pip install -r requirements.txt` again inside your active virtual
environment — it's easy to accidentally install into the wrong Python.

**Search results look empty or search is slow**
DuckDuckGo's free search endpoint is sometimes rate-limited. The tool is
written to fail gracefully (tells the agent not to guess) rather than
crashing the app — just retry after a few seconds.

**PDF upload says "no extractable text found"**
That PDF is likely scanned images rather than real text. For now, ask the
user to upload a text-based PDF/DOCX, or add an OCR step (e.g.
`pytesseract`) to `utils/file_parser.py` if you need that.

---

## 8. Ideas for extending this

- Add an OCR fallback for scanned/image resumes.
- Add a "Design mood board" tab that fetches reference images for the
  user's field via an image search API.
- Persist chat history per user with a lightweight database instead of
  `st.session_state` (which resets on refresh).
- Swap the Researcher's tool for a paid search API (e.g. Serper, Tavily) if
  you outgrow DuckDuckGo's free rate limits.
- Add a "compare two gig drafts" mode using CrewAI's `Process.hierarchical`
  with a manager agent picking the stronger draft.
