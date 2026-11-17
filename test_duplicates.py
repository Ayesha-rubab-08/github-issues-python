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


def test_duplicate_ids_are_skipped():
    pages = [
        [fake_issue(1), fake_issue(2)],
        [fake_issue(2), fake_issue(3)],
        [],
    ]
    saved = {}

    def fake_dump(data, f, indent=None):
        saved["data"] = data

    with patch.dict("os.environ", {"GITHUB_TOKEN": "x"}), \
         patch("fetch_issues.fetch_page", side_effect=pages), \
         patch("builtins.open", mock_open()), \
         patch("fetch_issues.json.dump", side_effect=fake_dump), \
         patch("fetch_issues.os.replace"), \
         patch("db.save_issues") as mock_save:
        fetch_issues.main()

    ids = [i["id"] for i in saved["data"]]
    assert ids == [1, 2, 3]
    mock_save.assert_called_once()
