import requests
from flask import g


def get_default_header() -> dict:
    """
    Returns the default headers for HTTP requests, including the authorization token.

    Returns:
        dict: A dictionary containing the default headers.
    """
    return {
        "Authorization": f"Bearer {g.access_token}",
        "Content-Type": "application/json"
    }

def post_request(url: str, data: dict, headers: dict = None) -> requests.Response:
    """
    Sends a POST request to the specified URL with the given data and headers.

    Args:
        url (str): The URL to send the POST request to.
        data (dict): The data to be sent in the POST request.
        headers (dict, optional): Optional headers to include in the request.

    Returns:
        requests.Response: The response object from the POST request.
    """
    if headers is None:
        headers = get_default_header()
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response

def get_request(url: str, headers: dict = None, data: dict = None) -> requests.Response:
    """
    Sends a GET request to the specified URL with the given headers.

    Args:
        url (str): The URL to send the GET request to.
        headers (dict, optional): Optional headers to include in the request.

    Returns:
        requests.Response: The response object from the GET request.
    """
    if headers is None:
        headers = get_default_header()
    response = requests.get(url, headers=headers, json=data)
    response.raise_for_status()
    return response