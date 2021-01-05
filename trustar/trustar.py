from __future__ import absolute_import
import json
from os import name

from .indicators import SearchIndicator
from .submission import Submission
from .trustar_enums import TruStarUrls
from .version import __version__


class TruStar:

    DEFAULTS = {
        "auth_endpoint": TruStarUrls.AUTH_TOKEN.value,
        "api_endpoint": TruStarUrls.API.value,
        "station": TruStarUrls.STATION.value,
        "client_type": "PYTHON_SDK",
        "client_version": __version__,
        "verify": True,
        "retry": True,
        "max_wait_time": 60,
        "http_proxy": None,
        "https_proxy": None,
    }

    def __init__(self, api_key, api_secret, client_metatag, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_metatag = client_metatag
        self.request_details = self.DEFAULTS.copy()
        self.request_details.update(kwargs)

    @classmethod
    def config_from_file(cls, config_file_path, config_role):
        with open(config_file_path, "r") as f:
            config_file = json.load(f)

        config = config_file.get(config_role)
        if not config:
            raise AttributeError(
                "{} role was not found in {} file".format(config_role, config_file_path)
            )

        return cls(**config)

    def indicators(self):
        # TODO add condig
        return SearchIndicator(self)

    def submission(self):
        return Submission(self)
