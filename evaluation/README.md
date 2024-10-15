## Evaluation

**Get issues**
Save a github PAT to a `.env` in the repo root, then to generate the example issues run.
```
python evaluation/get_issues.py
```

This will populate `evaluation/parsed_issues` with json files, one for each pr, formatted like this:
```
{
    "title": "issue title",
    "description": "...",
    "base_commit": "4e7367596ee3fb17d6280d035e465e4e45c70473",
    "diff": "dif --git ..."
}
```

Right now it's grabbing up to 100 closed prs from repositories hardcoded in `evaluation/get_issues.py::repos`.


**Workspaces**
A workspace is created from a github issue
```
python evaluation/make_workspace.py
```

This will create a "workspace"
```
evaluation/workspaces/{repo_name}_issue_{issue_no}/
    issue.json
    {repo}/
        ...cloned repo code...
```

The workspace contains the json of the issue, and a clone at the base commit of the issue.
