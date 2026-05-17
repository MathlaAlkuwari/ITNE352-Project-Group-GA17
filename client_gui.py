import socket
import json
import struct
import tkinter as tk

from tkinter import (
    ttk,
    messagebox,
    simpledialog
)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# valid inputs 
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

# GUI client class
class MealDBClientGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "MealDB Recipe Client"
        )

        self.root.geometry("950x700")

        self.root.minsize(950, 700)

        self.socket = None

        self.results = []

        self.connect_to_server()

        self.username = simpledialog.askstring(
            "Username",
            "Enter username:"
        )

        if not self.username:

            self.username = "Guest"

        self.send_json({
            "type": "username",
            "value": self.username
        })

        response = self.receive_json()

        if response:

            messagebox.showinfo(
                "Server",
                response.get("message")
            )

        self.create_widgets()

    # TCP framing
    def send_json(self, data):

        json_data = json.dumps(data).encode()

        message_length = struct.pack(
            "!I",
            len(json_data)
        )

        self.socket.sendall(
            message_length + json_data
        )

    def recv_exact(self, size):

        data = b""

        while len(data) < size:

            packet = self.socket.recv(
                size - len(data)
            )

            if not packet:
                return None

            data += packet

        return data

    def receive_json(self):

        raw_length = self.recv_exact(4)

        if not raw_length:
            return None

        message_length = struct.unpack(
            "!I",
            raw_length
        )[0]

        message_data = self.recv_exact(
            message_length
        )

        if not message_data:
            return None

        return json.loads(
            message_data.decode()
        )

    # connection to the server to work
    def connect_to_server(self):

        try:

            self.socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.socket.connect(
                (SERVER_HOST, SERVER_PORT)
            )

        except Exception as e:

            messagebox.showerror(
                "Connection Error",
                str(e)
            )

            self.root.destroy()

    # GUI
    def create_widgets(self):

        title = tk.Label(
            self.root,
            text="MealDB Recipe Client",
            font=("Arial", 20, "bold")
        )

        title.pack(pady=10)

        # button framing
        button_frame = tk.Frame(self.root)

        button_frame.pack(pady=10)

        buttons = [

            ("Search Name", self.search_name),

            (
                "Filter Category",
                self.filter_category
            ),

            ("Filter Area", self.filter_area),

            (
                "Filter Ingredient",
                self.filter_ingredient
            ),

            (
                "Random Recipe",
                self.random_recipe
            ),

            (
                "List Categories",
                self.list_categories
            ),

            ("List Areas", self.list_areas),

            (
                "List Ingredients",
                self.list_ingredients
            ),

            ("Quit", self.quit_program)
        ]

        row = 0
        col = 0

        for text, command in buttons:

            tk.Button(
                button_frame,
                text=text,
                width=20,
                command=command
            ).grid(
                row=row,
                column=col,
                padx=5,
                pady=5
            )

            col += 1

            if col > 2:

                col = 0
                row += 1

        # showing treeview
        columns = (
            "Meal ID",
            "Recipe Name"
        )

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=12
        )

        self.tree.heading(
            "Meal ID",
            text="Meal ID"
        )

        self.tree.heading(
            "Recipe Name",
            text="Recipe Name"
        )

        self.tree.column(
            "Meal ID",
            width=150
        )

        self.tree.column(
            "Recipe Name",
            width=600
        )

        self.tree.pack(
            fill="both",
            expand=False,
            padx=20,
            pady=10
        )

        self.tree.bind(
            "<Double-1>",
            self.show_selected_recipe
        )

        # 
        # show ouput and can scrol through it 
        output_frame = tk.Frame(self.root)

        output_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        scrollbar = tk.Scrollbar(
            output_frame
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.output_text = tk.Text(
            output_frame,
            wrap="word",
            yscrollcommand=scrollbar.set
        )

        self.output_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.output_text.yview
        )

    # helpers 
    def clear_output(self):

        self.output_text.delete(
            "1.0",
            tk.END
        )

    def clear_tree(self):

        for item in self.tree.get_children():

            self.tree.delete(item)

    # display lists 
    def display_recipe_list(self, results):

        self.clear_tree()

        self.clear_output()

        self.results = results

        for meal in results:

            self.tree.insert(
                "",
                tk.END,
                values=(
                    meal.get("idMeal"),
                    meal.get("strMeal")
                )
            )

    def display_reference_list(
        self,
        results,
        key
    ):

        self.clear_tree()

        self.clear_output()

        for index, item in enumerate(
            results,
            start=1
        ):

            self.output_text.insert(
                tk.END,
                f"{index}. {item.get(key)}\n"
            )

    # display all recipes in the program
    def display_full_recipe(self, meal):

        self.clear_output()

        self.output_text.insert(
            tk.END,
            f"Name: {meal.get('strMeal')}\n"
        )

        self.output_text.insert(
            tk.END,
            f"Category: "
            f"{meal.get('strCategory')}\n"
        )

        self.output_text.insert(
            tk.END,
            f"Area: "
            f"{meal.get('strArea')}\n"
        )

        self.output_text.insert(
            tk.END,
            f"Tags: "
            f"{meal.get('strTags')}\n"
        )

        self.output_text.insert(
            tk.END,
            f"YouTube: "
            f"{meal.get('strYoutube')}\n"
        )

        self.output_text.insert(
            tk.END,
            f"Source: "
            f"{meal.get('strSource')}\n\n"
        )

        self.output_text.insert(
            tk.END,
            "Instructions:\n"
        )

        self.output_text.insert(
            tk.END,
            f"{meal.get('strInstructions')}\n\n"
        )

        self.output_text.insert(
            tk.END,
            "Ingredients:\n"
        )

        for i in range(1, 21):

            ingredient = meal.get(
                f"strIngredient{i}"
            )

            measure = meal.get(
                f"strMeasure{i}"
            )

            if ingredient and ingredient.strip():

                self.output_text.insert(
                    tk.END,
                    f"- {ingredient} : {measure}\n"
                )

    # search for specific recipe name 
    def search_name(self):

        keyword = simpledialog.askstring(
            "Search",
            "Enter recipe name:"
        )

        if not keyword:
            return

        self.send_json({
            "type": "search_name",
            "value": keyword
        })

        response = self.receive_json()

        if response["status"] == "ok":

            results = response["results"]

            if not results:

                messagebox.showinfo(
                    "No Results",
                    "No recipes found."
                )

                return

            self.display_recipe_list(results)

    # filter category of the recipe 
    def filter_category(self):

        category = simpledialog.askstring(
            "Category",
            "Choose category:\n\n"
            + "\n".join(VALID_CATEGORIES)
        )

        if not category:
            return

        if category not in VALID_CATEGORIES:

            messagebox.showerror(
                "Invalid",
                "Invalid category."
            )

            return

        self.send_json({
            "type": "filter_category",
            "value": category
        })

        response = self.receive_json()

        if response["status"] == "ok":

            results = response["results"]

            if not results:

                messagebox.showinfo(
                    "No Results",
                    "No recipes found."
                )

                return

            self.display_recipe_list(results)

    # filter the area we are choosing from 
    def filter_area(self):

        area = simpledialog.askstring(
            "Area",
            "Choose area:\n\n"
            + "\n".join(VALID_AREAS)
        )

        if not area:
            return

        if area not in VALID_AREAS:

            messagebox.showerror(
                "Invalid",
                "Invalid area."
            )

            return

        self.send_json({
            "type": "filter_area",
            "value": area
        })

        response = self.receive_json()

        if response["status"] == "ok":

            results = response["results"]

            if not results:

                messagebox.showinfo(
                    "No Results",
                    "No recipes found."
                )

                return

            self.display_recipe_list(results)

    # ingrediant choosing if we want something specific in the food
    def filter_ingredient(self):

        ingredient = simpledialog.askstring(
            "Ingredient",
            "Enter ingredient:"
        )

        if not ingredient:
            return

        ingredient = ingredient.replace(
            " ",
            "_"
        )

        self.send_json({
            "type": "filter_ingredient",
            "value": ingredient
        })

        response = self.receive_json()

        if response["status"] == "ok":

            results = response["results"]

            if not results:

                messagebox.showinfo(
                    "No Results",
                    "No recipes found."
                )

                return

            self.display_recipe_list(results)

    # to have a random recipe when nothing in mind 
    def random_recipe(self):

        self.send_json({
            "type": "random_recipe"
        })

        response = self.receive_json()

        if response["status"] == "ok":

            self.display_full_recipe(
                response["meal"]
            )

    # reference list but not to choose from 
    def list_categories(self):

        self.send_json({
            "type": "list_categories"
        })

        response = self.receive_json()

        if response["status"] == "ok":

            self.display_reference_list(
                response["results"],
                "strCategory"
            )

    def list_areas(self):

        self.send_json({
            "type": "list_areas"
        })

        response = self.receive_json()

        if response["status"] == "ok":

            self.display_reference_list(
                response["results"],
                "strArea"
            )

    def list_ingredients(self):

        self.send_json({
            "type": "list_ingredients"
        })

        response = self.receive_json()

        if response["status"] == "ok":

            self.display_reference_list(
                response["results"],
                "strIngredient"
            )

    # double click to choose the wanted recipe
    def show_selected_recipe(self, event):

        selected = self.tree.focus()

        if not selected:
            return

        values = self.tree.item(
            selected,
            "values"
        )

        meal_id = values[0]

        self.send_json({
            "type": "meal_details",
            "value": meal_id
        })

        response = self.receive_json()

        if response["status"] == "ok":

            self.display_full_recipe(
                response["meal"]
            )

    # for quitting
    def quit_program(self):

        try:

            self.send_json({
                "type": "quit"
            })

            self.socket.close()

        except:
            pass

        self.root.destroy()

# main
def main():

    root = tk.Tk()

    app = MealDBClientGUI(root)

    root.mainloop()

# starting the program 
if __name__ == "__main__":

    main()
