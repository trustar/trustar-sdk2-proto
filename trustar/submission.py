from __future__ import unicode_literals

from .base import fluent, Methods, Params, Param, get_timestamp
from .query import Query


class SubmissionsParamSerializer(Params):
    def serialize(self):
        return {n.key: n.value for n in self}


@fluent
class Submission(object):

    NEW_SUBMISSION_MANDATORY_FIELDS = ("title", "content", "enclaveGuid")
    path = "/submissions/indicators"

    def __init__(self, config=None):
        self.config = config
        self.params = SubmissionsParamSerializer()
        for func in (self.set_tags,):
            func()

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
        self.set_custom_param("enclaveGuid", enclave_id)

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

    def set_tags(self, tags=None):
        """Adds tags param to set of params.

        :param tags: field value.
        :returns: self.
        """
        if not tags:
            tags = []
        self.set_custom_param("tags", tags)

    def set_id_type_as_external(self, external=False):
        """Sets idType to EXTERNAL if 'external' parameter is True.
        
        :param external: boolean indicating if id is external or not
        :returns: self.
        """
        if external:
            self.set_custom_param("idType", "EXTERNAL")

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
            timestamp = get_timestamp(timestamp)

        self.set_custom_param("timestamp", timestamp)

    def set_raw_content(self, raw_content):
        """Adds rawContent param to set of params.

        :param raw_content: field value.
        :returns: self.
        """
        self.set_custom_param("rawContent", raw_content)

    def set_submission_version(self, version):
        """Adds submissionVersion param to set of params.

        :param version: field value.
        :returns: self.
        """
        self.set_custom_param("submissionVersion", version)

    @property
    def query_params(self):
        return {
            p.key: p.value
            for p in self.params
            if p.key in ("id", "idType", "enclaveGuid", "includeContent")
        }

    def get_by_external_id(self):
        """Returns True if params are set to retrieve a submission by external id"""
        return "idType" in self.params and "externalId" in self.params

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
        query_string = self.query_params
        if self.get_by_external_id():
            query_string["id"] = self.params.get("externalId")

        return (
            self.create_query(Methods.GET)
            .set_query_string(query_string)
            .fetch_one()
        )

    def update(self):
        """Updates a submission according to query_params set before."""
        return (
            self.create_query(Methods.PUT)
            .set_query_string(self.query_params)
            .fetch_one()
        )
