from unittest.mock import patch, Mock
import requests
from fetch_issues import fetch_page

success_response = Mock()
success_response.status_code = 200
success_response.json.return_value = [{"id": 1}]

with patch("fetch_issues.requests.get", side_effect=[
    requests.exceptions.Timeout("fake timeout"),
    success_response
]) as mock_get:

    with patch("fetch_issues.time.sleep") as mock_sleep:
        result = fetch_page("https://example.com", {}, 1)

        print("Result:", result)
        print("Total requests:", mock_get.call_count)
        print("Wait calls:", mock_sleep.call_args_list)
