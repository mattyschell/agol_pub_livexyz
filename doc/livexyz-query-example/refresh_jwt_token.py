import requests


def refresh_jwt_token(token: str) -> str:
    print('Refreshing JWT Token')

    headers = {
        "Authorization": token
    }
    response = requests.post("https://auth-api.liveapp.com/azure/refresh", headers=headers)

    if response.status_code == 200:

        # Successful request
        data = response.json()

        # Do something with the data here
        token = data.get('token')

        print(token)
        return token
