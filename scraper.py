#scrape a bunch of chickpea recipes
import pprint
import requests
import re
import json
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=2)

urls = [
	'https://www.archanaskitchen.com/karate-batate-puddi-sagale-recipe-konkani-style-bitter-gourd-and-potato-curry',
	'https://www.rotinrice.com/fuzzy-melon-and-glass-vermicelli-stir-fry-daai-ji-maa-gaa-neoi-%E5%A4%A7%E5%A7%A8%E5%AA%BD%E5%AB%81%E5%A5%B3/',
	'https://www.ruchiskitchen.com/punjabi-bharwan-karela-recipe/',
	# 'https://www.foodelicacy.com/steamed-bitter-gourd-stuffed-with-minced-pork/'
]

def match_label(ingredient):
	matches = requests.get('http://www.ebi.ac.uk/ols/api/search?q=(%s)&ontology=foodon' % ingredient)
	resJSON = matches.json()
	match = resJSON['response']['docs'][0]
	print(ingredient, 'matched with:', match['label'])
	# res = json.dumps(resJSON['response'][0], indent=2, sort_keys=True)
	# f = open("result.json","a")
	# f.write(res)
	# f.close()

open('result.json', 'w').close()

for url in urls:
	print('NEW RECIPE')
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
		print('recipe title', title.text.strip())

	print('this recipe has', len(ingredients), 'ingredients, and', len(directions), 'steps')


	for ingredient in ingredients:
		# print(ingredient.find())
		ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
		if ingredient_name:
			ingredient = ingredient_name
		ingredient_text = ingredient.text.strip()
		ingredient_text = re.sub(r'\s+', ' ', ingredient_text)
		# print(ingredient_text)
		match_label(ingredient_text)

	for direction in directions:
		# print(ingredient.find())
		direction_text = direction.text.strip()
		direction_text = re.sub(r'\s+', ' ', direction_text)
		# print( re.sub(r'\s+', ' ', direction_text))
