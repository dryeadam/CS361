import json

import os
import customtkinter as ctk
from tkinter import filedialog
import zmq

SORT_PORT = 5556
STATS_PORT = 5559


class app(ctk.CTk):
    def __init__(self):
        super().__init__()


        # Window Setup
        self.title("Game Library Viewer")
        self.geometry("1280x720")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.games = {}  # {game_dir: [game names]}
        self.nav_frame = None
        self.games_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "games.json")
        self.load_games()
        if self.games:
            self.display_games()
        else:
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
            self.r = 0
            self.c = 0
            self.game_btn.pack(expand=True, fill="both", padx=5, pady=5)

    def display_settings_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.display_nav()
        self.settings_btn.configure(fg_color="grey25")
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_frame.grid(row=1, column=0, sticky="nsew")

        self.settings_topbar = ctk.CTkFrame(self.content_frame, height=50, corner_radius=0)
        self.settings_topbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.settings_topbar.grid_columnconfigure(1, weight=1)

        self.nav_title = ctk.CTkLabel(self.settings_topbar, text="Settings", font=("Arial", 20, "bold"),fg_color="grey17")
        self.nav_title.grid(row=0, column=1, pady=20)

        self.save_settings_btn = ctk.CTkButton(
            self.settings_topbar, text="Save",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.save_settings
        )
        #self.save_settings_btn.grid(row=0, column=3, padx=5, pady=5)

        self.clear_user_data_btn = ctk.CTkButton(self.content_frame,
                                                 text="Clear User Data",
                                                 corner_radius=10,
                                                 height=50,
                                                 width=180,
                                                 font=("Arial", 16, "bold"),
                                                 fg_color="#A51F1F",
                                                 hover_color="#631919",
                                                 command=self.clear_user_data_warning
                                                 )
        self.clear_user_data_btn.place(relx=0.5, rely=0.5, anchor="center")

        self.clear_data_desc= ctk.CTkLabel(self.content_frame,
                                        text="Removes your saved game folder and settings.\nYou'll need to choose a directory again.",
                                        font=("Arial", 16))
        self.clear_data_desc.place(relx=0.5, rely=0.4, anchor="center")

        self.clear_data_desc2 = ctk.CTkLabel(self.content_frame,
                                            text="This cannot be undone.",
                                            font=("Arial", 16, "bold"))
        self.clear_data_desc2.place(relx=0.5, rely=0.6, anchor="center")

    def display_nav(self):
        if self.nav_frame is not None:
            self.nav_frame.destroy()
        # Navigation Sidebar
        self.nav_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(3, weight=1)
        self.nav_frame.grid_propagate(False)

        self.nav_title = ctk.CTkLabel(self.nav_frame, text="Game Library Viewer", font=("Arial", 20, "bold"))
        self.nav_title.grid(row=0, column=0, padx=20, pady=20)

        # Navigation Buttons
        self.library_btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10, text="Library",
                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                      hover_color=("gray70", "gray30"),
                                      anchor="w", command=self.display_games)
        self.library_btn.grid(row=1, column=0, sticky="ew")

        self.settings_btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10,
                                          text="Settings",
                                          fg_color="transparent", text_color=("gray10", "gray90"),
                                          hover_color=("gray70", "gray30"),
                                          anchor="w", command=self.display_settings_page)
        self.settings_btn.grid(row=2, column=0, sticky="ew")

    def display_library_topbar(self):
        self.library_topbar = ctk.CTkFrame(self.content_frame, height=50, corner_radius=0)
        self.library_topbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.library_topbar.grid_columnconfigure(1, weight=1)

        self.library_desc = ctk.CTkLabel(self.library_topbar,
                                         text="Your games from all chosen folders, in one place! Click a game to open a its folder.",
                                         font=("Arial", 18, "bold"),
                                         padx=10,
                                         pady=10,
                                         )
        self.library_desc.grid(row=0, column=0, sticky="ew")

        self.add_dir_btn = ctk.CTkButton(
            self.library_topbar, text="Add a Game Directory",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.add_game_dir
        )
        self.add_dir_btn.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dir_frame = ctk.CTkFrame(self.library_topbar, fg_color="transparent")
        self.dir_frame.grid(row=2, column=0, sticky="w")
        for i, game_dir in enumerate(self.games):
            self.dir_btn = ctk.CTkButton(
                self.dir_frame, text=game_dir + "   ✕",
                corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
                command=lambda d=game_dir: self.remove_game_dir(d)
            )
            self.dir_btn.grid(row=0, column=i, padx=5, pady=5)


        self.alph_sort_btn = ctk.CTkButton(
            self.library_topbar, text="Sort (A-Z)",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.alph_sort
        )
        # self.alph_sort_btn.grid(row=0, column=2, padx=5, pady=5)

        self.size_sort_btn = ctk.CTkButton(
            self.library_topbar, text="Sort (Size)",
            corner_radius=10, height=40, border_spacing=10, font=("Arial", 16, "bold"),
            command=self.size_sort
        )
        # self.size_sort_btn.grid(row=0, column=3, padx=5, pady=5)

    def ask_service(self, port, request, timeout=2000):
        """Send a JSON-serializable request to the service on `port` and
        return its JSON reply. Returns None if the service doesn't answer."""
        socket = zmq.Context.instance().socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, timeout)
        socket.setsockopt(zmq.SNDTIMEO, timeout)
        socket.connect(f"tcp://localhost:{port}")
        try:
            socket.send_json(request)
            return socket.recv_json()
        except zmq.Again:
            print(f"Service on port {port} not responding.")
            return None
        finally:
            socket.close()

    def ask_service_sorting(self, data, key, timeout=2000):
        # Sorting service expects [key, data]
        return self.ask_service(SORT_PORT, [key, data], timeout)

    def ask_service_stats(self, data, operation, field, timeout=2000):
        # Stats service expects {data: [dicts], operation, field}
        request = {"data": data, "operation": operation, "field": field}
        response = self.ask_service(STATS_PORT, request, timeout)

        if response is None:
            return None
        if "error" in response:
            print(f"Stats service error: {response['error']}")
            return None
        return response["result"]

    def alph_sort(self):
        print(f"Sending request to sorting_microservice on port {SORT_PORT}...")
        for game_dir, game_list in self.games.items():
            result = self.ask_service_sorting(game_list, "ALPH")
            if result:
                self.games[game_dir] = result
        print(f"alph_sort received, updating display...")
        self.display_games()

    def size_sort(self):
        print(f"Sending request to sorting_microservice on port {SORT_PORT}....")
        for game_dir, game_list in self.games.items():
            game_paths = [f"{game_dir}/{game}" for game in game_list]
            result = self.ask_service_sorting(game_paths, "SIZE")
            if result:
                self.games[game_dir] = [os.path.basename(path) for path in result]
        print("size_sort received, updating display...")
        self.display_games()

    def on_game_click(self, game_dir, game_name):
        self.start_game_dir = game_dir + "/" + game_name
        os.startfile(self.start_game_dir)

    def show_game_info(self, game_dir, game_name):

        self.info_title.configure(text=game_name)

        self.info_path.configure(text=f"Path: {game_dir}/{game_name}")
        self.info_frame.tkraise()


    def dir_error(self, error, game_dir):

        self.error_frame = ctk.CTkFrame(self.content_frame,
                                        width=250,
                                        height=70,
                                        fg_color="#A51F1F",
                                        bg_color="transparent",
                                        corner_radius=10
                                     )
        self.error_frame.place(anchor="se", relx=1, rely=1)

        self.error_text = ctk.CTkLabel(self.error_frame,
                                       text="",
                                       justify="left",
                                       font=("Arial", 14, "bold"),
                                       bg_color="transparent",
                                       text_color="white",
                                       padx = 5,
                                       pady = 5,
        )
        self.error_text.place(anchor="center", x=0, y=0)
        self.error_text.pack(padx=20, pady=15)

        if error == "empty":
            print(f"ERROR: {game_dir} is empty.")
            self.error_text.configure(
                text=f"ERROR: {game_dir} is empty.\nPlease try another folder!"
            )

        if error == "already added":
            print(f"ERROR: {game_dir} has already been added to your Library.")
            self.error_text.configure(
                text=f"ERROR: {game_dir} has already\nbeen added to your Library.\nPlease try another folder!")
        self.error_frame.after(4000, self.error_frame.lower)

    def add_game_dir(self):
        game_dir = filedialog.askdirectory(title="Choose a folder to see your games...")
        if os.path.isdir(game_dir):
            if game_dir in self.games:
                self.dir_error("already added", game_dir)
                return
            if not os.listdir(game_dir):
                self.dir_error("empty", game_dir)
                return
            self.games[game_dir] = os.listdir(game_dir)
            self.save_games()
            print(game_dir + " added!")
            print(f"Games Detected in {game_dir}:")
            for game in self.games[game_dir]:
                print(game)
            self.display_games()

    def remove_game_dir(self, game_directory):
        del self.games[game_directory]
        self.save_games()
        self.display_games()

    def save_settings(self):
        pass

    def load_games(self):
        if not os.path.exists(self.games_json):
            return
        try:
            with open(self.games_json, 'r') as file:
                self.games = json.load(file)
        except:
            self.games = {}

    def save_games(self):
        with open(self.games_json, 'w') as file:
            json.dump(self.games, file)

    def start_game(self):
        pass

    def clear_user_data_warning(self):
        self.cud_warning_frame = ctk.CTkFrame(self.content_frame,
                                       width=450,
                                       height=200,
                                       corner_radius=0,
                                       border_width=3,
                                       border_color="white",
                                       )
        self.cud_warning_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.close_cud_warning= ctk.CTkButton(self.cud_warning_frame,
                                        text="✕",
                                        width=30,
                                        height=30,
                                        corner_radius=25,
                                        font=("Arial", 18, "bold"),
                                        text_color="white",
                                        fg_color="#27557A",
                                        bg_color="transparent",
                                        command=self.cud_warning_frame.destroy
                                        )

        self.close_cud_warning.place(anchor="center", relx=.88, rely=.1)

        self.cud_warning_desc = ctk.CTkLabel(self.cud_warning_frame,
                                      text="Are you sure you want to clear all user data?",
                                      width=50,
                                      height=55,
                                      font=("Arial", 14),
                                      text_color="white",
                                      bg_color="transparent",
                                      )
        self.cud_warning_desc.place(anchor="center", relx=.5, rely=.3)

        self.cud_warning_desc2 = ctk.CTkLabel(self.cud_warning_frame,
                                      text="This cannot be undone.",
                                      width=50,
                                      height=55,
                                      font=("Arial", 14, "bold"),
                                      text_color="white",
                                      bg_color="transparent",
                                      )
        self.cud_warning_desc2.place(anchor="center", relx=.5, rely=.5)

        self.clear_user_data_btn = ctk.CTkButton(self.cud_warning_frame,
                                                 text="Clear User Data",
                                                 corner_radius=10,
                                                 height=50,
                                                 width=180,
                                                 font=("Arial", 16, "bold"),
                                                 fg_color="#A51F1F",
                                                 hover_color="#631919",
                                                 command=self.clear_user_data
                                                 )
        self.clear_user_data_btn.place(relx=0.5, rely=0.75, anchor="center")

    def clear_user_data(self):
        if os.path.exists(self.games_json):
            os.remove(self.games_json)
        self.games = {}
        self.nav_frame.destroy()
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.setup_page()

    def setup_page(self):
        self.nav_frame = None

        self.setup_btn = ctk.CTkButton(
            self.content_frame, text="Choose Game Directory",
            corner_radius=10, height=50, width=180, font=("Arial", 16, "bold"),
            command=self.add_game_dir
        )
        self.setup_btn.place(relx=0.5, rely=0.5, anchor="center")

        self.setup_guide = ctk.CTkLabel(self.content_frame,
                                        text="Choose the folder where your games are installed.\nThey'll appear in one library, so you can pick one to play.",
                                        font=("Arial", 16))
        self.setup_guide.place(relx=0.5, rely=0.4, anchor="center")

        self.setup_guide = ctk.CTkLabel(self.content_frame,
                                        text="Note: You can add another folder later.",
                                        font=("Arial", 16))
        self.setup_guide.place(relx=0.5, rely=0.6, anchor="center")

    def display_games(self):

        self.display_nav()
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.library_btn.configure(fg_color="grey25")

        self.display_library_topbar()

        self.games_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.games_frame.grid(row=1, column=0, sticky="nsew")
        for col in range(2):
            self.games_frame.grid_columnconfigure(col, weight=1)

        print("Displaying games...")

        max_cols = 2
        i = 0
        for game_dir, game_list in self.games.items():
            for game_name in game_list:
                game_card = self.GameCard(
                    self.games_frame,
                    game_name=game_name,
                    command=lambda d=game_dir, g=game_name: self.on_game_click(d, g),
                )
                game_card.grid(row=i // max_cols, column=i % max_cols, padx=5, pady=5, sticky="new")
                self.game_info_btn = ctk.CTkButton(game_card.game_btn,
                                                   text="\u2139",
                                                   width=50,
                                                   height=55,
                                                   corner_radius=25,
                                                   font=("Arial", 14, "bold"),
                                                   text_color="white",
                                                   fg_color="#27557A",
                                                   bg_color="transparent",
                                                   command=lambda d=game_dir, g=game_name: self.show_game_info(d, g))
                self.game_info_btn.place(anchor="center", relx=0.9, rely=0.5)
                i += 1

        self.info_frame = ctk.CTkFrame(self.content_frame,
                                       width = 450,
                                       height= 200,
                                       corner_radius= 0,
                                       border_width= 3,
                                       border_color="white",
                                       )
        self.info_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.close_info = ctk.CTkButton(self.info_frame,
                                        text="✕",
                                        width=30,
                                        height=30,
                                        corner_radius=25,
                                        font=("Arial", 18, "bold"),
                                        text_color="white",
                                        fg_color="#27557A",
                                        bg_color="transparent",
                                        command= self.info_frame.lower
                                        )
        self.close_info.place(anchor="center", relx=.88, rely=.2)

        self.info_title = ctk.CTkLabel(self.info_frame,
                                       text="Game Name",
                                       font=("Arial", 18, "bold"),
                                       text_color="white",
                                       bg_color="transparent",
                                       )
        self.info_title.place(anchor="center", relx=.5, rely=.35)

        self.info_path = ctk.CTkLabel(self.info_frame,
                                       text="Game Path: G:/Games/This_Game",
                                       width=50,
                                       height=55,
                                       font=("Arial", 14, "bold"),
                                       text_color="white",
                                       bg_color="transparent",
                                       )
        self.info_path.place(anchor="center", relx=.5, rely=.7)
        self.info_frame.lower()

if __name__ == "__main__":
    self = app()
    self.mainloop()