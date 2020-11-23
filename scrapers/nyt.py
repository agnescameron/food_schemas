from pyquery import PyQuery as pq
from classes.recipe import Recipe
import re
import os

def scrape():
	#try for 1000 files
	recipes = []
	directory = os.listdir( 'nyt_recipes/' )

	for index, file in enumerate(directory):
		# print(index, file)
		if index < 200:
			d = pq(filename='nyt_recipes/'+file)
			ingredients = []
			directions = []
			tags = []

			url = d('meta[property="og:url"]').attr("content")

			cuisineTag = d('meta[itemProp="recipeCuisine"]').attr("value")
			if cuisineTag is not None:
				tags.append(cuisineTag)

			for el in d('div.tags-nutrition-container a'):
				print(d(el).text())
				tags.append(d(el).text())

			# print(d)
			title = d(".recipe-title").text()
			author = d("span.byline-name").text()
			print(title, author)

			for el in d("span.ingredient-name"):
				ingredients.append(d(el).text())

			for el in d("ol.recipe-steps > li"):
				directions.append(d(el).text())

			recipe = Recipe(title, ingredients, directions, url, author, tags)
			recipes.append(recipe)


	return recipes