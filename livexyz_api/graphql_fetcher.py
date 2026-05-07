import requests
import json
import logging
import time
from datetime import datetime, timedelta
import base64


LOGGER = logging.getLogger(__name__)


AUTH_ENDPOINT = "https://auth-api.liveapp.com/authentication"
REFRESH_ENDPOINT = "https://auth-api.liveapp.com/azure/refresh"


def _normalize_token(token):
    """Normalize token text copied from env vars or docs."""
    if token is None:
        return None

    clean = str(token).strip()
    if clean.startswith('"') and clean.endswith('"'):
        clean = clean[1:-1].strip()
    if clean.lower().startswith("bearer "):
        clean = clean[7:].strip()
    return clean


def _looks_like_jwt(token):
    token = _normalize_token(token)
    if not token:
        return False
    return len(token.split('.')) == 3


class GraphQLFetcher:
    """
    Base class for fetching data from a GraphQL API.
    Provides basic functionality to make POST requests with JSON payloads.
    """

    def __init__(self
                ,endpoint
                ,headers=None):
        """
        Initialize the fetcher with endpoint and optional headers.

        :param endpoint: The API endpoint URL
        :param headers: Dictionary of headers to include in requests
        """
        self.endpoint = endpoint
        self.headers = headers or {}

    def fetch(self
              ,payload):
        """
        Make a POST request to the endpoint with the given payload.

        :param payload: Dictionary to send as JSON in the request body
        :return: Response object from requests
        """
        response = requests.post(self.endpoint
                                ,json=payload
                                ,headers=self.headers)
        return response


