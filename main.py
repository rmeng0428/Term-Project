from flask import Flask, render_template, request
import openai
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Configure API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
mapbox_api_key = os.getenv("MAPBOX_API_KEY")

app = Flask(__name__)


def translate_and_describe_food(chinese_food_name):
    """Uses OpenAI API to translate and provide detailed insights into Chinese cuisine."""
    try:
        # OpenAI API prompt to get detailed information
        prompt = (
            f"You are a culinary expert specializing in Chinese cuisine. Please provide a detailed description of the dish '{chinese_food_name}'. "
            f"Include the following details:\n"
            f"1. An English translation of the dish name.\n"
            f"2. Key ingredients.\n"
            f"3. Flavor profile (e.g., spicy, sweet, umami, etc.).\n"
            f"4. Regional origin within China (if applicable).\n"
            f"5. Cooking method (e.g., stir-fried, steamed, etc.).\n"
            f"6. A recommendation on whether the dish is suitable for foreigners trying Chinese food for the first time, and why."
        )

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {e}"


def get_nearby_restaurants(zip_code):
    """Uses Mapbox API to find nearby Chinese restaurants."""
    try:
        # Geocode the zip code to get latitude and longitude
        geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zip_code}.json?access_token={mapbox_api_key}"
        geo_response = requests.get(geocode_url).json()
        coordinates = geo_response['features'][0]['geometry']['coordinates']

        # Search for nearby Chinese restaurants
        search_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/chinese restaurant.json?proximity={coordinates[0]},{coordinates[1]}&access_token={mapbox_api_key}"
        search_response = requests.get(search_url).json()
        
        restaurants = [place['place_name'] for place in search_response['features']]
        return restaurants if restaurants else ["No nearby Chinese restaurants found."]
    except Exception as e:
        return [f"Error: {e}"]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        chinese_food_name = request.form["food_name"]
        zip_code = request.form.get("zip_code")

        # Get translation and description
        description = translate_and_describe_food(chinese_food_name)

        # Get nearby restaurants if zip code is provided
        restaurants = get_nearby_restaurants(zip_code) if zip_code else None

        return render_template("result.html", food_name=chinese_food_name, description=description, restaurants=restaurants)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
