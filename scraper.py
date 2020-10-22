#scrape a bunch of chickpea recipes
import pprint
import requests
import re
import json
from bs4 import BeautifulSoup
import toml
import sqlite3
import os

dirname = os.path.dirname(__file__)
db_file = 'recipe-reduced.sqlite'
pp = pprint.PrettyPrinter(indent=2)

urls = [
	'https://www.archanaskitchen.com/karate-batate-puddi-sagale-recipe-konkani-style-bitter-gourd-and-potato-curry',
	'https://www.rotinrice.com/fuzzy-melon-and-glass-vermicelli-stir-fry-daai-ji-maa-gaa-neoi-%E5%A4%A7%E5%A7%A8%E5%AA%BD%E5%AB%81%E5%A5%B3/',
	'https://www.ruchiskitchen.com/punjabi-bharwan-karela-recipe/'
]

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

for url in urls:
	recipe_id = 0
	page = requests.get(url)

	soup = BeautifulSoup(page.content, 'html.parser')

	title = soup.find('h1', {'class': re.compile(r'name|title|heading(?!.*(site|website))')})

	# look for a div where the classname contains ingredients and get the list from there
	ingredient_container = soup.find('div', {'class': re.compile(r'(?<!direction.)ingredient(?!.*(direction|instruction|steps))')})
	ingredients = ingredient_container.find_all('li')

	#look for a div where the classname contains ingredients and get the list from there
	direction_container = soup.find('div', {'class': re.compile(r'(?<!ingredient.)direction|instruction|steps(?!.*(ingredient|description))')})
	directions = direction_container.find_all('li')

	if title:
		print('RECIPE:', title.text.strip())
		title = title.text.strip()
	else:
		title = None

	print('this recipe has', len(ingredients), 'ingredients, and', len(directions), 'steps')

	#add recipe info to db
	try:
		conn = sqlite3.connect(os.path.join(dirname, db_file))
		c = conn.cursor()
		with conn:
			c.execute("INSERT INTO 'https://schema.org/Recipe' ('https://schema.org/Recipe/name', 'https://schema.org/Recipe/url') VALUES (?, ?)", (title, url))
			recipe_id = c.lastrowid
	except sqlite3.Error as e:
		print(e)


	for ingredient in ingredients:
		ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
		if ingredient_name:
			ingredient = ingredient_name
		ingredient_text = ingredient.text.strip()
		ingredient_text = re.sub(r'\s+', ' ', ingredient_text)

		matched_ingredient = match_label(ingredient_text, title)
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

	for direction in directions:
		direction_text = direction.text.strip()
		direction_text = re.sub(r'\s+', ' ', direction_text)


	print('\n\n\n\n\n')
