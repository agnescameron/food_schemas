from py2neo import Graph, Node, Relationship, NodeMatcher
import os
import cmd

uri = 'bolt://localhost:7687'
user = 'neo4j'
password = 'snacks'

def fill_schema():
	tx = graph_db.begin()

	collection_url = input("please provide a URL for the collection (e.g. https://github.com/agnescameron/food_schemas/collections_graph/<mm_dd_yy>): ")
	collection = Node("http://www.w3.org/ns/prov/Entity", type='collection', url=collection_url)
	tx.create(collection)


	agent_name = input("please enter your name: ")
	agent_email = input("please enter your email: ")
	agent_git = input("please enter your github username: ")
	agent = Node("http://www.w3.org/ns/prov/Agent", name=agent_name, email=agent_email, git=agent_git)
	tx.create(agent)


	script_repo = input("please enter the repository url for the script used to generate this collection: ")
	script_version = input("please enter the commit id: ")
	script = Node("http://underlay.org/ns/Script", repository=script_repo, version=script_version)
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