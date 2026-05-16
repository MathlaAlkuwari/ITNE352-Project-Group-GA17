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

# valid inputs to choose from
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

# GUI in client
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

    # connection
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

        
        # buttons for categories
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

        # displaying lists
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

        # outputs showing 
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

    # helpers to support the programs
    def clear_output(self):

        self.output_text.delete(
            "1.0",
            tk.END
        )

    def clear_tree(self):

        for item in self.tree.get_children():

            self.tree.delete(item)

    # displying lists
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

    # displayong full recipe
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
                    f"- {ingredient} : {measure}\n"-9 
                )
