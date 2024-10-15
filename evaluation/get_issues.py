import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'token {token}'}

raw_issues_directory = 'evaluation/issue_data'
parsed_issues_directory = 'evaluation/parsed_issues'

repos = [
    'sqlfluff/sqlfluff',
    'pvlib/pvlib-python',
]

# raw data ####################

def get_issues(repo, state='closed'):
    """Fetches issues for a given repository."""
    issues_url = f'https://api.github.com/repos/{repo}/issues'
    params = {'state': state}
    response = requests.get(issues_url, headers=headers, params=params)
    return response.json()


def save_issues(repo, state='closed', directory=raw_issues_directory):
    """Saves issues to a JSON file, creates directory if necessary."""

    issues = get_issues(repo)

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = f"{directory}/{repo.replace('/', '_')}_issues.json"

    if os.path.exists(filename):
        print(f"File already exists for repository: {repo}")
        return

    with open(filename, 'w') as f:
        json.dump(issues, f, indent=4)

    print(f"Saved {len(issues)} issues to {filename}")


def load_issues_from_file(repo, directory=raw_issues_directory):
    """Loads issues from a JSON file for a given repository."""
    filename = f"{directory}/{repo.replace('/', '_')}_issues.json"

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            issues = json.load(f)
        print(f"Loaded {len(issues)} issues from {filename}")
        return issues
    else:
        print(f"No file found for repository: {repo}")
        return None


# parse data ####################

def fetch_pull_request_data(pull_request_url):
    """Fetches pull request details to get base commit."""
    response = requests.get(pull_request_url, headers=headers)
    return response.json()

def fetch_diff(diff_url):
    """Fetches the diff for the pull request."""
    response = requests.get(diff_url, headers=headers)
    return response.text


def parse_issue(issue_data):
    """Parses issue to extract the title, description, base commit, and diff."""
    title = issue_data['title']
    description = issue_data['body']

    if not 'pull_request' in issue_data:
        return None

    pull_request_data = fetch_pull_request_data(issue_data['pull_request']['url'])
    base_commit = pull_request_data['base']['sha']  # Base commit SHA

    diff = fetch_diff(issue_data['pull_request']['diff_url'])

    parsed_data = {
        'url': issue_data['repository_url'],
        'html_url': issue_data['html_url'],
        'title': title,
        'number': issue_data['number'],
        'description': description,
        'base_commit': base_commit,
        'diff': diff
    }

    return parsed_data

def save_to_json(parsed_data, repo, issue_number, directory=parsed_issues_directory):
    """Saves the parsed data to a new JSON file."""
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = f"{directory}/{repo.replace('/', '_')}_issue_{issue_number}.json"
    with open(filename, 'w') as f:
        json.dump(parsed_data, f, indent=4)

    print(f"  created: {filename}")


if __name__ == '__main__':
    for repo in repos:
        save_issues(repo)
        issues = load_issues_from_file(repo)

        # save issues that have prs attached
        print(f"parsing issues for {repo}")
        for issue in issues:
            parsed_data = parse_issue(issue)
            if not parsed_data:
                continue

            save_to_json(parsed_data, repo, issue['number'])

