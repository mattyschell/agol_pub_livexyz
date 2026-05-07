import unittest
from unittest.mock import patch, MagicMock
import json
import datetime
from livexyz_api.graphql_fetcher import (
    GraphQLFetcher
    ,LiveXYZFetcher
)


def _build_test_jwt(exp_offset_hours=1):
    future_ts = int((datetime.datetime.utcnow()
                     + datetime.timedelta(hours=exp_offset_hours))
                    .timestamp())
    token_payload = {"exp": future_ts}
    import base64
    payload_json = json.dumps(token_payload)
    payload_b64 = base64.urlsafe_b64encode(
        payload_json.encode()
    ).decode().rstrip('=')
    return f"header.{payload_b64}.signature"


class TestGraphQLFetcher(unittest.TestCase):
    """Tests for GraphQLFetcher base class."""

    def setUp(self):
        self.endpoint = "https://api.example.com/graphql"
        self.fetcher = GraphQLFetcher(self.endpoint)

    def test_init_default_headers(self):
        """Test initialization with default headers."""
        self.assertEqual(self.fetcher.endpoint, self.endpoint)
        self.assertEqual(self.fetcher.headers, {})

    def test_init_custom_headers(self):
        """Test initialization with custom headers."""
        custom_headers = {"Authorization": "Bearer token"}
        fetcher = GraphQLFetcher(self.endpoint, custom_headers)
        self.assertEqual(fetcher.headers, custom_headers)

    @patch('requests.post')
    def test_fetch_success(self, mock_post):
        """Test fetch method with successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"result": "success"}}
        mock_post.return_value = mock_response

        payload = {"query": "{ test }"}
        response = self.fetcher.fetch(payload)

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once_with(
            self.endpoint
            ,json=payload
            ,headers={})

    @patch('requests.post')
    def test_fetch_with_headers(self, mock_post):
        """Test fetch method includes custom headers."""
        custom_headers = {"X-Auth-Token": "Bearer abc123"}
        fetcher = GraphQLFetcher(self.endpoint, custom_headers)
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        payload = {"query": "{ test }"}
        fetcher.fetch(payload)

        mock_post.assert_called_once_with(
            self.endpoint
            ,json=payload
            ,headers=custom_headers)


class TestLiveXYZFetcher(unittest.TestCase):
    """Tests for LiveXYZFetcher child class."""

    def setUp(self):
        self.token = _build_test_jwt(1)
        self.fetcher = LiveXYZFetcher(self.token)

    def test_init_default_endpoint(self):
        """Test initialization with default LiveXYZ endpoint."""
        self.assertIn("graphql-enki.liveapp.com", self.fetcher.endpoint)
        self.assertEqual(self.fetcher.token, self.token)

    def test_init_custom_endpoint(self):
        """Test initialization with custom endpoint."""
        custom_endpoint = "https://custom.endpoint.com"
        fetcher = LiveXYZFetcher(self.token, custom_endpoint)
        self.assertEqual(fetcher.endpoint, custom_endpoint)

    def test_is_jwt_token_expired_valid(self):
        """Test with valid (non-expired) token."""
        token = _build_test_jwt(1)

        is_expired = self.fetcher._is_jwt_token_expired(token)
        self.assertFalse(is_expired)

    def test_is_jwt_token_expired_expired(self):
        """Test with expired token."""
        # Create a token that expired far in past (fixed timestamp)
        token_payload = {"exp": 1000000000}  # Sept 2001
        import base64
        payload_json = json.dumps(token_payload)
        payload_b64 = base64.urlsafe_b64encode(
            payload_json.encode()).decode().rstrip('=')
        token = f"header.{payload_b64}.signature"

        is_expired = self.fetcher._is_jwt_token_expired(token)
        self.assertTrue(is_expired)

    def test_is_jwt_token_expired_malformed(self):
        """Test with malformed token (not 3 parts)."""
        malformed_token = "invalid.token"
        is_expired = self.fetcher._is_jwt_token_expired(malformed_token)
        self.assertTrue(is_expired)

    def test_is_jwt_token_expired_missing_exp(self):
        """Test with token missing exp claim."""
        token_payload = {"iss": "test"}
        import base64
        payload_json = json.dumps(token_payload)
        payload_b64 = base64.urlsafe_b64encode(
            payload_json.encode()).decode().rstrip('=')
        token = f"header.{payload_b64}.signature"

        is_expired = self.fetcher._is_jwt_token_expired(token)
        self.assertTrue(is_expired)

    @patch('requests.post')
    def test_refresh_jwt_token_success(self, mock_post):
        """Test refresh_jwt_token with successful response."""
        new_token = "new_jwt_token_value"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": new_token}
        mock_post.return_value = mock_response

        result = self.fetcher._refresh_jwt_token(self.token)

        self.assertEqual(result, new_token)
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_authenticate_service_account_success(self, mock_post):
        """Service account credentials are exchanged for JWT."""
        new_token = _build_test_jwt(1)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "name": "ProdSvc"
           ,"token": new_token
        }
        mock_post.return_value = mock_response

        fetcher = LiveXYZFetcher(
            None
           ,None
           ,"ProdSvc"
           ,"x" * 65
        )

        self.assertEqual(fetcher.token, new_token)
        self.assertEqual(
            fetcher.headers.get("X-Auth-Token")
           ,f"Bearer {new_token}"
        )

    @patch('requests.post')
    def test_init_token_uses_service_key_when_name_present(self, mock_post):
        """Non-JWT token is treated as key when service name is present."""
        new_token = _build_test_jwt(1)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "name": "ProdSvc"
           ,"token": new_token
        }
        mock_post.return_value = mock_response

        fetcher = LiveXYZFetcher("x" * 65
                                ,None
                                ,"ProdSvc")

        self.assertEqual(fetcher.token, new_token)

    def test_init_non_jwt_without_service_name_fails(self):
        """Reject plain service keys passed as JWT token."""
        with self.assertRaises(ValueError):
            LiveXYZFetcher("x" * 65)

    @patch('requests.post')
    def test_refresh_jwt_token_failure(self, mock_post):
        """Test refresh_jwt_token with failed response."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.fetcher._refresh_jwt_token(self.token)

        self.assertIn("Failed to refresh token", str(context.exception))

    @patch.object(LiveXYZFetcher, '_refresh_jwt_token')
    @patch.object(LiveXYZFetcher, '_is_jwt_token_expired')
    def test_ensure_valid_token_valid(self
                                       ,mock_expired
                                       ,mock_refresh):
        """Test _ensure_valid_token when token is valid."""
        mock_expired.return_value = False

        self.fetcher._ensure_valid_token()

        mock_refresh.assert_not_called()

    @patch.object(LiveXYZFetcher, '_refresh_jwt_token')
    @patch.object(LiveXYZFetcher, '_is_jwt_token_expired')
    def test_ensure_valid_token_expired(self
                                         ,mock_expired
                                         ,mock_refresh):
        """Test _ensure_valid_token when token is expired."""
        mock_expired.return_value = True
        new_token = "refreshed_token"
        mock_refresh.return_value = new_token

        self.fetcher._ensure_valid_token()

        self.assertEqual(self.fetcher.token, new_token)
        mock_refresh.assert_called_once()

    @patch.object(LiveXYZFetcher, '_ensure_valid_token')
    @patch.object(LiveXYZFetcher, 'fetch')
    def test_fetch_paginated_single_page(self
                                          ,mock_fetch
                                          ,mock_ensure):
        """Test fetch_paginated with single page (no cursor)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "features": {
                    "pageInfo": {"cursor": None}
                }
            }
        }
        mock_fetch.return_value = mock_response

        base_payload = {"test": "data"}
        pages = list(self.fetcher.fetch_paginated(base_payload))

        self.assertEqual(len(pages), 1)
        mock_ensure.assert_called_once()

    @patch.object(LiveXYZFetcher, '_ensure_valid_token')
    @patch.object(LiveXYZFetcher, 'fetch')
    def test_fetch_paginated_multiple_pages(self
                                             ,mock_fetch
                                             ,mock_ensure):
        """Test fetch_paginated with multiple pages."""
        responses = [
            MagicMock(status_code=200, json=lambda: {
                "data": {"features": {"pageInfo": {"cursor": "cursor1"}}}
            }),
            MagicMock(status_code=200, json=lambda: {
                "data": {"features": {"pageInfo": {"cursor": None}}}
            })
        ]
        mock_fetch.side_effect = responses

        base_payload = {"test": "data"}
        pages = list(self.fetcher.fetch_paginated(base_payload))

        self.assertEqual(len(pages), 2)
        self.assertEqual(mock_ensure.call_count, 2)

    @patch.object(LiveXYZFetcher, '_ensure_valid_token')
    @patch.object(LiveXYZFetcher, 'fetch')
    def test_fetch_paginated_error_response(self
                                             ,mock_fetch
                                             ,mock_ensure):
        """Test fetch_paginated stops on error response."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_fetch.return_value = mock_response

        base_payload = {"test": "data"}
        pages = list(self.fetcher.fetch_paginated(base_payload))

        self.assertEqual(len(pages), 0)


if __name__ == "__main__":
    unittest.main()
