\# GitHub Issues Fetcher (Python)



A small Python script that fetches issues from the GitHub REST API, handles pagination, cleans the response, and saves the result to a JSON file.



\## What it does



\- Calls the GitHub Issues API for `n8n-io/n8n`

\- Fetches 3 pages of 10 issues each (30 records)

\- Keeps only the useful fields: `id`, `number`, `title`, `author`, `is\_pull\_request`, `labels`

\- Handles failed requests cleanly (timeouts, HTTP errors) with one clear error line

\- Exits with code `1` on failure, so schedulers and other tools can detect it

\- Saves the result to `issues.json`



\## Requirements



\- Python 3.12+

\- A GitHub personal access token



\## Setup (Windows PowerShell)



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



\## Configuration



The token is read from an environment variable. It is never stored in the code.



```powershell

$env:GITHUB\_TOKEN = "your\_token\_here"

```



\## Usage



```powershell

python fetch\_issues.py

```



Expected output:



```text

page 1 got 10

page 2 got 10

page 3 got 10

saved 30 issues

```



\## Example output (issues.json)



The values below are examples only.



```json

\[

&#x20; {

&#x20;   "id": 123456789,

&#x20;   "number": 1234,

&#x20;   "title": "Example issue title",

&#x20;   "author": "example-user",

&#x20;   "is\_pull\_request": false,

&#x20;   "labels": \["bug"]

&#x20; }

]

```



\## Error handling



If a request fails, the script prints one clean error line and exits with code `1`:



```text

Request failed on page 1 - 404 Client Error: Not Found for url: ...

```

