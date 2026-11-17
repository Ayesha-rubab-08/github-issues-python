from unittest.mock import patch, Mock

import pytest
import requests

from fetch_issues import fetch_page


def test_403_with_rate_limit_exhausted_retries():
    limited = Mock()
    limited.status_code = 403
    limited.headers = {"X-RateLimit-Remaining": "0"}

    ok = Mock()
    ok.status_code = 200
    ok.json.return_value = [{"id": 1}]

    with patch("fetch_issues.requests.get", side_effect=[limited, ok]) as mock_get, \
         patch("fetch_issues.time.sleep") as mock_sleep:
        result = fetch_page("https://example.com", {}, 1)

    assert result == [{"id": 1}]
    assert mock_get.call_count == 2
    assert mock_sleep.call_count == 1


def test_403_without_rate_limit_stops_without_retry():
    denied = Mock()
    denied.status_code = 403
    denied.headers = {"X-RateLimit-Remaining": "4999"}
    denied.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")

    with patch("fetch_issues.requests.get", side_effect=[denied]) as mock_get, \
         patch("fetch_issues.time.sleep") as mock_sleep:
        with pytest.raises(SystemExit):
            fetch_page("https://example.com", {}, 1)

    assert mock_get.call_count == 1
    assert mock_sleep.call_count == 0
