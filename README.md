**GitHub Repo Health Assistant**

Ask natural-language questions about any public GitHub repo — is it actively maintained, how much activity has it seen recently, how fast are issues getting resolved — and get real, data-backed answers powered by an LLM.

🔗 **Live demo:** [Try it here](https://github-repo-health-api.onrender.com/)
📂 **Repo:**.     github.com/SubashiniSampath/github-repo-health-assistant

<img width="1092" height="1120" alt="image" src="https://github.com/user-attachments/assets/95ca4abf-feb5-4ed3-bf52-fc09c80893ce" />


**What it does**

Point it at any public GitHub repo (owner + repo name) and it fetches live data — commits, issues, contributors — and either shows a quick health scorecard, or answers a specific question about it in plain English ("how many commits in the last 2 weeks?", "are issues getting resolved quickly?").

Under the hood, an LLM (Gemini) decides which data to fetch and how to interpret it, using a set of tools exposed through MCP (Model Context Protocol) — rather than a hardcoded set of canned responses.

**Tech stack**

ETL pipeline — Python, GitHub REST API, pagination handling
MCP (Model Context Protocol) — exposes the ETL pipeline as tools an LLM can call
LLM — Google Gemini, via an agentic tool-calling loop (supports multiple tool calls per question)
API — FastAPI, with a simple HTML/JS frontend
Deployment — Render

**Architecture**

User question
    │
    ▼
FastAPI (/ask endpoint)
    │
    ▼
Gemini ──(decides which tool to call)──▶ MCP Server
    │                                         │
    │◀───────────(tool result)────────────────┘
    │
    ▼
Gemini may call another tool, or
return a final natural-language answer
    │
    ▼
Response shown to user

Each MCP tool (get_repo_health, get_commit_activity, compare_repos) wraps the ETL pipeline: Extract (pull raw data from GitHub's API, with pagination) → Transform (turn it into clean metrics — commit activity, issue ratios, etc.).

**API endpoints**
Endpoint	Description	Example:

GET /	Frontend UI	/
GET /repo-health	Full health scorecard for a repo	/repo-health?owner=facebook&repo=react
GET /ask	Natural-language Q&A, powered by Gemini + MCP	/ask?question=is facebook/react actively maintained?
GET /docs	Auto-generated interactive API docs (Swagger UI)	/docs


**Running it locally**

**1. Clone and install dependencies**

bash
git clone https://github.com/SubashiniSampath/github-repo-health-assistant.git
cd github-repo-health-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

**2. Add your API keys**

Create a .env file in the project root:

GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key
GitHub token: github.com/settings/tokens (needs public_repo scope)
Gemini key: free at aistudio.google.com

**3. Run the API**

bash
uvicorn src.api.main:app --reload

Visit http://127.0.0.1:8000

**License**

MIT
