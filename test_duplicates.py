import json
from unittest.mock import patch, mock_open
import fetch_issues


def fake_issue(i):
    return {
        "id": i,
        "number": i,
        "title": "t" + str(i),
        "user": {"login": "u"},
        "labels": [],
    }


pages = [
    [fake_issue(1), fake_issue(2)],
    [fake_issue(2), fake_issue(3)],
    [],
]

saved = {}


def fake_dump(data, f, indent=None):
    saved["data"] = data


with patch.dict("os.environ", {"GITHUB_TOKEN": "x"}):
    with patch("fetch_issues.fetch_page", side_effect=pages):
        with patch("builtins.open", mock_open()):
            with patch("fetch_issues.json.dump", side_effect=fake_dump):
                fetch_issues.main()

ids = [i["id"] for i in saved["data"]]
print("Saved ids:", ids)
