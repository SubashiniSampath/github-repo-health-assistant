from extract import get_repo_info, get_commits, get_issues, get_contributors
from transform import build_health_scorecard

owner = "psf"
repo = "requests"

repo_info = get_repo_info(owner, repo)
commits = get_commits(owner, repo)
issues = get_issues(owner, repo)
contributors = get_contributors(owner, repo)

scorecard = build_health_scorecard(repo_info, commits, issues, contributors)

print(scorecard)