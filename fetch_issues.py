import json
import os
import time

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
    max_retries = 4
    retry_delays = [1, 2, 4, 8]

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                params={"per_page": 10, "page": page},
                timeout=10,
            )

            is_rate_limited = response.status_code == 429 or (
                response.status_code == 403
                and response.headers.get("X-RateLimit-Remaining") == "0"
            )

            if is_rate_limited:
                if attempt == max_retries:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")

                if retry_after and retry_after.isdigit():
                    wait_time = int(retry_after)
                else:
                    wait_time = retry_delays[attempt]

                print("Rate limited. Waiting", wait_time, "seconds.")
                time.sleep(wait_time)
                continue

            if 500 <= response.status_code <= 599:
                if attempt == max_retries:
                    response.raise_for_status()

                wait_time = retry_delays[attempt]
                print("Server error:", response.status_code)
                print("Retrying in", wait_time, "seconds.")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as error:
            if attempt == max_retries:
                print("Request failed on page", page, "-", error)
                raise SystemExit(1)

            wait_time = retry_delays[attempt]
            print("Network error:", error)
            print("Retrying in", wait_time, "seconds.")
            time.sleep(wait_time)
            continue
        except requests.exceptions.RequestException as error:
            print("Request failed on page", page, "-", error)
            raise SystemExit(1)

    raise SystemExit("Maximum retries exceeded on page " + str(page))


def main():
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


if __name__ == "__main__":
    main()