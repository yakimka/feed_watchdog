import httpx

httpx.HTTPStatusError


def make_request_with_retries(url, retries=5, backoff_factor=0.1):
    transport = httpx.AsyncHTTPTransport(retries=1)
    client = httpx.AsyncClient(transport=transport)

    # Define the adapter to be used with httpx
    adapter = HTTPAdapter(max_retries=retry_strategy)

    # Create the httpx client with the defined adapter
    http = httpx.Client(base_url=url, adapter=adapter)

    # Make a GET request to the endpoint
    try:
        response = http.get("/resource")
        if response.status_code == 200:
            # Process the response data
            data = response.json()
            print(data)
        else:
            # Raise an exception for non-200 status codes
            raise Exception(
                "Request failed with status code {}".format(
                    response.status_code
                )
            )
    except Exception as e:
        # Handle the exception
        print("Request failed: {}".format(e))
