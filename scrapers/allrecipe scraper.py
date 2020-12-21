from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
from classes.recipe import Recipe
import requests
import re

urls = [
	'https://www.allrecipes.com/recipe/262725/polish-borscht/',
    'https://www.allrecipes.com/recipe/84450/ukrainian-red-borscht-soup/'
	
]

def scrape():
	recipes = []

	for url in urls:
		recipe_id = 0
		page = requests.get(url)

		soup = BeautifulSoup(page.content, 'html.parser')

		title = soup.find('h1')

		# look for a div where the classname contains ingredients and get the list from there
		ingredient_container = soup.find('div', {'class':'recipe-shopper-wrapper'})
		ingredients = []
		try:
			ingredients = ingredient_container.find_all('li')
		except:
			print('steady')
   
		for index, ingredient in enumerate(ingredients):
			ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
			if ingredient_name:
				ingredient = ingredient_name
			ingredient = ingredient.text.strip()
			ingredients[index] = re.sub(r'\s+', ' ', ingredient)


		#look for a div where the classname contains ingredients and get the list from there
		direction_container = soup.find('section', {'class': 'recipe-instructions'})
		directions = []
		try:
			directions = direction_container.find_all('li')
		except:
			print('i no dey')
   
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
