from extract import get_repo_info, get_commits, get_issues, get_contributors
from transform import build_health_scorecard
from load import create_table, save_scorecard, get_latest_scorecard

# Make sure the table exists
create_table()

owner = "psf"
repo = "requests"

repo_info = get_repo_info(owner, repo)
commits = get_commits(owner, repo)
issues = get_issues(owner, repo)
contributors = get_contributors(owner, repo)

scorecard = build_health_scorecard(repo_info, commits, issues, contributors)

# Save it to the database
save_scorecard(scorecard)
print("Saved scorecard for", scorecard["repo_name"])

# Now try reading it back
retrieved = get_latest_scorecard("psf/requests")
print("\nRetrieved from database:")
print(retrieved)