import sys
import os

# Let this file find your etl functions, which live in a different folder
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))

from mcp.server.fastmcp import FastMCP
from extract import get_repo_info, get_commits, get_issues, get_contributors
from transform import build_health_scorecard, commits_in_last_n_days, issues_in_last_n_days

# Create the MCP server, give it a name
mcp = FastMCP("github-repo-health")


@mcp.tool()
def get_repo_health(owner: str, repo: str) -> dict:
    """
    Get the full health scorecard for a GitHub repo — stars, recent commit
    activity, issue open/closed ratio, average time to close issues, and
    contributor count.

    IMPORTANT: Both 'owner' (the GitHub username or organization) and 'repo'
    (the repository name) are required and must be separate, specific values
    — e.g., owner='facebook', repo='react'. Do NOT guess the owner if the
    user's question only mentions a repo name without clearly specifying who
    owns it. Instead, ask the user to clarify which owner/organization they mean.
    """

    try:
        repo_info = get_repo_info(owner, repo)
        commits = get_commits(owner, repo)
        issues = get_issues(owner, repo)
        contributors = get_contributors(owner, repo)

        return build_health_scorecard(repo_info, commits, issues, contributors)

    except ValueError as e:
        return {"error": str(e)}


@mcp.tool()
def get_commit_activity(owner: str, repo: str, days: int) -> dict:
    """
    Get EXACT commit and issue activity (opened/closed) for a specific,
    custom time window (in days). ALWAYS use this tool — instead of
    relying on get_repo_health's default 6-month/all-time figures —
    whenever the user's question mentions a specific time period like
    'last week' (days=7), 'last month' (days=30), 'last 2 weeks' (days=14),
    'yesterday' (days=1), etc. Convert the user's time period into the
    correct number of days before calling this tool.
    """
    commits = get_commits(owner, repo)
    issues = get_issues(owner, repo)

    commit_count = commits_in_last_n_days(commits, days)
    issue_activity = issues_in_last_n_days(issues, days)

    return {
        "repo_name": f"{owner}/{repo}",
        "days_requested": days,
        "commit_count": commit_count,
        "issues_opened": issue_activity["opened"],
        "issues_closed": issue_activity["closed"],
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
    