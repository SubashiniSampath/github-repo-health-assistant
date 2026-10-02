import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))

from fastapi import FastAPI
from extract import get_repo_info, get_commits, get_issues, get_contributors
from transform import build_health_scorecard
from client import ask_question

app = FastAPI(title="GitHub Repo Health API")

@app.get("/")
def home():
    """A simple welcome message, so visiting the base URL shows something useful"""
    return {"message": "Welcome to the GitHub Repo Health API. Try /repo-health?owner=psf&repo=requests"}


@app.get("/repo-health")
def repo_health(owner: str, repo: str):
    """Returns the full health scorecard for a given GitHub repo"""
    try:
        repo_info = get_repo_info(owner, repo)
        commits = get_commits(owner, repo)
        issues = get_issues(owner, repo)
        contributors = get_contributors(owner, repo)

        scorecard = build_health_scorecard(repo_info, commits, issues, contributors)
        return scorecard
    except ValueError as e:
            return {"error": str(e)}

@app.get("/ask")
async def ask(question: str):
    """Ask a natural language question about a GitHub repo, answered using Gemini + MCP tools"""
    answer = await ask_question(question)
    return {"question": question, "answer": answer}