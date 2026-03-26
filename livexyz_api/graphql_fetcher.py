import requests
import json
from datetime import datetime, timedelta
import base64


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
                ,token
                ,endpoint=None):
        """
        Initialize with JWT token and optional endpoint.

        :param token: Initial JWT token
        :param endpoint: API endpoint, defaults to LiveXYZ features endpoint
        """
        if endpoint is None:
            endpoint = "https://graphql-enki.liveapp.com/features/648b1584fe16016869b2415a"
        
        super().__init__(endpoint
                        ,{"X-Auth-Token": f"Bearer {token}"})
        
        self.token = token

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
            "Authorization": token
        }
        response = requests.post("https://auth-api.liveapp.com/azure/refresh"
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
            self.token = self._refresh_jwt_token(self.token)
            self.headers["X-Auth-Token"] = f"Bearer {self.token}"

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

            response = self.fetch(payload)

            if response.status_code == 200:
                data = response.json()
                yield data

                # Get the cursor for the next page
                cursor = data.get('data', {}).get('features', {}).get('pageInfo', {}).get('cursor')
                print(f"Next cursor: {cursor}")

                # If there is no cursor, it means we have reached the last page
                if not cursor:
                    break
            else:
                print(f"Request failed with status code: {response.status_code}")
                break