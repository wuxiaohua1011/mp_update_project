from maggma.stores import JSONStore  # THIS IS ALREADY maggma
from endpoint_cluster import EndpointCluster
from models import MaterialModel
import graphene
from models import Material
from graphene import ObjectType, String, Schema

store = JSONStore("../data/more_mats.json")
store.connect()


# materialEndpointCluster = EndpointCluster(store, MaterialModel)
# materialEndpointCluster.run()


class Query(graphene.ObjectType):
    materials = graphene.List(Material)

    hello = String(name=String(default_value="stranger"))
    goodbye = String()

    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response
    def resolve_hello(root, info, name):
        cursor = store.query_one()
        cursor.pop("_id")
        cursor.pop("composition")
        cursor.pop("composition_reduced")
        cursor.pop("_bt")
        # print(cursor)
        # print([MaterialModel(**cursor)])
        return [Material(**cursor)]

    def resolve_materials(root, info):
        cursor = store.query_one()
        # materialModel = MaterialModel(**cursor)
        print(cursor)
        # print([Material(**cursor)])
        return "materials"

schema = graphene.Schema(query=Query)

query_material = '{ materials }'
result = schema.execute(query_material)
print(result.data)

# query_str = '{goodbye}'
# result = schema.execute(query_str)
# print(result.data)
# query_string = '{ hello }'
# result = schema.execute(query_string)
# print(result.data['hello'])
# # "Hello stranger"
#
# # or passing the argument in the query
# query_with_argument = '{ hello(name: "GraphQL") }'
# result = schema.execute(query_with_argument)
# print(result.data['hello'])


# query = '{material}'
# result = schema.execute(query)
# import json
#
# print(json.dumps(result.data, indent=2))
