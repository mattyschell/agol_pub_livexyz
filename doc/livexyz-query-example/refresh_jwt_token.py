import requests


def authenticate_service_account(name: str
                                ,key: str) -> str:
    """Exchange service account name/key for a JWT token."""
    response = requests.post("https://auth-api.liveapp.com/authentication"
                            ,json={"name": name, "key": key})

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Service account authentication failed: {response.status_code}"
        )

    token = response.json().get('token')
    if not token:
        raise RuntimeError("Authentication succeeded but token was missing")
    return token


def refresh_jwt_token(token: str) -> str:
    print('Refreshing JWT Token')

    headers = {
        "Authorization": token
    }
    response = requests.post("https://auth-api.liveapp.com/azure/refresh"
                            ,headers=headers)

    if response.status_code == 200:

        # Successful request
        data = response.json()

        # Do something with the data here
        token = data.get('token')

        print(token)
        return token

    raise RuntimeError(f"Token refresh failed: {response.status_code}")
