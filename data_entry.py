#scrape a bunch of chickpea recipes
import pprint
import re
import json
import toml
import sqlite3
import os
import requests

import web_scraper as ws

dirname = os.path.dirname(__file__)
db_file = 'recipe-reduced.sqlite'
pp = pprint.PrettyPrinter(indent=2)

def match_label(ingredient, title):
	matches = requests.get('http://www.ebi.ac.uk/ols/api/search?q=(%s)&ontology=foodon' % ingredient)
	resJSON = matches.json()
	if len(resJSON['response']['docs']) > 0:
		match = resJSON['response']['docs'][0]
		print(ingredient, 'matched with:', match['label'])
		return match
	else:
		return None

#init db w foreign key constraints
try:
	conn = sqlite3.connect(os.path.join(dirname, db_file))
	c = conn.cursor()
	with conn:
		c.execute("PRAGMA foreign_keys = ON;")
except sqlite3.Error as e:
	print(e)


def insert_data(recipe):
	#add recipe info to db
	try:
		conn = sqlite3.connect(os.path.join(dirname, db_file))
		c = conn.cursor()
		with conn:
			c.execute("INSERT INTO 'https://schema.org/Recipe' ('https://schema.org/Recipe/name', 'https://schema.org/Recipe/url') VALUES (?, ?)", (recipe.title, recipe.url))
			recipe_id = c.lastrowid
	except sqlite3.Error as e:
		print(e)


	for ingredient in recipe.ingredients:
		ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
		if ingredient_name:
			ingredient = ingredient_name
		ingredient_text = ingredient.text.strip()
		ingredient_text = re.sub(r'\s+', ' ', ingredient_text)

		matched_ingredient = match_label(ingredient_text, recipe.title)
		if matched_ingredient:
			try:
				conn = sqlite3.connect(os.path.join(dirname, db_file))
				c = conn.cursor()
				description = None
				row_id = 0

				if 'description' in matched_ingredient:
					description = matched_ingredient['description'][0]
				with conn:

					##insert the ingredients
					row = c.execute('''
						SELECT * FROM "https://schema.org/Ingredient"
						WHERE "https://schema.org/Ingredient/name" = ?''', (matched_ingredient['label'],))
					row = row.fetchone()

					if row is None:
						c.execute('''
							INSERT INTO "https://schema.org/Ingredient" ("https://schema.org/Ingredient/description", "https://schema.org/Ingredient/id", "https://schema.org/Ingredient/name") 
							VALUES (?,?,?)''', (description , matched_ingredient['iri'] , matched_ingredient['label'] ))
						row_id = c.lastrowid
						conn.commit()
					else:
						row_id = row[0]

					##now, add to the ingredient list
					c.execute('''
						INSERT INTO "https://schema.org/Recipe/Ingredient" ("http://underlay.org/ns/source", "http://underlay.org/ns/target") 
						VALUES (?,?)''', (recipe_id, row_id))

			except sqlite3.Error as e:
				print('sqlite', e)
			finally:
				if conn:
					conn.close()

	for direction in recipe.directions:
		direction_text = direction.text.strip()
		direction_text = re.sub(r'\s+', ' ', direction_text)


if __name__ == "__main__":
#each recipe gets directions and ingredients
	recipes = ws.scrape()

	for recipe in recipes:
		insert_data(recipe)

