import os
import requests
from dotenv import load_dotenv

# Load keys from .env file
load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Headers tell GitHub who we are (using our token)
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_repo_info(owner, repo):
    """Get basic info about a repo (stars, forks, description, etc.)"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_commits(owner, repo):
    """Get recent commits"""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_issues(owner, repo):
    """Get issues (open and closed)"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_contributors(owner, repo):
    """Get list of contributors"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url, headers=HEADERS)
    return response.json()


# This block only runs when you run this file directly (for testing)
if __name__ == "__main__":
    owner = "octocat"
    repo = "Hello-World"

    print("Repo Info:")
    print(get_repo_info(owner, repo))

    print("\nCommits:")
    print(get_commits(owner, repo))

    print("\nIssues:")
    print(get_issues(owner, repo))

    print("\nContributors:")
    print(get_contributors(owner, repo))