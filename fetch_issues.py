import json
import os
import requests


def clean_issue(issue):
    return {
        "id": issue["id"],
        "number": issue["number"],
        "title": issue["title"],
        "author": issue["user"]["login"],
        "is_pull_request": "pull_request" in issue,
    }


def fetch_page(url, headers, page):
    try:
        response = requests.get(
            url,
            headers=headers,
            params={"per_page": 10, "page": page},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print("Request failed on page", page, "-", error)
        raise SystemExit(1)


token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise SystemExit("GITHUB_TOKEN is not set")

url = "https://api.github.com/repos/n8n-io/n8n/issues"
headers = {"Authorization": f"Bearer {token}"}

all_issues = []
for page in range(1, 4):
    batch = fetch_page(url, headers, page)
    if not batch:
        break
    all_issues.extend(clean_issue(issue) for issue in batch)
    print("page", page, "got", len(batch))

with open("issues.json", "w", encoding="utf-8") as f:
    json.dump(all_issues, f, indent=2)
print("saved", len(all_issues), "issues")
