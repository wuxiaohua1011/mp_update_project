import graphene
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from pydantic import BaseModel
from graphene_pydantic import PydanticObjectType
import typing


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name


app = FastAPI()
app.add_route("/", GraphQLApp(schema=graphene.Schema(query=Query)))
