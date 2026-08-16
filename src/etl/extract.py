import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def fetch_all_pages(url):
    """Keep asking GitHub for the next page until there's no more data"""
    all_data = []
    page = 1

    while True:
        response = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        data = response.json()

        # If GitHub returns an empty list, we've reached the end
        if not data:
            break

        all_data.extend(data)
        page += 1

        # Safety brake: stop after 10 pages (1000 items) so we don't accidentally loop forever
        if page > 10:
            break

    return all_data


def get_repo_info(owner, repo):
    """Get basic info about a repo (stars, forks, description, etc.) - only 1 page, no pagination needed"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def get_commits(owner, repo):
    """Get ALL recent commits across multiple pages"""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    return fetch_all_pages(url)


def get_issues(owner, repo):
    """Get ALL issues (open and closed) across multiple pages"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    return fetch_all_pages(url)


def get_contributors(owner, repo):
    """Get ALL contributors across multiple pages"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    return fetch_all_pages(url)


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