#scrape a bunch of recipes
import re
import json
import sqlite3
import os
import requests

# incorporating different scraping modules
# change the import statement to change the scraper
# e.g. import scrapers.nyt as mod
# e.g. import scrapers.manual as mod
import scrapers.allrecipe_scraper as mod
import cleaning

dirname = os.path.dirname(__file__)
db_file = 'recipe.sqlite'

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
	#add recipe info to db
	try:
		conn = sqlite3.connect(os.path.join(dirname, db_file))
		c = conn.cursor()
		with conn:
			c.execute("INSERT INTO 'http://underlay.org/ns/Recipe' ('http://underlay.org/ns/Recipe/name', 'http://underlay.org/ns/Recipe/author', 'http://underlay.org/ns/Recipe/source') VALUES (?, ?, ?)", (recipe.title, recipe.author, recipe.source))
			recipe_id = c.lastrowid
	except sqlite3.Error as e:
		print(e)


	for ingredient in recipe.ingredients:
		ingredient = cleaning.clean_ingredient(ingredient)
		matched_ingredient = match_label(ingredient, recipe.title)

		if matched_ingredient:
			try:
				conn = sqlite3.connect(os.path.join(dirname, db_file))
				c = conn.cursor()
				description = None
				row_id = 0

				if 'description' in matched_ingredient:
					description = matched_ingredient['description'][0]

				with conn:

					##insert or match with foodON entity
					row = c.execute('''
						SELECT * FROM "http://purl.obolibrary.org/obo/FOODON_00001002"
						WHERE "http://purl.obolibrary.org/obo/FOODON_00001002/iri" = ?''', (matched_ingredient['iri'],))
					row = row.fetchone()

					if row is None:
						c.execute('''
							INSERT INTO "http://purl.obolibrary.org/obo/FOODON_00001002" ("http://purl.obolibrary.org/obo/FOODON_00001002/iri", "http://purl.obolibrary.org/obo/FOODON_00001002/label") 
							VALUES (?,?)''', (matched_ingredient['iri'] , matched_ingredient['label'] ))
						foodON_id = c.lastrowid
						conn.commit()
					else:
						foodON_id = row[0]

					##insert the ingredient
					c.execute('''
						INSERT INTO "http://underlay.org/ns/Ingredient" ("http://underlay.org/ns/Ingredient/hasCleanedName", "http://underlay.org/ns/Ingredient/hasNameInRecipe") 
						VALUES (?,?)''', (matched_ingredient['iri'] , matched_ingredient['label'] ))
					ingredient_id = c.lastrowid

					##match ingredient to recipe
					c.execute('''
						INSERT INTO "http://underlay.org/ns/Recipe/hasIngredient" ("http://underlay.org/ns/source", "http://underlay.org/ns/target") 
						VALUES (?,?)''', (recipe_id, ingredient_id))

					##match ingredient to entity
					c.execute('''
						INSERT INTO "http://underlay.org/ns/Ingredient/matchesFoodONEntity" ("http://underlay.org/ns/source", "http://underlay.org/ns/target") 
						VALUES (?,?)''', (ingredient_id, foodON_id))

					conn.commit()

			except sqlite3.Error as e:
				print('sqlite', e)
			finally:
				if conn:
					conn.close()

if __name__ == "__main__":

	#init db w foreign key constraints
	try:
		conn = sqlite3.connect(os.path.join(dirname, db_file))
		c = conn.cursor()
		with conn:

			#table for recipes
			c.execute('''CREATE TABLE IF NOT EXISTS "http://underlay.org/ns/Recipe" ( id INTEGER PRIMARY KEY, "http://underlay.org/ns/Recipe/author" text not null, "http://underlay.org/ns/Recipe/name" text not null, "http://underlay.org/ns/Recipe/source" text not null )''')

			#table for ingredients
			c.execute('''CREATE TABLE IF NOT EXISTS "http://underlay.org/ns/Ingredient" ( id INTEGER PRIMARY KEY, "http://underlay.org/ns/Ingredient/hasCleanedName" text not null, "http://underlay.org/ns/Ingredient/hasNameInRecipe" text not null )''')

			#table for foodON entities
			c.execute('''CREATE TABLE IF NOT EXISTS `http://purl.obolibrary.org/obo/FOODON_00001002` ( id INTEGER PRIMARY KEY, "http://purl.obolibrary.org/obo/FOODON_00001002/iri" text not null, "http://purl.obolibrary.org/obo/FOODON_00001002/label" text not null )''')

			#table for recipe/ingredient relationship
			c.execute('''CREATE TABLE IF NOT EXISTS "http://underlay.org/ns/Recipe/hasIngredient" ( id INTEGER PRIMARY KEY, "http://underlay.org/ns/source" integer not null references "http://underlay.org/ns/Recipe", "http://underlay.org/ns/target" integer not null references "http://underlay.org/ns/Ingredient" )''')

			#table for ingredient/entity match
			c.execute('''CREATE TABLE IF NOT EXISTS "http://underlay.org/ns/Ingredient/matchesFoodONEntity" ( id INTEGER PRIMARY KEY, "http://underlay.org/ns/source" integer not null references "http://underlay.org/ns/Ingredient", "http://underlay.org/ns/target" integer not null references "http://purl.obolibrary.org/obo/FOODON_00001002" )''')

			c.execute("PRAGMA foreign_keys = ON;")

			conn.commit()
	except sqlite3.Error as e:
		print(e)

	recipes = mod.scrape()

	#each recipe gets directions and ingredients
	# recipes = ws.scrape()

	for index, recipe in enumerate(recipes):
		print('recipe number', index)
		insert_data(recipe)
