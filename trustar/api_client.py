from math import ceil
import requests
from requests.exceptions import HTTPError
import time


class ApiClient(object):
    """
    This class is used to make HTTP requests to the TruStar API.
    """

    INVALID_TOKEN_MESSAGES = (
        "Expired oauth2 access token",
        "Invalid oauth2 access token",
    )

    _instance = None

    def __init__(self, config):
        self.config = config
        self.token = None

    def __new__(cls, config, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)

        return cls._instance

    def _refresh_token(self):
        """
        Refreshes oauth token.
        """
        client_auth = requests.auth.HTTPBasicAuth(
            self.config.api_key, self.config.api_secret
        )
        post_data = {"grant_type": "client_credentials"}
        endpoint = self.config.request_details.get("auth_endpoint")
        response = requests.post(
            endpoint, auth=client_auth, data=post_data, verify=True
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def _get_token(self):
        """
        Retrieves token.
        :returns: oauth token.
        """
        if self.token is None:
            self._refresh_token()

        return self.token

    def _token_is_expired(self, response):
        """
        Checks if an HTTP response failed due to a expired oauth token.

        :param response: HTTP response object.
        :returns: True or False indicating if the response failed.
        """
        if response.status_code != 400:
            return False

        body = response.json()
        return str(body.get("error_description")) in self.INVALID_TOKEN_MESSAGES

    def _get_headers(self, method):
        """
        Forms the HTTP headers according to user's config and method.

        :param method: HTTP method.
        :returns: HTTP headers as dict.
        """
        headers = {
            "Authorization": "Bearer " + self._get_token(),
            "Client-Metatag": self.config.client_metatag,
        }

        client_type = self.config.request_details.get("client_type")
        client_version = self.config.request_details.get("client_version")

        if client_type:
            headers["Client-Type"] = client_type

        if client_version:
            headers["Client-Version"] = client_version

        if method in ("POST", "PUT"):
            headers["Content-Type"] = "application/json"

        return headers

    def _request(self, method, endpoint, payload=None, params=None):
        """
        Generic request method to handle diffent HTTP requests.

        :param method: HTTP request method.
        :param endpoint: URL to be requested.
        :param payload: payload to include in the request.
        :param params: params to include in the request.

        :returns: response object.
        """
        retry = self.config.request_details.get("retry")
        attempted = False

        while not attempted or retry:
            headers = self._get_headers(method)
            response = requests.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=payload,
                params=params,
            )
            if response.status_code == requests.codes.ok:
                return response

            if self._token_is_expired(response):
                self._refresh_token()

            elif retry and response.status_code == requests.codes.too_many:
                retry = self._sleep(response)

            else:
                message = "{} {} Error (Trace-Id: {})".format(
                    response.status_code,
                    "Client" if response.status_code < 500 else "Server",
                    self._get_trace_id(response),
                )
                raise HTTPError(request=message, response=response)

    def _sleep(self, response):
        """
        Sleeps if response is a 429 and wait time is lower the max_wait_time in config.

        :param response: HTTP response object.
        :returns: True or False indicating if it is necessary to keep trying.
        """
        wait_time = ceil(response.json().get("waitTime") / 1000)
        keep_trying = wait_time <= self.config.request_details.get("max_wait_time")
        if keep_trying:
            time.sleep(wait_time)

        return keep_trying

    @staticmethod
    def _get_trace_id(response):
        """
        Fetches the trace id from the HTTP response header.

        :param response: HTTP response object.
        :returns: TruSTAR Trace-Id if found.
        """
        trace_id = response.headers.get("Trace-Id")
        return trace_id if trace_id is not None else None

    def fetch(self, query):
        payload = query.params.serialize() if query.params else None
        return self._request(
            query.method.name, query.endpoint, payload, params=query.query_string
        )
