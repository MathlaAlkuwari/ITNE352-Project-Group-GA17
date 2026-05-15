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
