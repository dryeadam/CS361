import os, json, urllib.request
import customtkinter as ctk
from tkinter import filedialog



class app(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.game_dir = ""
        self.games = []

        # Window Setup
        self.title("Game Library Viewer")
        self.geometry("700x450")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Navigation Sidebar
        self.nav_frame = ctk.CTkFrame(self, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(4, weight=1)

        self.nav_title = ctk.CTkLabel(self.nav_frame, text="My App", font=ctk.CTkFont(size=20, weight="bold"))
        self.nav_title.grid(row=0, column=0, padx=20, pady=20)

        # Navigation Buttons
        self.home_btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                      hover_color=("gray70", "gray30"),
                                      anchor="w", command=self.test)
        self.home_btn.grid(row=1, column=0, sticky="ew")

        self.settings_btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10,
                                          text="Settings",
                                          fg_color="transparent", text_color=("gray10", "gray90"),
                                          hover_color=("gray70", "gray30"),
                                          anchor="w")
        self.settings_btn.grid(row=2, column=0, sticky="ew")

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, padx=20, pady=20)
        self.setup_page()

    class GameCard(ctk.CTkFrame):
        def __init__(self, master, game_name="", command=None):
            super().__init__(master, width=150, height=100)
            self.grid_propagate(False)  # Lock card dimensions
            self.Title = game_name

            self.game_btn = ctk.CTkButton(
                self,
                text=self.Title,
                font=("Arial", 12),
                command=command
            )
            self.game_btn.pack(expand=True, fill="both", padx=5, pady=5)

    def test(self):
        print("test")

    def setup_page(self):
        self.choose_path_btn = ctk.CTkButton(
            self.content_frame,
            text="Choose Game Directory",
            corner_radius=0,
            height=40,
            border_spacing=10,
            command=self.choose_game_dir
        )
        self.choose_path_btn.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")

    def display_games(self):
        # Clear old cards if choosing a new directory
        for widget in self.content_frame.winfo_children():
            if widget != self.choose_path_btn:
                widget.destroy()

        max_cols = 2  # Set how many cards per row

        # Make columns stretch evenly
        for col in range(max_cols):
            self.content_frame.grid_columnconfigure(col, weight=1)

        for i, game_name in enumerate(self.games):
            row = (i // max_cols) + 1  # Offset by 1 for the button
            col = i % max_cols

            game_card = self.GameCard(
                self.content_frame,
                game_name=game_name,
                command=lambda game=game_name: self.on_game_click(game)
            )
            game_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # Sort Alphabetically Button
        self.alph_sort_btn = ctk.CTkButton(
            self.content_frame,
            text="Sort (A-Z)",
            corner_radius=0,
            height=40,
            border_spacing=10,
            command=lambda: self.send_sort_request()
        )
        self.alph_sort_btn.grid(row=0, column=1, pady=(0, 10), padx=(5, 0), sticky="e")

        # Sort by Size Button
        self.size_sort_btn = ctk.CTkButton(
            self.content_frame,
            text="Sort (Size)",
            corner_radius=0,
            height=40,
            border_spacing=10,
            command=lambda: self.send_sort_request()
        )
        self.size_sort_btn.grid(row=0, column=2, pady=(0, 10), padx=(5, 0), sticky="e")

    def send_sort_request(self):
        pass

    def on_game_click(self, game_name):
        pass

    def choose_game_dir(self):
        self.game_dir = filedialog.askdirectory()
        print(self.game_dir + " selected!")
        self.games = os.listdir(self.game_dir)
        print("Games Detected: " + ', '.join(map(str, self.games)))
        self.display_games()



if __name__ == "__main__":
    self = app()
    self.mainloop()

