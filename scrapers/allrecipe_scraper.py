from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
from classes.recipe import Recipe
import requests
import re


with open("sources/allrecipe.txt", "r") as pr:
    global urls
    urls = pr.readlines()
    urls = [i.replace("\n", "") for i in urls] 
    
def scrape():
	global urls
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
			print('could not find ingredient')
   
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
			print('could not find directions')
   
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
