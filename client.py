# client.py

import socket
import json
import struct

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# VALID INPUTS

VALID_CATEGORIES = [
    "Beef",
    "Chicken",
    "Seafood",
    "Vegetarian",
    "Dessert",
    "Pasta",
    "Breakfast"
]

VALID_AREAS = [
    "Italian",
    "Indian",
    "Mexican",
    "Japanese",
    "Moroccan",
    "British",
    "American",
    "Thai"
]

# TCP FRAMING

def send_json(sock, data):

    json_data = json.dumps(data).encode()

    message_length = struct.pack(
        "!I",
        len(json_data)
    )

    sock.sendall(message_length + json_data)


def recv_exact(sock, size):

    data = b""

    while len(data) < size:

        packet = sock.recv(size - len(data))

        if not packet:
            return None

        data += packet

    return data


def receive_json(sock):

    raw_length = recv_exact(sock, 4)

    if not raw_length:
        return None

    message_length = struct.unpack(
        "!I",
        raw_length
    )[0]

    message_data = recv_exact(
        sock,
        message_length
    )

    if not message_data:
        return None

    return json.loads(message_data.decode())

# DISPLAY FUNCTIONS

def print_line():

    print("=" * 60)


def wait():

    input("\nPress Enter to continue...")


def print_recipe_list(results):

    print_line()
    print("RECIPES")
    print_line()

    for index, meal in enumerate(results, start=1):

        print(f"\n[{index}]")

        print(f"Meal ID : {meal.get('idMeal')}")
        print(f"Name    : {meal.get('strMeal')}")
        print(f"Thumbnail URL : {meal.get('strMealThumb')}")


def print_full_recipe(recipe):

    print_line()
    print("FULL RECIPE DETAILS")
    print_line()

    print(f"Name      : {recipe.get('strMeal')}")
    print(f"Category  : {recipe.get('strCategory')}")
    print(f"Area      : {recipe.get('strArea')}")
    print(f"Tags      : {recipe.get('strTags')}")
    print(f"YouTube   : {recipe.get('strYoutube')}")
    print(f"Source    : {recipe.get('strSource')}")

    print("\nInstructions:")
    print(recipe.get("strInstructions"))

    print("\nIngredients:")

    for i in range(1, 21):

        ingredient = recipe.get(f"strIngredient{i}")
        measure = recipe.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():

            print(f"- {ingredient} : {measure}")


def print_categories(results):

    print_line()
    print("CATEGORIES")
    print_line()

    for index, item in enumerate(results, start=1):

        print(f"{index}. {item.get('strCategory')}")

        description = item.get(
            "strCategoryDescription"
        )

        if description:

            print(
                f"   Description: "
                f"{description[:100]}..."
            )


def print_areas(results):

    print_line()
    print("AREAS")
    print_line()

    for index, item in enumerate(results, start=1):

        print(f"{index}. {item.get('strArea')}")


def print_ingredients(results):

    print_line()
    print("INGREDIENTS")
    print_line()

    for index, item in enumerate(results, start=1):

        print(f"{index}. {item.get('strIngredient')}")

# Full details request

def request_full_recipe(sock, results):

    try:

        selected = input(
            "\nEnter recipe number "
            "for full details (0 to cancel): "
        )

        if selected == "0":
            return

        selected_index = int(selected) - 1

        if (
            selected_index < 0
            or
            selected_index >= len(results)
        ):

            print("Invalid selection.")
            wait()
            return

        meal_id = results[selected_index]["idMeal"]

        request = {
            "type": "meal_details",
            "value": meal_id
        }

        send_json(sock, request)

        response = receive_json(sock)

        if response is None:

            print("Server disconnected.")
            return

        if response["status"] == "ok":

            print_full_recipe(response["meal"])

        else:

            print(response["message"])

    except ValueError:

        print("Please enter a valid number.")

    except Exception as e:

        print("Error:", e)

    wait()

# Recipes menu

def recipes_menu(sock):

    while True:

        print_line()
        print("RECIPES MENU")
        print_line()

        print("1. Search by name")
        print("2. Filter by category")
        print("3. Filter by area")
        print("4. Filter by ingredient")
        print("5. Random recipe")
        print("6. Back to main menu")

        choice = input("\nChoose option: ")

        # Search name

        if choice == "1":

            keyword = input(
                "\nEnter recipe keyword: "
            ).strip()

            if not keyword:

                print("Keyword cannot be empty.")
                wait()
                continue

            request = {
                "type": "search_name",
                "value": keyword
            }

            send_json(sock, request)

            response = receive_json(sock)

            if response["status"] == "ok":

                results = response["results"]

                if not results:

                    print("No recipes found.")
                    wait()
                    continue

                print_recipe_list(results)

                request_full_recipe(sock, results)

            else:

                print(response["message"])
                wait()

        # Filter category

        elif choice == "2":

            print("\nAllowed categories:")

            for category in VALID_CATEGORIES:

                print("-", category)

            category = input(
                "\nEnter category: "
            ).strip()

            if category not in VALID_CATEGORIES:

                print("Invalid category.")
                wait()
                continue

            request = {
                "type": "filter_category",
                "value": category
            }

            send_json(sock, request)

            response = receive_json(sock)

            if response["status"] == "ok":

                results = response["results"]

                if not results:

                    print("No recipes found.")
                    wait()
                    continue

                print_recipe_list(results)

                request_full_recipe(sock, results)

            else:

                print(response["message"])
                wait()
                
        # Filter area

        elif choice == "3":

            print("\nAllowed areas:")

            for area in VALID_AREAS:

                print("-", area)

            area = input(
                "\nEnter area: "
            ).strip()

            if area not in VALID_AREAS:

                print("Invalid area.")
                wait()
                continue

            request = {
                "type": "filter_area",
                "value": area
            }

            send_json(sock, request)

            response = receive_json(sock)

            if response["status"] == "ok":

                results = response["results"]

                if not results:

                    print("No recipes found.")
                    wait()
                    continue

                print_recipe_list(results)

                request_full_recipe(sock, results)

            else:

                print(response["message"])
                wait()

        # Filter ingredient

        elif choice == "4":

            ingredient = input(
                "\nEnter ingredient: "
            ).strip()

            if not ingredient:

                print(
                    "Ingredient cannot be empty."
                )

                wait()
                continue

            ingredient = ingredient.replace(
                " ",
                "_"
            )

            request = {
                "type": "filter_ingredient",
                "value": ingredient
            }

            send_json(sock, request)

            response = receive_json(sock)

            if response["status"] == "ok":

                results = response["results"]

                if not results:

                    print("No recipes found.")
                    wait()
                    continue

                print_recipe_list(results)

                request_full_recipe(sock, results)

            else:

                print(response["message"])
                wait()

