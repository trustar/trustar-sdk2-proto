from __future__ import unicode_literals

from model_base import Base
from base import fluent, Params, Param, get_timestamp
from trustar_enums import AttributeTypes, ObservableTypes


class EntitySerializer(Params):
    def serialize(self):
        serialized = {}
        for n in self:
            serialized[n.key] = n.value
        return serialized


@fluent
class Entity(Base):

    def __init__(self, validator, entity_type, value, alias='entity'):
        self.params = EntitySerializer()
        if entity_type not in validator.members():
            raise AttributeError(
                "Attribute type should be in the following: {}".format(
                    list(validator.members())
                ))
        self.key = alias
        self.set_custom_param(self.key, {"value": value, "type": entity_type})

    @classmethod
    def attribute(cls, entity_type, value):
        return Entity(AttributeTypes, entity_type, value)

    @classmethod
    def observable(cls, entity_type, value):
        return Entity(ObservableTypes, entity_type, value)

    def set_valid_from(self, valid_from):
        if not isinstance(valid_from, int):
            raise AttributeError("timestamp must be an int")

        self.set_custom_param("validFrom", valid_from)

    def set_valid_to(self, valid_to):
        if not isinstance(valid_to, int):
            raise AttributeError("timestamp must be an int")
        self.set_custom_param("validTo", valid_to)

    def set_confidence_score(self, confidence_score):
        # TODO validations
        self.set_custom_param("confidenceScore", confidence_score)

    def set_malicious_score(self, malicious_score):
        self.set_custom_param("maliciousScore", malicious_score)

    def set_custom_param(self, key, value):
        param = Param(key=key, value=value)
        self.params.add(param)

    def serialize(self):
        return self.params.serialize()
