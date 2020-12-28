from bs4 import BeautifulSoup
from classes.recipe import Recipe
import requests
import re
from recipe_scrapers import scrape_me
from selenium import webdriver
import numpy as np
from random import randint
from time import sleep


pages = np.arange(1, 3, 1)
recipes = []
def scrape():
    
    recipes = []

    for page in pages:
        page="https://www.spendwithpennies.com/borscht-recipe-beet-soup/"
        driver = webdriver.Chrome('/Users/MyUsername/Downloads/chromedriver')
        driver.get(page)  
        sleep(randint(1,2))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.find('h1')
        
        ingredient_container = soup.find('div', {'class': re.compile(r'(?<!direction.)ingredient(?!.*(direction|instruction|steps))')})
        ingredients = []
        try:
            ingredients = ingredient_container.find_all('li')
        except:
            print("ingredient not found")
        
        for index, ingredient in enumerate(ingredients):
            ingredient_name = ingredient.find('span', {'class': re.compile(r'name|Name|ingredient(?!.*(unit|amount))')})
            if ingredient_name:
                ingredient = ingredient_name
            ingredient = ingredient.text.strip()    
            ingredients[index] = re.sub(r'\s+', ' ', ingredient)
            
        direction_container = soup.find('div', {'class': re.compile(r'(?<!ingredient.)direction|instruction|steps(?!.*(ingredient|description))')})
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
            
        recipe = Recipe(title, ingredients, directions, page)
        recipes.append(recipe)
        print('this recipe has', len(ingredients), 'ingredients, and', len(directions), 'steps')
        
    return recipes     
