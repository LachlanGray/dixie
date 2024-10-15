import os
import subprocess
import json

workspaces_dir = "evaluation/workspaces"

def clone_repo(repo_url, commit, clone_directory):
    """Clones a repository at a specific commit."""

    print(f"Cloning {repo_url} at commit {commit} to {clone_directory}")
    subprocess.run(["git", "init", clone_directory])

    # Step 2: Set the remote origin for the repository
    print(f"Setting remote origin to {repo_url}")
    subprocess.run(["git", "-C", clone_directory, "remote", "add", "origin", repo_url])

    print(f"Fetching commit {commit}")
    # Step 3: Fetch the specific commit
    subprocess.run(["git", "-C", clone_directory, "fetch", "--depth", "1", "origin", commit])

    print(f"Checking out commit {commit}")
    # Step 4: Checkout the specific commit
    subprocess.run(["git", "-C", clone_directory, "checkout", commit])


def load_issue(file_path):
    """Load JSON data from a given file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def init_workspace_from_issue(issue):
    """Initializes a workspace from an issue."""

    issue_no = issue['number']
    repo_name = issue['url'].split('/')[-1]
    workspace_path = f"{repo_name}_issue_{issue_no}"

    workspace_path = os.path.join(workspaces_dir, workspace_path)

    if os.path.exists(workspace_path):
        print(f"Workspace already exists: {workspace_path}")
        return

    os.makedirs(workspace_path)

    issue_path = os.path.join(workspace_path, 'issue.json')
    with open(issue_path, 'w') as f:
        json.dump(issue, f, indent=4)

    clone_directory = os.path.join(workspace_path, repo_name)
    os.makedirs(clone_directory, exist_ok=True)

    repo_url = issue['html_url'].split('/pull')[0]
    commit_hash = issue['base_commit']
    clone_repo(repo_url, commit_hash, clone_directory)


if __name__ == '__main__':
    os.makedirs(workspaces_dir, exist_ok=True)

    issue_path = "evaluation/parsed_issues/sqlfluff_sqlfluff_issue_6335.json"
    issue = load_issue(issue_path)
    init_workspace_from_issue(issue)

