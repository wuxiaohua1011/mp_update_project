import pydantic
import uuid

class PersonModel(pydantic.BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str

import graphene
from graphene_pydantic import PydanticObjectType

class Person(PydanticObjectType):
    class Meta:
        model = PersonModel
        # only return specified fields
        # only_fields = ("first_name",)
        # exclude specified fields
        exclude_fields = ("id",)


def get_people():
    return [PersonModel(id=uuid.uuid4(),
                        first_name="michael",
                        last_name="wu"),
            PersonModel(id=uuid.uuid4(),
                        first_name="jerry",
                        last_name="ding")
            ]


class Query(graphene.ObjectType):
    people = graphene.List(Person)

    def resolve_people(self, info):
        return get_people()  # function returning `PersonModel`s

schema = graphene.Schema(query=Query)

query = '''
    query {
      people {
        firstName,
        lastName
      }
    }
'''
result = schema.execute(query)
import json
print(json.dumps(result.data, indent=2))

