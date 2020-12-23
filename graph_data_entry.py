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
import scrapers.allrecipe_scraper as mod
import cleaning

with open("corpuses/meats.txt", "r") as am:
	global meats
	meats = am.readlines()
	meats = [i.replace("\n", "") for i in meats] 

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
	global meats
	recipe_id = 0
	#add recipe, author and source to the graph
	tx = graph_db.begin()
	recipeNode = matcher.match("http://underlay.org/Recipe", wasDerivedFromURL=recipe.source).first()
	if recipeNode == None:
		recipeNode = Node("http://underlay.org/Recipe", name=recipe.title, wasDerivedFromURL=recipe.source)
		print('source is', recipe.source)

	author = matcher.match("http://underlay.org/Author", name=recipe.author).first()
	if author == None:
		author = Node("http://underlay.org/Author", name=recipe.author)
		tx.create(author)

	rootURL = re.match(r'http?s:\/\/([a-z]+\.){1,}[a-z]+', recipe.source)[0]
	print(rootURL)

	source = matcher.match("http://underlay.org/Webpage", url=rootURL).first()
	if source == None:
		source = Node("http://underlay.org/Webpage", url=rootURL)
		tx.create(source)

	tx.create(recipeNode)
	auth_relation = Relationship(recipeNode, "http://underlay.org/hasAuthor", author)
	source_relation = Relationship(recipeNode, "http://underlay.org/hasSource", source)
	tx.create(auth_relation)
	tx.create(source_relation)
	tx.commit()


	for ingredient in recipe.ingredients:
		tx = graph_db.begin()
		original_ingredient = ingredient
		cleaned_ingredient = cleaning.clean_ingredient(ingredient)
		matched_ingredient = match_label(cleaned_ingredient, recipe.title)

		if matched_ingredient:
			ingredient = matcher.match("http://underlay.org/Ingredient", matchedFoodONEntity=matched_ingredient["label"]).first()
			if ingredient == None:
				meat = False
				for word in meats:
					if word in matched_ingredient["label"].lower(): meat = True
				print('1', cleaned_ingredient, '2', original_ingredient, '3', matched_ingredient["label"])
				ingredient = Node("http://underlay.org/Ingredient", hasCleanedName=cleaned_ingredient, matchedFoodONEntity=matched_ingredient["label"], hasEntryInRecipe=original_ingredient, containsMeat=meat)
				tx.create(ingredient)
			relation = Relationship(recipeNode, "http://underlay.org/hasIngredient", ingredient)
			tx.create(relation)
		tx.commit()

	for tag in recipe.tags:
		tx = graph_db.begin()

		tagNode = matcher.match("http://underlay.org/Tag", name=tag).first()
		if tagNode == None:
			tagNode = Node("http://underlay.org/Tag", name=tag)
			tx.create(tagNode)
		relation = Relationship(recipeNode, "http://underlay.org/hasAssociatedTag", tagNode)
		tx.create(relation)
		tx.commit()

if __name__ == "__main__":
	graph_db = Graph(uri, auth=(user, password))
	graph_db.delete_all()
	matcher = NodeMatcher(graph_db)

	recipes = mod.scrape()

	for index, recipe in enumerate(recipes):
		print('recipe number', index)
		insert_data(recipe)

