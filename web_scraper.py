from bs4 import BeautifulSoup
from recipe import Recipe
import requests
import re

urls = [
	'https://www.archanaskitchen.com/karate-batate-puddi-sagale-recipe-konkani-style-bitter-gourd-and-potato-curry',
	'https://www.rotinrice.com/fuzzy-melon-and-glass-vermicelli-stir-fry-daai-ji-maa-gaa-neoi-%E5%A4%A7%E5%A7%A8%E5%AA%BD%E5%AB%81%E5%A5%B3/',
	'https://www.ruchiskitchen.com/punjabi-bharwan-karela-recipe/'
]

def scrape():
	recipes = []

	for url in urls:
		recipe_id = 0
		page = requests.get(url)

		soup = BeautifulSoup(page.content, 'html.parser')

		title = soup.find('h1', {'class': re.compile(r'name|title|heading(?!.*(site|website))')})

		# look for a div where the classname contains ingredients and get the list from there
		ingredient_container = soup.find('div', {'class': re.compile(r'(?<!direction.)ingredient(?!.*(direction|instruction|steps))')})
		ingredients = ingredient_container.find_all('li')

		for ingredient in ingredients:
			ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
			if ingredient_name:
				ingredient = ingredient_name
			ingredient = ingredient.text.strip()
			ingredient = re.sub(r'\s+', ' ', ingredient)

		#look for a div where the classname contains ingredients and get the list from there
		direction_container = soup.find('div', {'class': re.compile(r'(?<!ingredient.)direction|instruction|steps(?!.*(ingredient|description))')})
		directions = direction_container.find_all('li')

		for direction in directions:
			direction = direction.text.strip()
			direction = re.sub(r'\s+', ' ', direction)


		if title:
			print('RECIPE:', title.text.strip())
			title = title.text.strip()
		else:
			title = None

		recipe = Recipe(title, ingredients, directions, url)
		recipes.append(recipe)
		print('this recipe has', len(ingredients), 'ingredients, and', len(directions), 'steps')

	return recipes