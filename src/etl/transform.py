from datetime import datetime, timezone


def days_since_last_commit(commits):
    """How many days ago was the most recent commit?"""
    if not commits:
        return None

    latest_commit = commits[0]  # GitHub returns newest commit first
    commit_date_str = latest_commit["commit"]["author"]["date"]
    commit_date = datetime.fromisoformat(commit_date_str.replace("Z", "+00:00"))

    today = datetime.now(timezone.utc)
    days_ago = (today - commit_date).days
    return days_ago


def commits_last_6_months(commits):
    """Count how many commits happened in the last 6 months"""
    six_months_ago = datetime.now(timezone.utc).timestamp() - (6 * 30 * 24 * 60 * 60)

    count = 0
    for commit in commits:
        commit_date_str = commit["commit"]["author"]["date"]
        commit_date = datetime.fromisoformat(commit_date_str.replace("Z", "+00:00"))
        if commit_date.timestamp() > six_months_ago:
            count += 1

    return count


def issue_open_closed_ratio(issues):
    """Count open vs closed issues"""
    open_count = 0
    closed_count = 0
 
    for issue in issues:
        # GitHub's issues API also includes pull requests, so we skip those
        if "pull_request" in issue:
            continue

        if issue["state"] == "open":
            open_count += 1
        else:
            closed_count += 1

    return {"open": open_count, "closed": closed_count}


def average_issue_close_time(issues):
    """Average number of days it takes to close an issue"""
    close_times = []

    for issue in issues:
        if "pull_request" in issue:
            continue
        if issue["state"] != "closed":
            continue
        if issue["closed_at"] is None:
            continue

        created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
        closed = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
        days_to_close = (closed - created).days
        close_times.append(days_to_close)

    if not close_times:
        return None

    return sum(close_times) / len(close_times)


def active_contributor_count(contributors):
    """Simple count of total contributors"""
    return len(contributors)


def build_health_scorecard(repo_info, commits, issues, contributors):
    """Combine everything into one clean summary"""
    return {
        "repo_name": repo_info.get("full_name"),
        "stars": repo_info.get("stargazers_count"),
        "days_since_last_commit": days_since_last_commit(commits),
        "commits_last_6_months": commits_last_6_months(commits),
        "issues": issue_open_closed_ratio(issues),
        "avg_days_to_close_issue": average_issue_close_time(issues),
        "contributor_count": active_contributor_count(contributors),
    }