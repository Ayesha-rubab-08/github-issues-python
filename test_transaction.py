from db import save_issues

issues = []
for i in range(30):
    issues.append({
        "id": 9000000 + i,
        "number": i,
        "title": f"test {i}",
        "author": "tester",
        "is_pull_request": False,
    })

# Break the 16th row: title is NOT NULL, so Postgres must reject it
issues[15]["title"] = None

try:
    save_issues(issues)
except SystemExit as error:
    print("save_issues exited with code", error.code)