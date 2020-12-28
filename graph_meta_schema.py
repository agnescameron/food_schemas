from py2neo import Graph, Node, Relationship, NodeMatcher
import os

uri = 'bolt://localhost:7687'
user = 'neo4j'
password = 'snacks'

def fill_schema():
	tx = graph_db.begin()
	collection = Node("http://www.w3.org/ns/prov/Entity", type='collection', url='https://github.com/agnescameron/food_schemas/tree/master/collections_graph/12_28_20')
	tx.create(collection)

	agent = Node("http://www.w3.org/ns/prov/Agent", name='Agnes Cameron', url='https://github.com/agnescameron')
	tx.create(agent)

	script = Node("http://underlay.org/ns/Script", repository='https://github.com/agnescameron/food_schemas/', version='50c4b35')
	tx.create(script)

	generated_relation = Relationship(collection, "http://www.w3.org/ns/prov/WasGeneratedBy",script)
	attribution_relation = Relationship(collection, "http://www.w3.org/ns/prov/WasAttributedTo", agent)
	tx.create(generated_relation)
	tx.create(attribution_relation)

	tx.commit()

if __name__ == "__main__":
	graph_db = Graph(uri, auth=(user, password))
	graph_db.delete_all()
	matcher = NodeMatcher(graph_db)

	fill_schema()