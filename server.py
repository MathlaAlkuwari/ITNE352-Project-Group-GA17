import socket
import threading
import requests
import json
import struct

HOST = "0.0.0.0"
PORT = 5000

GROUP_ID = "GROUPX"

# THREAD LOCK
file_lock = threading.Lock()

# CACHE
reference_cache = {
    "categories": [],
    "areas": [],
    "ingredients": []
}

# API URLS
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

CATEGORY_URL = f"{BASE_URL}/list.php?c=list"
AREA_URL = f"{BASE_URL}/list.php?a=list"
INGREDIENT_URL = f"{BASE_URL}/list.php?i=list"

SEARCH_URL = f"{BASE_URL}/search.php?s="
FILTER_CATEGORY_URL = f"{BASE_URL}/filter.php?c="
FILTER_AREA_URL = f"{BASE_URL}/filter.php?a="
FILTER_INGREDIENT_URL = f"{BASE_URL}/filter.php?i="
LOOKUP_URL = f"{BASE_URL}/lookup.php?i="
RANDOM_URL = f"{BASE_URL}/random.php"


# HELPER FUNCTIONS
def print_line():
    print("=" * 60)

# TCP MESSAGE FRAMING
def send_json(client_socket, data):

    json_data = json.dumps(data).encode()

    message_length = struct.pack("!I", len(json_data))

    client_socket.sendall(message_length + json_data)


def recv_exact(client_socket, size):

    data = b""

    while len(data) < size:

        packet = client_socket.recv(size - len(data))

        if not packet:
            return None

        data += packet

    return data


def receive_json(client_socket):

    raw_length = recv_exact(client_socket, 4)

    if not raw_length:
        return None

    message_length = struct.unpack("!I", raw_length)[0]

    message_data = recv_exact(client_socket, message_length)

    if not message_data:
        return None

    return json.loads(message_data.decode())


# CACHE LOADING
def load_reference_cache():

    global reference_cache

    print_line()
    print("Loading reference cache...")
    print_line()

    try:

        categories = requests.get(CATEGORY_URL).json()["meals"]

        areas = requests.get(AREA_URL).json()["meals"]

        ingredients = requests.get(INGREDIENT_URL).json()["meals"]

        reference_cache["categories"] = categories
        reference_cache["areas"] = areas
        reference_cache["ingredients"] = ingredients

        print(f"Categories loaded: {len(categories)}")
        print(f"Areas loaded: {len(areas)}")
        print(f"Ingredients loaded: {len(ingredients)}")

        save_data = {
            "categories": categories,
            "areas": areas,
            "ingredients": ingredients[:50]
        }

        filename = f"reference_{GROUP_ID}.json"

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(save_data, file, indent=4)

        print(f"\nReference cache saved to {filename}")

    except Exception as e:

        print(f"Cache loading error: {e}")

# SAVE JSON FILES
def save_recipe_json(client_name, option, data):

    filename = f"{client_name}_{option}_{GROUP_ID}.json"

    with file_lock:

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4)

    print(f"Saved JSON file: {filename}")

# API FUNCTIONS

#name search
def search_by_name(keyword):

    response = requests.get(
        SEARCH_URL + keyword
    ).json()

    meals = response.get("meals")

    return meals[:15] if meals else []

#category search
def filter_by_category(category):

    response = requests.get(
        FILTER_CATEGORY_URL + category
    ).json()

    meals = response.get("meals")

    return meals[:15] if meals else []

#area search
def filter_by_area(area):

    response = requests.get(
        FILTER_AREA_URL + area
    ).json()

    meals = response.get("meals")
  
    return meals[:15] if meals else []

#ingredient search
def filter_by_ingredient(ingredient):

    response = requests.get(
        FILTER_INGREDIENT_URL + ingredient
    ).json()

    meals = response.get("meals")

    return meals[:15] if meals else []

#random search
def get_random_recipe():

    response = requests.get(RANDOM_URL).json()

    meals = response.get("meals")

    return meals[0] if meals else None

#meal deatils
def get_meal_details(meal_id):

    response = requests.get(
        LOOKUP_URL + meal_id
    ).json()

    meals = response.get("meals")

    return meals[0] if meals else None


