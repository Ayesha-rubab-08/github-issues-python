# GitHub Issues Fetcher (Python)

A small Python script that fetches issues from the GitHub REST API, handles pagination, cleans the response, and saves the result to a JSON file.

## What it does

- Calls the GitHub Issues API for `n8n-io/n8n`
- Fetches 3 pages of 10 issues each (30 records)
- Keeps only the useful fields: `id`, `number`, `title`, `author`, `is_pull_request`
- Retries temporary failures with exponential backoff (1, 2, 4, 8 seconds): HTTP 429, 5xx, timeouts and connection errors
- Detects GitHub rate limits (HTTP 429, or 403 with `X-RateLimit-Remaining: 0`) and honors the `Retry-After` header
- Does not retry permanent errors (for example 401 or 404): it logs one `ERROR` line and exits with code `1`, so schedulers and other tools can detect the failure
- Skips duplicate issues by `id`
- Logs with timestamps and levels (`INFO`, `WARNING`, `ERROR`)
- Writes `issues.json` atomically (temporary file, then `os.replace`), so the file is never left half-written
- Saves issues to PostgreSQL with an upsert inside one transaction (all rows or none), so running the script twice never creates duplicates

## Requirements

- Python 3.12+
- A GitHub personal access token

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

The token is read from an environment variable. It is never stored in the code.

```powershell
$env:GITHUB_TOKEN = "your_token_here"
```

## Usage

```powershell
python fetch_issues.py
```

Expected output (timestamps will differ on every run):

```text
2026-11-14 16:09:12,345 INFO Page 1 got 10 issues, added 10
2026-11-14 16:09:12,812 INFO Page 2 got 10 issues, added 10
2026-11-14 16:09:13,267 INFO Page 3 got 10 issues, added 10
2026-11-14 16:09:13,270 INFO Saved 30 issues
2026-11-14 16:09:13,713 INFO Upserted 30 issues into Postgres
```

## Example output (issues.json)

The values below are examples only.

```json
[
  {
    "id": 123456789,
    "number": 1234,
    "title": "Example issue title",
    "author": "example-user",
    "is_pull_request": false,
    "labels": ["bug"]
  }
]
```

## PostgreSQL storage

After saving `issues.json`, the script upserts the issues into a PostgreSQL table.

Start PostgreSQL in Docker (the volume keeps the data after restarts):

```powershell
$env:PG_PASSWORD = "choose_a_strong_password"
docker run -d --name issues-postgres `
  -e POSTGRES_USER=issues_user `
  -e POSTGRES_PASSWORD=$env:PG_PASSWORD `
  -e POSTGRES_DB=issues_db `
  -p 127.0.0.1:5432:5432 `
  -v issues_pg_data:/var/lib/postgresql/data `
  --restart unless-stopped `
  postgres:16
```

Create the table and the index (safe to run more than once):

```powershell
Get-Content schema.sql | docker exec -i issues-postgres psql -U issues_user -d issues_db
```

Install the dependencies, set both environment variables, and run the script:

```powershell
pip install -r requirements.txt
$env:GITHUB_TOKEN = "your_token_here"
python fetch_issues.py
```

Running the script twice still leaves exactly 30 rows, because each row is an upsert (`INSERT ... ON CONFLICT (id) DO UPDATE`). All rows are written in one transaction, so a failure leaves no partial data. `python test_transaction.py` proves this by breaking one row on purpose.

The password is read from the `PG_PASSWORD` environment variable and is never stored in the code.

## Error handling

The script retries temporary failures with exponential backoff (1, 2, 4, 8 seconds):

- HTTP 429 and 5xx responses
- Timeouts and connection errors
- HTTP 403 only when `X-RateLimit-Remaining` is 0 (a rate limit, not a permission problem)

Duplicate issues are skipped, and `issues.json` is written atomically (`issues.json.tmp`, then `os.replace`), so a failed run never leaves a half-written file.

If a request fails for good (for example a bad token or a permission error), the script logs one `ERROR` line and exits with code `1`:

```text
2026-11-14 16:09:12,345 ERROR Request failed on page 1 - 404 Client Error: Not Found for url: ...
```
