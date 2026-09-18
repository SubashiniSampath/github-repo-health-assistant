import sys
import os

# Let this file find your etl functions, which live in a different folder
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))

from mcp.server.fastmcp import FastMCP
from extract import get_repo_info, get_commits, get_issues, get_contributors
from transform import build_health_scorecard, commits_in_last_n_days

# Create the MCP server, give it a name
mcp = FastMCP("github-repo-health")


@mcp.tool()
def get_repo_health(owner: str, repo: str) -> dict:
    """
    Get the full health scorecard for a GitHub repo — stars, recent commit
    activity, issue open/closed ratio, average time to close issues, and
    contributor count. Use this for general 'is this repo healthy/active'
    questions.
    """
    repo_info = get_repo_info(owner, repo)
    commits = get_commits(owner, repo)
    issues = get_issues(owner, repo)
    contributors = get_contributors(owner, repo)

    return build_health_scorecard(repo_info, commits, issues, contributors)


@mcp.tool()
def get_commit_activity(owner: str, repo: str, days: int) -> dict:
    """
    Get the exact number of commits in a specific, custom time window
    (in days). Use this whenever the user asks about a specific number of
    days, weeks, or months (convert weeks/months to days first) — instead
    of relying on the default 6-month figure from get_repo_health.
    """
    commits = get_commits(owner, repo)
    count = commits_in_last_n_days(commits, days)

    return {
        "repo_name": f"{owner}/{repo}",
        "days_requested": days,
        "commit_count": count
    }


@mcp.tool()
def compare_repos(owner1: str, repo1: str, owner2: str, repo2: str) -> dict:
    """
    Get health scorecards for two repos side by side, so they can be
    compared against each other.
    """
    scorecard1 = get_repo_health(owner1, repo1)
    scorecard2 = get_repo_health(owner2, repo2)

    return {
        "repo_1": scorecard1,
        "repo_2": scorecard2
    }


# This starts the server when you run this file directly
if __name__ == "__main__":
    
    mcp.run()
    