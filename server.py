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
# CLIENT HANDLER

def handle_client(client_socket, client_address):

    client_name = "Unknown"

    print_line()
    print(f"Connection from {client_address}")
    print_line()

    try:

        while True:

            request = receive_json(client_socket)

            # CLIENT DISCONNECTED
            if request is None:

                print(f"\n[DISCONNECTED] {client_name}")
                break

            request_type = request.get("type")
            request_value = request.get("value")

            # USERNAME
            if request_type == "username":

                client_name = request_value

                print(f"[CONNECTED] {client_name}")

                send_json(client_socket, {
                    "status": "ok",
                    "message": f"Welcome {client_name}"
                })
            # REFERENCE LISTS
            elif request_type == "list_categories":

                print(f"\n[{client_name}] Categories")
                print("Served from CACHE")

                send_json(client_socket, {
                    "status": "ok",
                    "results": reference_cache["categories"]
                })

            elif request_type == "list_areas":

                print(f"\n[{client_name}] Areas")
                print("Served from CACHE")

                send_json(client_socket, {
                    "status": "ok",
                    "results": reference_cache["areas"]
                })

            elif request_type == "list_ingredients":

                print(f"\n[{client_name}] Ingredients")
                print("Served from CACHE")

                send_json(client_socket, {
                    "status": "ok",
                    "results": reference_cache["ingredients"][:50]
                })
                # =========================
            # SEARCH/FILTER
            # =========================

            elif request_type == "search_name":

                print(f"\n[{client_name}] Search: {request_value}")

                meals = search_by_name(request_value)

                save_recipe_json(
                    client_name,
                    "search_name",
                    meals
                )

                send_json(client_socket, {
                    "status": "ok",
                    "results": meals
                })

            elif request_type == "filter_category":

                print(f"\n[{client_name}] Category: {request_value}")

                meals = filter_by_category(request_value)

                save_recipe_json(
                    client_name,
                    "filter_category",
                    meals
                )

                send_json(client_socket, {
                    "status": "ok",
                    "results": meals
                })

            elif request_type == "filter_area":

                print(f"\n[{client_name}] Area: {request_value}")

                meals = filter_by_area(request_value)

                save_recipe_json(
                    client_name,
                    "filter_area",
                    meals
                )

                send_json(client_socket, {
                    "status": "ok",
                    "results": meals
                })

            elif request_type == "filter_ingredient":

                print(f"\n[{client_name}] Ingredient: {request_value}")

                meals = filter_by_ingredient(request_value)

                save_recipe_json(
                    client_name,
                    "filter_ingredient",
                    meals
                )

                send_json(client_socket, {
                    "status": "ok",
                    "results": meals
                })

            # =========================
            # RANDOM RECIPE
            # =========================

            elif request_type == "random_recipe":

                print(f"\n[{client_name}] Random recipe")

                meal = get_random_recipe()

                save_recipe_json(
                    client_name,
                    "random_recipe",
                    meal
                )

                send_json(client_socket, {
                    "status": "ok",
                    "meal": meal
                })

            # =========================
            # FULL DETAILS
            # =========================

            elif request_type == "meal_details":

                print(f"\n[{client_name}] Meal details: {request_value}")

                meal = get_meal_details(request_value)

                send_json(client_socket, {
                    "status": "ok",
                    "meal": meal
                })

            # =========================
            # QUIT
            # =========================

            elif request_type == "quit":

                print(f"\n[QUIT] {client_name}")
                break

            # =========================
            # INVALID REQUEST
            # =========================

            else:

                send_json(client_socket, {
                    "status": "error",
                    "message": "Invalid request"
                })

    except Exception as e:

        print(f"\nError with {client_name}: {e}")

    finally:

        client_socket.close()

        print(f"Closed connection for {client_name}")





