from unittest.mock import patch, Mock

from fetch_issues import fetch_page


def test_retries_after_503_then_succeeds():
    fake_response = Mock()
    fake_response.status_code = 503

    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = [{"id": 1}]

    with patch("fetch_issues.requests.get", side_effect=[
        fake_response,
        success_response,
    ]) as mock_get, patch("fetch_issues.time.sleep") as mock_sleep:
        result = fetch_page("https://example.com", {}, 1)

    assert result == [{"id": 1}]
    assert mock_get.call_count == 2
    assert mock_sleep.call_count == 1
