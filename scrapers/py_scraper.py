from recipe_scrapers import scrape_me
from scrapers.recipe import Recipe

urls = [
	'https://www.seriouseats.com/recipes/2016/05/okonomiyaki-japanese-pancake-cabbage-recipe.html',
	'https://www.chopstickchronicles.com/osaka-okonomiyaki/',
	'https://www.justonecookbook.com/okonomiyaki/',
	'https://www.thespruceeats.com/japanese-okonomiyaki-recipe-2031053',
	'https://www.yummly.com/recipe/Japanese-pancakes-_okonomiyaki_-306541?prm-v1',
	'https://www.food.com/recipe/okonomiyaki-532674'
]

def scrape():
	recipes = []
	for url in urls:
		# Q: What if the recipe site I want to extract information from is not listed below?
		# A: You can give it a try with the wild_mode option! If there is Schema/Recipe available it will work just fine.
		try:
			scraper = scrape_me(url, wild_mode=True)
			if scraper:
				recipe = Recipe(scraper.title(), scraper.ingredients(), scraper.instructions(), url, scraper.author())
				recipes.append(recipe)
		except:
			print('no recipe schema for ', url)

	return recipes
