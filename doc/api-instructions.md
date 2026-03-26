## API instructions from Live XYZ Google Doc

Yes I will be feeding these into an AI agent.

### The Actual API instructions from Live XYZ Google Doc

To access our API, please follow these instructions


API Endpoint:


NYC All-time: https://graphql-enki.liveapp.com/features/648b1584fe16016869b2415a


Headers:


Key: Content-type | Value: application/json
Key: X-Auth-Token | Value: Bearer USER_TOKEN (replace USER_TOKEN with your unique token)
User token can be found in the drop-down menu on the Live XYZ Directory (click Api Key)


Request Body: The request body supports the following parameters:


"validityTime": defines the temporal range of the data that is returned. 
For today’s snapshot  "validityTime": 
{  "at": "now" }
For a specific date snapshot  "validityTime": 
{  "at": "2019-03-03T00:00:00Z" } or format as {  "at": "03 Mar 19" }
For all historical data, do not include the validityTime parameter in your request body
"pageSize": represents the number of items you want to receive in a single response. The maximum allowed value is 10,000.
"cursor":  an optional parameter that enables you to retrieve results from the next page of data in the result set returned by the API. You can obtain the cursor value from the body of any response that contains a next page. When making an initial request, you do not pass a cursor, and the response will return the first page of data (with the length determined by the "pageSize" parameter). This response will also include a "cursor" property, which you can utilize to retrieve the next page of data, as long as it is not the last page.

	Sample request body:
		{
    "pageSize": 10,
    "cursor": "1427226260",
    "validityTime": {
    "at": "now"
}
}

Here is a link to a python example of how to iterate over the complete dataset and utilize the cursor to get each page. Just follow the instructions in the read.md to add your own bearer token and run the script.

Please ensure that you include the specified headers and body parameters in your API requests to successfully access our data.

Here is the API Key refresh token endpoint

Request:

curl --location --request POST 'https://auth-api.liveapp.com/azure/refresh' \
--header 'Authorization: EXISTING_TOKEN' \
--header 'Content-Type: application/json'

Response:

{
    "token": "NEW_TOKEN"
}

You can parse this token (jwt) on jwt.io or using other libraries  to figure out when the token will expire (exp field in payload).

-

If you encounter any issues or have further questions regarding the API integration, please don't hesitate to reach out to our support team at [support@livexyz.com]. We will be more than happy to assist you.

We look forward to hearing your feedback! 
