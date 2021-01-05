from __future__ import unicode_literals

from .base import fluent, Methods, Params, Param, get_timestamp
from .query import Query


class SubmissionsParamSerializer(Params):
    def serialize(self):
        serialized = {}
        for n in self:
            serialized[n.key] = n.value
        return serialized


@fluent
class Submission(object):

    NEW_SUBMISSION_MANDATORY_FIELDS = ("title", "content", "enclaveId")
    path = "/submissions/indicators"

    def __init__(self, config):
        self.config = config
        self.params = SubmissionsParamSerializer()

    @property
    def endpoint(self):
        return self.config.request_details.get("api_endpoint") + self.path

    def set_custom_param(self, key, value):
        """Adds a new param to set of params."""
        param = Param(key=key, value=value)
        self.params.add(param)

    def set_id(self, submission_id):
        """Adds id param to set of params.

        :param submission_id: field value.
        :returns: self.
        """
        self.set_custom_param("id", submission_id)

    def set_title(self, title):
        """Adds title param to set of params.

        :param title: field value.
        :returns: self.
        """
        self.set_custom_param("title", title)

    def set_content_indicators(self, indicators):
        """Adds content param to set of params.

        :param indicators: field value. List of Indicator objects.
        :returns: self.
        """
        indicators = [i.serialize() for i in indicators]
        content = {"indicators": indicators}
        self.set_custom_param("content", content)

    def set_enclave_id(self, enclave_id):
        """Adds enclaveId param to set of params.

        :param enclave_id: field value.
        :returns: self.
        """
        self.set_custom_param("enclaveId", enclave_id)

    def set_external_id(self, external_id):
        """Adds externalId param to set of params.

        :param external_id: field value.
        :returns: self.
        """
        self.set_custom_param("externalId", external_id)

    def set_external_url(self, external_url):
        """Adds externalUrl param to set of params.

        :param external_url: field value.
        :returns: self.
        """
        self.set_custom_param("externalUrl", external_url)

    def set_tags(self, tags):
        """Adds tags param to set of params.

        :param tags: field value.
        :returns: self.
        """
        self.set_custom_param("tags", tags)

    def set_include_content(self, content=False):
        """
        Adds includeContent param to set of params.

        :param content: field value.
        :returns: self.
        """
        self.set_custom_param("includeContent", content)

    def set_timestamp(self, timestamp):
        """Adds timestamp param to set of params.

        :param timestamp: field value.
        :returns: self.
        """
        if not isinstance(timestamp, int):
            raise AttributeError("timestamp must be an int")

        self.set_custom_param("timestamp", timestamp)

    def set_raw_content(self, raw_content):
        """Adds rawContent param to set of params.

        :param raw_content: field value.
        :returns: self.
        """
        self.set_custom_param("rawContent", raw_content)

    @property
    def query_params(self):
        params = {}
        for p in self.params:
            if p in ("id", "enclaveId", "includeContent"):
                params[p.key] = p.value
        return params

    def create_query(self, method):
        """Returns a new instance of a Query object according config, endpoint and method."""
        return Query(self.config, self.endpoint, method)

    def create(self):
        """Creates a new submission according to params set before."""
        for k in self.NEW_SUBMISSION_MANDATORY_FIELDS:
            if k not in self.params:
                raise AttributeError("{} field should be in your submission".format(k))
        return self.create_query(Methods.POST).set_params(self.params).fetch_one()

    def delete(self):
        """Deletes a submission according to query_params set before."""
        return (
            self.create_query(Methods.DELETE)
            .set_query_string(self.query_params)
            .fetch_one()
        )

    def get(self):
        """Retrieves a submission according to query_params set before."""
        return (
            self.create_query(Methods.GET)
            .set_query_string(self.query_params)
            .fetch_one()
        )

    def update(self):
        """Updates a submission according to query_params set before."""
        return (
            self.create_query(Methods.PUT)
            .set_query_string(self.query_params)
            .fetch_one()
        )
