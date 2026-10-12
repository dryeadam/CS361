import os
import time

import customtkinter as ctk
from tkinter import filedialog
import zmq



class app(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.game_dir = ""
        self.games = []

        # Window Setup
        self.title("Game Library Viewer")
        self.geometry("1280x720")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Navigation Sidebar
        self.nav_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(3, weight=1)  # Pushes anything below down
        self.nav_frame.grid_propagate(False)  # Lock sidebar width

        self.nav_title = ctk.CTkLabel(self.nav_frame, text="Game Library Viewer", font=("Arial", 20, "bold"))
        self.nav_title.grid(row=0, column=0, padx=20, pady=20)

        # Navigation Buttons
        self.home_btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                      hover_color=("gray70", "gray30"),
                                      anchor="w", command=self.display_games)
        self.home_btn.grid(row=1, column=0, sticky="ew")



        self.settings_btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10,
                                          text="Settings",
                                          fg_color="transparent", text_color=("gray10", "gray90"),
                                          hover_color=("gray70", "gray30"),
                                          anchor="w", command=self.display_settings_page)
        self.settings_btn.grid(row=2, column=0, sticky="ew")

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.setup_page()

    class GameCard(ctk.CTkFrame):
        def __init__(self, master, game_name="", command=None):
            super().__init__(master, height=75)
            self.Title = game_name
            self.pack_propagate(False)
            self.game_btn = ctk.CTkButton(
                self,
                text=self.Title,
                font=("Arial", 16, "bold"),
                command=command,
                corner_radius=10
            )
            self.game_btn.pack(expand=True, fill="both", padx=5, pady=5)

    def display_settings_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.settings_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.settings_frame.grid(row=1, column=0, sticky="nsew")

        self.settings_topbar = ctk.CTkFrame(self.content_frame, height=50, corner_radius=0)
        self.settings_topbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.settings_topbar.grid_columnconfigure(1, weight=1)

        self.nav_title = ctk.CTkLabel(self.content_frame, text="Settings", font=("Arial", 20, "bold"),fg_color="grey17")
        self.nav_title.grid(row=2, column=0, padx=20, pady=20)

        self.save_settings_btn = ctk.CTkButton(
            self.settings_topbar, text="Save",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.save_settings
        )
        self.save_settings_btn.grid(row=0, column=3, padx=5, pady=5)

    def ask_service(self, port, data):
        socket = zmq.Context().socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 2000)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(f"tcp://localhost:{port}")
        try:
            socket.send_pyobj(data)
            return socket.recv_pyobj()
        except zmq.Again:
            print(f"Service on port {port} not responding")
            return None
        finally:
            socket.close()

    def alph_sort(self):
        result = self.ask_service(5556, self.games)
        print(f"Sending request to alph_sort on port 5556.")
        if result:
            self.games = result
            print(f"alph_sort received, updating display...")
            self.display_games()

    def size_sort(self):
        result = self.ask_service(5557, self.games)
        print(f"Sending request to alph_sort on port 5557.")
        if result:
            self.games = result
            print(f"size_sort received, updating display...")
            self.display_games()
    def on_game_click(self, game_name):
        pass

    def save_settings(self):
        pass

    def choose_game_dir(self):
        self.game_dir = filedialog.askdirectory()
        print(self.game_dir + " selected!")
        self.games = os.listdir(self.game_dir)
        print("Games Detected: " + ', '.join(map(str, self.games)))
        self.display_games()


    def display_home_topbar(self):
        self.home_topbar = ctk.CTkFrame(self.content_frame, height=50, corner_radius=0)
        self.home_topbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.home_topbar.grid_columnconfigure(1, weight=1)

        self.choose_path_btn = ctk.CTkButton(
            self.home_topbar, text="Choose Game Directory",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.choose_game_dir
        )
        self.choose_path_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.alph_sort_btn = ctk.CTkButton(
            self.home_topbar, text="Sort (A-Z)",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.alph_sort
        )
        self.alph_sort_btn.grid(row=0, column=2, padx=5, pady=5)

        self.size_sort_btn = ctk.CTkButton(
            self.home_topbar, text="Sort (Size)",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.size_sort
        )
        self.size_sort_btn.grid(row=0, column=3, padx=5, pady=5)

    def setup_page(self):
        # Games area
        self.games_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.games_frame.grid(row=1, column=0, sticky="nsew")
        for col in range(2):
            self.games_frame.grid_columnconfigure(col, weight=1)

        self.setup_btn = ctk.CTkButton(
            self.content_frame, text="Choose Game Directory",
            corner_radius=10, height=50, width=180, font=("Arial", 16, "bold"),
            command=self.choose_game_dir
        )
        self.setup_btn.place(relx=0.5, rely=0.5, anchor="center")

    def display_games(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.display_home_topbar()

        self.games_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.games_frame.grid(row=1, column=0, sticky="nsew")
        for col in range(2):
            self.games_frame.grid_columnconfigure(col, weight=1)

        print("Displaying games...")

        max_cols = 2
        for i, game_name in enumerate(self.games):
            game_card = self.GameCard(
                self.games_frame,
                game_name=game_name,
                command=lambda game=game_name: self.on_game_click(game)
            )
            game_card.grid(row=i // max_cols, column=i % max_cols, padx=5, pady=5, sticky="new")


if __name__ == "__main__":
    self = app()
    self.mainloop()

