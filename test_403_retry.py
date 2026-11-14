from unittest.mock import patch, Mock
import requests
from fetch_issues import fetch_page

# Test 1: 403 with rate limit exhausted -> should retry
limited = Mock()
limited.status_code = 403
limited.headers = {"X-RateLimit-Remaining": "0"}

ok = Mock()
ok.status_code = 200
ok.json.return_value = [{"id": 1}]

with patch("fetch_issues.requests.get", side_effect=[limited, ok]) as mock_get:
    with patch("fetch_issues.time.sleep") as mock_sleep:
        result = fetch_page("https://example.com", {}, 1)
        print("Test 1 result:", result)
        print("Test 1 requests:", mock_get.call_count)
        print("Test 1 waits:", mock_sleep.call_args_list)

# Test 2: 403 with rate limit NOT exhausted -> should stop, no retry
denied = Mock()
denied.status_code = 403
denied.headers = {"X-RateLimit-Remaining": "4999"}
denied.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")

with patch("fetch_issues.requests.get", side_effect=[denied]) as mock_get:
    with patch("fetch_issues.time.sleep") as mock_sleep:
        try:
            fetch_page("https://example.com", {}, 1)
        except SystemExit as e:
            print("Test 2 exit code:", e.code)
        print("Test 2 requests:", mock_get.call_count)
        print("Test 2 waits:", mock_sleep.call_args_list)
