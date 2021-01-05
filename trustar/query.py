from .api_client import ApiClient
from .base import Param, fluent


@fluent
class Query:

    def __init__(self, config, endpoint, method, params=None, query_string=None):
        self.config = config
        self.endpoint = endpoint
        self.method = method
        self.params = params
        self.query_string = query_string
        self.stop = False
        self.api = ApiClient(self.config)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def set_query_string(self, query_string):
        self.query_string = query_string

    def set_params(self, params):
        self.params = params

    def _update_params_from_response(self, response):
        if response["responseMetadata"]["nextCursor"] != "":
            cursor = Param("cursor", response["responseMetadata"]["nextCursor"])
            self.params.add(cursor)
        else:
            self.stop = True

    def next(self):
        if not self.stop:
            result = self.api.fetch(self)
            self._update_params_from_response(result.json())
            return result
        else:
            raise StopIteration

    def fetch_one(self):
        return self.api.fetch(self)
