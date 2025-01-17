import requests
from pprint import pprint
import os
import json
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

params = {
    # check https://developer.edamam.com/edamam-docs-recipe-api#/
    'type': 'public',
    'q': 'fish',
    'app_id': APP_ID,
    'app_key': APP_KEY,
    'ingr': '200',  # no. of ingredients 'MIN-MAX'
    # 'diet': '',
    'health': 'alcohol-free',
    # 'cuisineType': '',
    # 'mealType': '',
    # 'dishType': '',
    # 'calories': '',
    # 'time': '',
    # 'excluded': '',
    # 'calories': '',
    # 'nutrients[CHOCDF]': '',  # carbohydrates
    # 'nutrients[FAT]': '',
    # 'nutrients[SUGAR]': '',
    # 'nutrients[PROCNT]': '',
}

headers = {
    "Accept": "application/json"
}


def search_recipe(calories, health, cuisineType, mealType, carbMax, fatMax, sugarMax, proMin, random=True,
                  q="Vegetables"):
    params = {
        # check https://developer.edamam.com/edamam-docs-recipe-api#/
        'type': 'public',
        'q': q,
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'health': health,
        'cuisineType': cuisineType,
        'mealType': mealType,
        'nutrients[CHOCDF.net]': carbMax,
        'nutrients[FAT]': fatMax,
        'nutrients[SUGAR]': sugarMax,
        'nutrients[PROCNT]': str(proMin) + "+",
        'calories': calories,
        'random': random,
    }
    response = requests.get(url='https://api.edamam.com/api/recipes/v2', params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    # for i in data['hits']:
    #         recipes[i['recipe']['label']] = {
    #             'yield': i['recipe']['yield'],
    #             'calories': i['recipe']['calories'],
    #             'totalNutrients': i['recipe']['totalNutrients'],
    #             'carbohydrates': i['recipe']['totalNutrients']['CHOCDF']
    #         }

    # return data['hits']

    for recipe, det in data['hits']:
            name = recipe
            image = det['image']
            yld = det['yield']
            calories = det['calories']
            fats = det['totalNutrients']['FAT']['quantity']
            carbs = det['totalNutrients']['CHOCDF']['quantity']
            sugar = det['totalNutrients']['SUGAR']['quantity']
            protein = det['totalNutrients']['PROCNT']['quantity']


if __name__ == "__main__":
    # response = requests.get(url='https://api.edamam.com/api/recipes/v2', params=params, headers=headers)
    # response.raise_for_status()
    # data = response.json()
    # print(len(data['hits']))
    # pprint(data['hits'])
    recipes = {}

    for query in ['fried', 'fish', 'rice', 'salad']:
        params['q'] = query
        response = requests.get(url='https://api.edamam.com/api/recipes/v2', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(len(data['hits']))
        pprint(data['hits'])

        for i in data['hits'][:5]:
            recipes[i['recipe']['label']] = {
                'image': i['recipe']['image'],
                'yield': i['recipe']['yield'],
                'calories': i['recipe']['calories'],
                'totalNutrients': i['recipe']['totalNutrients'],
                'digest': i['recipe']['digest'],
            }
        pprint(recipes)

    # with open(r"recipes2.json", 'r') as f:
    #     data = json.load(f)

    # data['recipes'].update(recipes)

    # with open(r"recipes2.json", 'w') as f:
    #     json.dump(data, f, indent=4)
