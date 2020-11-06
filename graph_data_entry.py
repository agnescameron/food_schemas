from py2neo import Graph, Node, Relationship, NodeMatcher
import os
import sqlite3

uri = 'bolt://localhost:7687'
user = 'neo4j'
password = 'snacks'

dirname = os.path.dirname(__file__)
db_file = 'recipe.sqlite'

graph_db = Graph(uri, auth=(user, password))


conn = sqlite3.connect(os.path.join(dirname, db_file))
c = conn.cursor()
with conn:
	c.execute('SELECT * FROM "https://schema.org/Recipe"')
	rows = c.fetchall()
	for row in rows:
		tx = graph_db.begin()
		recipe = Node("Recipe", name=row[2], index=row[0])
		tx.create(recipe)
		tx.commit()

	c.execute('SELECT * FROM "https://schema.org/Ingredient"')
	rows = c.fetchall()
	for row in rows:
		tx = graph_db.begin()
		recipe = Node("Ingredient", name=row[3], index=row[0])
		tx.create(recipe)
		tx.commit()

	c.execute('SELECT * FROM "https://schema.org/Recipe/ingredient"')
	rows = c.fetchall()
	matcher = NodeMatcher(graph_db)
	for index, row in enumerate(rows):
		tx = graph_db.begin()

		recipe = matcher.match("Recipe", index=row[1]).first()
		ingredient = matcher.match("Ingredient", index=row[2]).first()

		relation = Relationship(recipe, "hasIngredient", ingredient)
		tx.create(relation)
		tx.commit()