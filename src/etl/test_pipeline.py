from extract import get_repo_info, get_commits, get_issues, get_contributors
from transform import build_health_scorecard, commits_in_last_n_days

owner = "psf"
repo = "requests"

repo_info = get_repo_info(owner, repo)
commits = get_commits(owner, repo)
issues = get_issues(owner, repo)
contributors = get_contributors(owner, repo)

scorecard = build_health_scorecard(repo_info, commits, issues, contributors)

print(scorecard)

# Test the flexible function directly with different timeframes
print("\nLast 10 days:", commits_in_last_n_days(commits, 10))
print("Last 30 days:", commits_in_last_n_days(commits, 30))
print("Last 91 days (13 weeks):", commits_in_last_n_days(commits, 91))