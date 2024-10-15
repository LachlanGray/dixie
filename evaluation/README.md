## Evaluation

Save a github PAT to a `.env` in the repo root, then to generate the example issues run
```
python evaluation/get_issues.py
```

This will populate `evaluation/parsed_issues` with json files, one for each pr that are formatted like this:
```
{
    "title": "issue title",
    "description": "...",
    "base_commit": "4e7367596ee3fb17d6280d035e465e4e45c70473",
    "diff": "dif --git ..."
}
```