class LiveXYZFetcher(GraphQLFetcher):
    """
    Child class for fetching data from the LiveXYZ API.
    Handles JWT token management, including expiration checks and refresh.
    Supports pagination with cursor.
    """

    def __init__(self
                ,token=None
                ,endpoint=None
                ,service_account_name=None
                ,service_account_key=None):
        """
        Initialize with JWT token and optional endpoint.

        :param token: Initial JWT token or service account key
        :param endpoint: API endpoint, defaults to LiveXYZ features endpoint
        :param service_account_name: Service account name for key auth
        :param service_account_key: Service account key for key auth
        """
        if endpoint is None:
            endpoint = "https://graphql-enki.liveapp.com/features/648b1584fe16016869b2415a"

        token = _normalize_token(token)

        service_account_name = _normalize_token(service_account_name)
        service_account_key = _normalize_token(service_account_key)

        if service_account_key and not service_account_name:
            raise ValueError(
                "Service account name is required when key is provided"
            )

        self.service_account_name = service_account_name
        self.service_account_key = service_account_key

        if service_account_name and token and not service_account_key:
            if not _looks_like_jwt(token):
                self.service_account_key = token
                token = None

        if not token and self.service_account_key:
            token = self._authenticate_service_account(
                self.service_account_name
               ,self.service_account_key
            )

        if token and not _looks_like_jwt(token):
            raise ValueError(
                "Expected JWT token; for service keys set both "
                "LIVEXYZ_SERVICE_ACCOUNT_NAME and "
                "LIVEXYZ_SERVICE_ACCOUNT_KEY"
            )

        if not token:
            raise ValueError(
                "A JWT token or service account credentials are required"
            )
        
        super().__init__(endpoint
                        ,{"X-Auth-Token": f"Bearer {token}"})
        
        self.token = token

    def _authenticate_service_account(self
                                     ,name
                                     ,key):
        """
        Exchange service account credentials for a JWT.

        :param name: Service account name
        :param key: Service account key
        :return: JWT token string
        """
        payload = {
            "name": name
           ,"key": key
        }
        response = requests.post(AUTH_ENDPOINT
                                ,json=payload)

        if response.status_code not in (200, 201):
            raise Exception(
                "Failed to authenticate service account: "
                f"{response.status_code}"
            )

        data = response.json()
        token = _normalize_token(data.get("token"))

        if not token:
            raise Exception("Authentication succeeded but token was missing")

        return token

    def _is_jwt_token_expired(self
                             ,token):
        """
        Check if the JWT token is expired.

        :param token: JWT token string
        :return: True if expired, False otherwise
        """
        current_time = datetime.utcnow()
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return True

            payload_b64 = parts[1]
            padding = '=' * ((4 - len(payload_b64) % 4) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes.decode('utf-8'))

            if 'exp' not in payload:
                # bad token
                return True

            exp_timestamp = int(payload['exp'])
            exp_datetime = datetime.utcfromtimestamp(exp_timestamp)

            if exp_datetime < current_time - timedelta(minutes=1):
                # Token has expired
                return True
            # Token is still valid  
            return False  

        except Exception:
            # decode error 
            return True  

    def _refresh_jwt_token(self
                          ,token):
        """
        Refresh the JWT token.

        :param token: Current token
        :return: New token
        """
        
        headers = {
            "Authorization": _normalize_token(token)
        }
        response = requests.post(REFRESH_ENDPOINT
                                ,headers=headers)

        if response.status_code == 200:
            data = response.json()
            new_token = data.get('token')
            return new_token
        else:
            raise Exception(f"Failed to refresh token: {response.status_code}")

    def _ensure_valid_token(self):
        """
        Ensure the token is valid, refresh if necessary.
        """
        if self._is_jwt_token_expired(self.token):
            try:
                self.token = self._refresh_jwt_token(self.token)
            except Exception:
                if not self.service_account_key:
                    raise
                self.token = self._authenticate_service_account(
                    self.service_account_name
                   ,self.service_account_key
                )
            self.headers["X-Auth-Token"] = f"Bearer {self.token}"

    def _fetch_with_retry(self
                         ,payload
                         ,max_retries=3
                         ,backoff_factor=1.0):
        """
        Fetch with retry logic for transient errors.

        :param payload: Request payload
        :param max_retries: Maximum number of retries
        :param backoff_factor: Base backoff multiplier (exponential)
        :return: Response object
        """
        transient_status_codes = {408, 429, 500, 502, 503, 504}

        for attempt in range(max_retries + 1):
            try:
                response = self.fetch(payload)

                if response.status_code in transient_status_codes:
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        LOGGER.warning(
                            "Transient error %d on attempt %d/%d. "
                            "Retrying in %.1f seconds..."
                            ,response.status_code
                            ,attempt + 1
                            ,max_retries + 1
                            ,wait_time
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        LOGGER.error(
                            "Transient error %d persisted after %d retries"
                            ,response.status_code
                            ,max_retries + 1
                        )

                return response

            except Exception as e:
                if attempt < max_retries:
                    wait_time = backoff_factor * (2 ** attempt)
                    LOGGER.warning(
                        "Request exception on attempt %d/%d: %s. "
                        "Retrying in %.1f seconds..."
                        ,attempt + 1
                        ,max_retries + 1
                        ,str(e)
                        ,wait_time
                    )
                    time.sleep(wait_time)
                else:
                    LOGGER.error(
                        "Request exception persisted after %d retries: %s"
                        ,max_retries + 1
                        ,str(e)
                    )
                    raise

        return response

    def fetch_paginated(self
                       ,base_payload
                       ,page_size=1000):
        """
        Fetch data with pagination support.

        :param base_payload: Base payload dictionary (without pageSize and cursor)
        :param page_size: Number of items per page
        :return: Generator yielding data pages
        """
        cursor = None
        while True:
            self._ensure_valid_token()

            payload = base_payload.copy()
            payload["pageSize"] = page_size
            payload["cursor"] = cursor

            response = self._fetch_with_retry(payload)

            if response.status_code == 200:
                data = response.json()
                yield data

                # Get the cursor for the next page
                cursor = data.get('data', {}).get('features', {}).get('pageInfo', {}).get('cursor')
                # print(f"Next cursor: {cursor}")

                # If there is no cursor, it means we have reached the last page
                if not cursor:
                    break
            else:
                LOGGER.error(
                    "Request failed with status code: %d"
                    ,response.status_code
                )
                if response.text:
                    LOGGER.error(
                        "Response body: %s"
                        ,response.text[:500]
                    )
                break

    def iter_pages(self
                  ,base_payload
                  ,page_size=1000
                  ,max_pages=None):
        """
        Iterate paginated responses with optional page cap.

        :param base_payload: Base payload dictionary (without pageSize/cursor)
        :param page_size: Number of items per page
        :param max_pages: Optional limit on number of pages to iterate
        :return: Generator yielding page dictionaries
        """
        pages_read = 0
        for page in self.fetch_paginated(base_payload
                                        ,page_size):
            yield page
            pages_read += 1
            if max_pages is not None and pages_read >= max_pages:
                break

    def iter_nodes(self
                  ,base_payload
                  ,page_size=1000
                  ,max_pages=None):
        """
        Iterate feature nodes across paginated responses.

        :param base_payload: Base payload dictionary (without pageSize/cursor)
        :param page_size: Number of items per page
        :param max_pages: Optional limit on number of pages to iterate
        :return: Generator yielding node dictionaries
        """
        for page in self.iter_pages(base_payload
                                   ,page_size
                                   ,max_pages):
            nodes = (
                page.get("data", {})
                    .get("features", {})
                    .get("nodes", [])
            )
            for node in nodes:
                yield node