from pyquery import PyQuery as pq
from scrapers.recipe import Recipe
import re
import os

def scrape():
	#try for 1000 files
	recipes = []
	directory = os.listdir( 'nyt_recipes/' )

	for index, file in enumerate(directory):
		# print(index, file)
		if index < 1000:
			d = pq(filename='nyt_recipes/'+file)
			ingredients = []
			directions = []

			url = d('meta[property="og:url"]').attr("content")

			# print(d)
			title = d(".recipe-title").text()
			print(title)

			for el in d("span.ingredient-name"):
				ingredients.append(d(el).text())

			for el in d("ol.recipe-steps > li"):
				directions.append(d(el).text())

			recipe = Recipe(title, ingredients, directions, url)
			recipes.append(recipe)


	return recipes