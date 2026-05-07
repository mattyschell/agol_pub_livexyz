import sys
import requests

from is_jwt_token_expired import is_jwt_token_expired
from refresh_jwt_token import authenticate_service_account
from refresh_jwt_token import refresh_jwt_token

base_url = "https://graphql-enki.liveapp.com/features/648b1584fe16016869b2415a"


# 10,000 is the max page size
page_count = 1
cursor = None

# Option 1: Start with a JWT token
# token = "your_jwt_here"

# Option 2: Exchange service-account credentials for a JWT token
service_account_name = "your_service_account_name"
service_account_key = "your_65_char_service_account_key"
token = authenticate_service_account(service_account_name
                                    ,service_account_key)
while True:

    # check if your token is expired
    if is_jwt_token_expired(token):
        # if it is expired, replace the value
        token = refresh_jwt_token(token)

    headers = {
        "X-Auth-Token": "Bearer " + token
    }

    # Construct the request payload
    payload = {
        "pageSize": page_count,
        "cursor": cursor,
        "validityTime": {
            "lte": "2016-03-03T00:00:00Z" # can also use "at" : "2019-03-03T00:00:00Z", "gte": "03 Mar 19", "lte": "03 Mar 19"
        }
    }

    # Make the POST request with the headers
    response = requests.post(base_url
                            ,json=payload
                            ,headers=headers)

    # Check the response status code
    if response.status_code == 200:

        # Successful request
        data = response.json()

        # Do something with the data here
        # print(data)

        # Get the cursor for the next page
        cursor = data.get('data', {}).get('features', {}).get('pageInfo', {}).get('cursor')

        print(cursor)

        # If there is no cursor, it means we have reached the last page
        if not cursor:
            break
    else:
        # Error occurred - 401 is from token refresh needed
        print("Request failed with status code:", response.status_code)
        break
