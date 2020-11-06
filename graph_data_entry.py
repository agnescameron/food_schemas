#scrape a bunch of recipes
import re
import json
import toml
from py2neo import Graph, Node, Relationship, NodeMatcher
import os
import requests

uri = 'bolt://localhost:7687'
user = 'neo4j'
password = 'snacks'

# incorporating different scraping modules
# change the import statement to change the scraper
# e.g. import scrapers.nyt as mod
# e.g. import scrapers.manual as mod
import scrapers.nyt as mod
import cleaning

graph_db = Graph(uri, auth=(user, password))
matcher = NodeMatcher(graph_db)

def match_label(ingredient, title):
	matches = requests.get('http://www.ebi.ac.uk/ols/api/search?q=(%s)&ontology=foodon' % ingredient)
	resJSON = matches.json()
	if len(resJSON['response']['docs']) > 0:
		match = resJSON['response']['docs'][0]
		print(ingredient, 'matched with:', match['label'])
		return match
	else:
		return None

def insert_data(recipe):
	recipe_id = 0
	#add recipe, author and source to the graph
	tx = graph_db.begin()
	recipeNode = Node("Recipe", name=recipe.title)

	author = matcher.match("Author", name=recipe.author).first()
	if author == None:
		author = Node("Author", name=recipe.author)
		tx.create(author)

	source = matcher.match("Source", url=recipe.source).first()
	if source == None:
		source = Node("Source", url=recipe.source)
		tx.create(source)

	tx.create(recipeNode)
	auth_relation = Relationship(recipeNode, "hasAuthor", author)
	source_relation = Relationship(recipeNode, "hasSource", source)
	tx.create(auth_relation)
	tx.create(source_relation)
	tx.commit()


	for ingredient in recipe.ingredients:
		tx = graph_db.begin()
		ingredient = cleaning.clean_ingredient(ingredient)
		matched_ingredient = match_label(ingredient, recipe.title)

		if matched_ingredient:
			ingredient = matcher.match("Ingredient", name=matched_ingredient["label"]).first()
			if ingredient == None:
				ingredient = Node("Ingredient", name=matched_ingredient["label"])
				tx.create(ingredient)
			relation = Relationship(recipeNode, "hasIngredient", ingredient)
			tx.create(relation)
		tx.commit()

	for cuisine in recipe.cuisines:
		tx = graph_db.begin()

		cuisineNode = matcher.match("Cuisine", name=cuisine).first()
		if cuisineNode == None:
			cuisineNode = Node("Cuisine", name=cuisine)
			tx.create(cuisineNode)
		relation = Relationship(recipeNode, "hasAssociatedCuisine", cuisineNode)
		tx.create(relation)
		tx.commit()

if __name__ == "__main__":

	recipes = mod.scrape()

	for index, recipe in enumerate(recipes):
		print('recipe number', index)
		insert_data(recipe)

