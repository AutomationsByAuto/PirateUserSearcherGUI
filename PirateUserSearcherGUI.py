"""
PirateBay User Searcher GUI
===========================

This is an object-oriented GUI application, transformed from a command-line script,
designed to search The Pirate Bay for torrents by usernames and terms. It allows users
to save search data to CSV, sort results by size, date, or seeders, and display results
with clickable links; including Pirate Bay URL, magnet link and relevant URLS from the
torrents' description (e.g., screenshots). Built with CustomTkinter for a modern
interface, it scales dynamically to different monitor sizes for optimal display. It aims
to provide an intuitive and visually appealing experience.
"""

# Standard library imports
import asyncio
import os
import platform
import random
import time
from datetime import datetime
from itertools import chain
import sys

# Third-party imports
import aiohttp
import customtkinter as ctk
import pandas as pd
import requests
from PIL import Image
import CTkMessagebox
import Pmw

# Local imports
import webbrowser

# Resource path function for PyInstaller
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Constants
MAX_RESULTS_WITH_LINKS = 100  # Maximum number of results with detailed links
REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds
TITLE = "Pirate User Searcher By Auto"
WIDTH = 700  # Base window width
HEIGHT = 600  # Base window height
IMAGE_PATH = resource_path("Resources/storm.jpg")  # Background image file
ICON_PATH = resource_path("Resources/pirate.ico")  # Application icon file

# Global Variables
PIRATE_URL = ""
USERNAMES = []
SEARCH_TERMS = []
LOADED_USERS = ""
LOADED_TERMS = ""
CHOSEN_CSV = ""
BUTTON_EXIST = False

class PirateSearcherApp:
    """Main application class for the PirateBay User Searcher GUI.

    This class initializes the GUI, manages frames, and handles user interactions
    for searching torrents, saving data, and displaying results.
    """

    def __init__(self, root):
        """Initialize the main window and UI components.

        Args:
            root: The CustomTkinter root window.
        """
        self.root = root
        self._configure_window()
        self._setup_background()
        self._set_icon()
        self._load_icons()
        self._create_frames()
        self._create_buttons()
        self._create_search_inputs()
        self._create_results_widgets()
        self._setup_tooltips()

    def _configure_window(self):
        """Configure the main window size, title, and appearance."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        dpi = self.root.winfo_fpixels('1i') or 96  # Fallback to 96 if invalid
        dpi_factor = max(1.0, dpi / 96)  # Ensure at least 1.0
        self.scale_factor = max(
            0.8, min(3.0, min(screen_width / 1920, screen_height / 1080) * dpi_factor)
        )
        self.window_width = int(WIDTH * self.scale_factor)
        self.window_height = int(HEIGHT * self.scale_factor)
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.title(TITLE)
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme(resource_path("Resources/harle.json"))
        ctk.set_widget_scaling(1.0)  # Disable CustomTkinter’s scaling
        self.root.option_add("*Font", ("Open Sans", int(16 * self.scale_factor)))
        self.root.wm_attributes("-toolwindow", False)
        self.root.wm_geometry(f"+0+{int(10 * self.scale_factor)}")

    def _setup_background(self):
        """Load and set the background image for the main window."""
        if not os.path.exists(IMAGE_PATH):
            raise FileNotFoundError(f"Image file not found at: {IMAGE_PATH}")
        image = Image.open(resource_path("Resources/storm.jpg"))
        ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(self.window_width, self.window_height),
        )
        bg_label = ctk.CTkLabel(self.root, text="", image=ctk_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def _set_icon(self):
        """Create and set the application icon."""
        img = Image.open(resource_path("Resources/pirate.png"))
        base_size = int(24 * self.scale_factor)
        sizes = [
            (base_size, base_size),
            (int(48 * self.scale_factor), int(48 * self.scale_factor)),
            (int(72 * self.scale_factor), int(72 * self.scale_factor)),
            (int(96 * self.scale_factor), int(96 * self.scale_factor)),
        ]
        img.save(ICON_PATH, format="ICO", sizes=sizes)
        self.root.iconbitmap(ICON_PATH)

    def _load_icons(self):
        """Load button icons for the GUI."""
        icon_size = (int(30 * self.scale_factor), int(30 * self.scale_factor))
        self.icon_images = {
            "home": ctk.CTkImage(Image.open(resource_path("Resources/home.png")), size=icon_size),
            "form": ctk.CTkImage(Image.open(resource_path("Resources/form.png")), size=icon_size),
            "delete": ctk.CTkImage(Image.open(resource_path("Resources/delete.png")), size=icon_size),
            "search": ctk.CTkImage(Image.open(resource_path("Resources/search.png")), size=icon_size),
            "back": ctk.CTkImage(Image.open(resource_path("Resources/back.png")), size=icon_size),
            "coffee": ctk.CTkImage(Image.open(resource_path("Resources/coffee.png")), size=icon_size),
            "selected": ctk.CTkImage(Image.open(resource_path("Resources/selected.png")), size=icon_size),
            "unselected": ctk.CTkImage(Image.open(resource_path("Resources/unselected.png")), size=icon_size),
        }

    def _create_frames(self):
        """Initialize main frames for the GUI."""
        frame_config = {
            "corner_radius": int(12 * self.scale_factor),
            "fg_color": "white",
            "bg_color": "transparent",
        }
        # Landing frame
        self.landing_frame = ctk.CTkFrame(
            self.root,
            width=int(330 * self.scale_factor),
            height=int(self.window_height),
            **frame_config,
        )
        self.landing_frame.place(x=int(370 * self.scale_factor), y=0)
        self.landing_frame.pack_propagate(False)

        # Search frame
        self.search_frame = ctk.CTkFrame(
            self.root,
            width=int(535 * self.scale_factor),
            height=int(self.window_height),
            **frame_config,
        )
        self.search_frame.place(x=int(82 * self.scale_factor), y=0)
        self.search_frame.pack_propagate(False)
        self.search_frame.lower()

        # Results frame
        self.results_frame = ctk.CTkFrame(
            self.root,
            width=int(550 * self.scale_factor),
            height=int(self.window_height),
            **frame_config,
        )
        self.results_frame.place(x=int(82 * self.scale_factor), y=0)
        self.results_frame.pack_propagate(False)
        self.results_frame.lower()

        # Refined frame
        self.refined_frame = ctk.CTkFrame(
            self.root,
            width=int(535 * self.scale_factor),
            height=int(self.window_height),
            **frame_config,
        )
        self.refined_frame.place(x=int(82 * self.scale_factor), y=0)
        self.refined_frame.pack_propagate(False)
        self.refined_frame.lower()

    def _create_buttons(self):
        """Create navigation and action buttons with scaled sizes."""
        button_config = {
            "fg_color": "white",
            "height": int(40 * self.scale_factor),
            "width": int(40 * self.scale_factor),
            "border_width": 0,
        }
        # Home button
        self.home_button = ctk.CTkButton(
            self.root, text="", image=self.icon_images["home"], **button_config
        )

        # Form button
        self.form_button = ctk.CTkButton(
            self.root,
            text="",
            image=self.icon_images["form"],
            command=self.form,
            **button_config,
        )

        # Delete button
        self.del_button = ctk.CTkButton(
            self.root, text="", image=self.icon_images["delete"], **button_config
        )

        # Refine button
        self.refine_button = ctk.CTkButton(
            self.root, text="", image=self.icon_images["search"], **button_config
        )

        # Back button
        self.back_button = ctk.CTkButton(
            self.root,
            text="",
            image=self.icon_images["back"],
            command=self._return_to_results,
            **button_config,
        )

        # Coffee button
        self.coffee_button = ctk.CTkButton(
            self.landing_frame,
            text="",
            image=self.icon_images["coffee"],
            command=lambda: webbrowser.open("https://ko-fi.com/massauto"),
            **button_config,
        )
        self.coffee_button.configure(fg_color="#a01f8c")

        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            border_width=1,
            font=("Open Sans", int(15 * self.scale_factor)),
            text_color="white",
            fg_color="#a01f8c",
            corner_radius=int(10 * self.scale_factor),
            width=int(120 * self.scale_factor),
            height=int(40 * self.scale_factor),
        )

        # Save new button
        self.save_new_button = ctk.CTkButton(
            self.search_frame,
            text="New Save",
            border_width=1,
            font=("Open Sans", int(15 * self.scale_factor)),
            text_color="white",
            fg_color="#a01f8c",
            corner_radius=int(10 * self.scale_factor),
            width=int(120 * self.scale_factor),
            height=int(40 * self.scale_factor),
            command=self.save,
        )

        # Overwrite button
        self.overwrite_button = ctk.CTkButton(
            self.search_frame,
            text="Overwrite",
            border_width=1,
            font=("Open Sans", int(15 * self.scale_factor)),
            text_color="white",
            fg_color="#a01f8c",
            corner_radius=int(10 * self.scale_factor),
            width=int(120 * self.scale_factor),
            height=int(40 * self.scale_factor),
            state="disabled",
            command=self.overwrite,
        )

    def _create_search_inputs(self):
        """Create input fields and labels for the search frame."""
        label_config = {
            "justify": "left",
            "anchor": "w",
            "font": ("Open Sans", int(15 * self.scale_factor), "bold"),
            "text_color": "#a01f8c",
        }
        entry_config = {
            "corner_radius": int(10 * self.scale_factor),
            "fg_color": "#a01f8c",
            "font": ("Open Sans", int(14 * self.scale_factor), "bold"),
            "border_color": "white",
            "text_color": "white",
        }
        self.url_label = ctk.CTkLabel(
            self.search_frame, text="\nPlease paste a Pirate Bay link or proxy:\n", **label_config
        )
        self.url_label.place(x=int(15 * self.scale_factor), y=int(10 * self.scale_factor))
        self.url_input = ctk.CTkEntry(
            self.search_frame,
            width=int(352 * self.scale_factor),
            height=int(30 * self.scale_factor),
            **entry_config,
        )
        self.url_input.place(in_=self.url_label, anchor="nw", y=int(47 * self.scale_factor))
        self.url_check_button = ctk.CTkButton(
            self.search_frame,
            text="Check",
            border_width=1,
            width=int(120 * self.scale_factor),
            height=int(30 * self.scale_factor),
            font=("Open Sans", int(15 * self.scale_factor)),
            text_color="white",
            fg_color="#a01f8c",
            corner_radius=int(10 * self.scale_factor),
            command=lambda: self.proxy_checker(self.url_input.get()),
        )
        self.url_check_button.place(in_=self.url_input, anchor="nw", x=int(362 * self.scale_factor))

        self.user_label = ctk.CTkLabel(
            self.search_frame,
            text="Enter users to search, separated by commas:",
            **label_config,
        )
        self.user_label.place(in_=self.url_label, y=int(92 * self.scale_factor))
        self.user_input = ctk.CTkEntry(
            self.search_frame,
            width=int(502 * self.scale_factor),
            height=int(30 * self.scale_factor),
            **entry_config,
        )
        self.user_input.place(in_=self.user_label, y=int(36 * self.scale_factor))

        self.term_label = ctk.CTkLabel(
            self.search_frame,
            text="Enter search terms, separated by commas:",
            **label_config,
        )
        self.term_label.place(in_=self.user_label, anchor="nw", y=int(76 * self.scale_factor))
        self.term_box = ctk.CTkTextbox(
            self.search_frame,
            width=int(502 * self.scale_factor),
            height=int(200 * self.scale_factor),
            **entry_config,
        )
        self.term_box.place(in_=self.term_label, anchor="nw", y=int(35 * self.scale_factor))

        self.note_box = ctk.CTkTextbox(
            self.search_frame,
            width=int(502 * self.scale_factor),
            height=int(100 * self.scale_factor),
            **entry_config,
        )
        self.note_box.insert(
            "0.0",
            "Note to user:\n\nThe official Pirate Bay URL yields the best results.\n"
            "thepiratebay.org/",
        )
        self.note_box.place(
            in_=self.search_button, anchor="nw", x=int(-10 * self.scale_factor), y=int(55 * self.scale_factor)
        )

        self.search_button.place(
            in_=self.term_box, anchor="nw", x=int(10 * self.scale_factor), y=int(214 * self.scale_factor)
        )
        self.save_new_button.place(in_=self.search_button, x=int(178 * self.scale_factor))
        self.overwrite_button.place(in_=self.save_new_button, x=int(180 * self.scale_factor))

    def _create_results_widgets(self):
        """Create widgets for displaying search and refined results."""
        textbox_config = {
            "corner_radius": int(10 * self.scale_factor),
            "fg_color": "#a01f8c",
            "text_color": "white",
            "border_color": "white",
            "font": ("Open Sans", int(14 * self.scale_factor), "bold"),
            "width": int(502 * self.scale_factor),
        }
        self.results_box = ctk.CTkTextbox(
            self.results_frame,
            height=int((HEIGHT - 100) * self.scale_factor),
            **textbox_config,
        )
        self.results_box.pack(pady=int(20 * self.scale_factor))

        self.refined_box = ctk.CTkTextbox(
            self.refined_frame,
            height=int((HEIGHT - 50) * self.scale_factor),
            **textbox_config,
        )
        self.refined_box.pack(pady=int(20 * self.scale_factor))

        # Sorting buttons
        sort_label_config = {
            "font": ("Open Sans", int(18 * self.scale_factor), "bold"),
            "text_color": "#a01f8c",
        }
        sort_button_config = {
            "fg_color": "white",
            "image": self.icon_images["selected"],
            "border_width": 0,
            "width": 0,
            "text": "",
        }
        self.sort_buttons = {
            "new": {
                "label": ctk.CTkLabel(self.results_frame, text="Newest", **sort_label_config),
                "button": ctk.CTkButton(self.results_frame, **sort_button_config),
            },
            "old": {
                "label": ctk.CTkLabel(self.results_frame, text="Oldest", **sort_label_config),
                "button": ctk.CTkButton(self.results_frame, **sort_button_config),
            },
            "large": {
                "label": ctk.CTkLabel(self.results_frame, text="Largest", **sort_label_config),
                "button": ctk.CTkButton(self.results_frame, **sort_button_config),
            },
            "small": {
                "label": ctk.CTkLabel(self.results_frame, text="Smallest", **sort_label_config),
                "button": ctk.CTkButton(self.results_frame, **sort_button_config),
            },
            "seed": {
                "label": ctk.CTkLabel(self.results_frame, text="Seeded", **sort_label_config),
                "button": ctk.CTkButton(self.results_frame, **sort_button_config),
            },
            "random": {
                "label": ctk.CTkLabel(self.results_frame, text="Random", **sort_label_config),
                "button": ctk.CTkButton(self.results_frame, **sort_button_config),
            },
        }

    def _setup_tooltips(self):
        """Configure tooltips for navigation buttons."""
        self.tooltips = Pmw.Balloon(
            self.root,
            label_background="#a01f8c",
            label_foreground="white",
            label_font=("Open Sans", int(25 * self.scale_factor))
        )
        self.tooltips.bind(self.home_button, "Return to the landing page and clear all data.")
        self.tooltips.bind(self.form_button, "Go to the search page to save or amend data.")
        self.tooltips.bind(self.del_button, "Delete the current dataset.")
        self.tooltips.bind(self.refine_button, "Filter torrent titles further.")
        self.tooltips.bind(self.back_button, "Return to previous search results.")

    def init(self):
        """Initialize the application, displaying the landing page."""
        csv_files = [file for file in os.listdir() if file.endswith(".csv")]
        title_label = ctk.CTkLabel(
            self.landing_frame,
            wraplength=int(300 * self.scale_factor),
            justify="center",
            anchor="w",
            font=("Open Sans", int(28 * self.scale_factor), "bold"),
            text_color="#a01f8c",
        )
        title_label.pack(pady=int(10 * self.scale_factor), padx=int(10 * self.scale_factor))

        if csv_files:
            title_label.configure(text="\nWelcome back to the Pirate User Searcher!\n")
            self.note_label = ctk.CTkLabel(
                self.landing_frame,
                text="Start a fresh search or;\nSelect a previous dataset from the dropdown box below:\n",
                wraplength=int(300 * self.scale_factor),
                justify="left",
                anchor="w",
                font=("Open Sans", int(20 * self.scale_factor)),
                text_color="#a01f8c",
            )
            self.note_label.pack(pady=int(12 * self.scale_factor), padx=int(10 * self.scale_factor))
            self.fresh_button = ctk.CTkButton(
                self.landing_frame,
                text="Fresh",
                border_width=1,
                font=("Open Sans", int(17 * self.scale_factor)),
                text_color="white",
                fg_color="#a01f8c",
                corner_radius=int(10 * self.scale_factor),
                width=int(150 * self.scale_factor),
                height=int(40 * self.scale_factor),
                command=lambda: (self.fresh(), self.del_button.place_forget()),
            )
            self.fresh_button.pack(pady=int(10 * self.scale_factor), padx=int(10 * self.scale_factor))
            self.csv_combo = ctk.CTkComboBox(
                self.landing_frame,
                values=csv_files,
                fg_color="#a01f8c",
                text_color="white",
                font=("Open Sans", int(15 * self.scale_factor)),
                dropdown_fg_color="#a01f8c",
                border_color="#a01f8c",
                width=int(150 * self.scale_factor),
                height=int(40 * self.scale_factor),
                corner_radius=int(10 * self.scale_factor),
                dropdown_font=("Open Sans", int(15 * self.scale_factor)),
                command=self.load,
            )
            self.csv_combo.pack(pady=int(10 * self.scale_factor), padx=int(10 * self.scale_factor))
            self.coffee_button.place(x=int(270 * self.scale_factor), y=int(540 * self.scale_factor))
        else:
            title_label.configure(text="\nWelcome to the Pirate User Searcher!\n")
            self.note_label = ctk.CTkLabel(
                self.landing_frame,
                text="No datasets found.\n\n"
                     "If you have existing datasets, please place them in the directory containing this script/exe and "
                     "restart.\n\n"
                     "Otherwise, start a fresh search below:\n"
                     ,
                wraplength=int(300 * self.scale_factor),
                justify="left",
                anchor="w",
                font=("Open Sans", int(20 * self.scale_factor)),
                text_color="#a01f8c",
            )
            self.note_label.pack(pady=int(12 * self.scale_factor), padx=int(10 * self.scale_factor))
            self.cont_button = ctk.CTkButton(
                self.landing_frame,
                text="Fresh",
                border_width=1,
                font=("Open Sans", int(17 * self.scale_factor)),
                text_color="white",
                fg_color="#a01f8c",
                corner_radius=int(10 * self.scale_factor),
                width=int(150 * self.scale_factor),
                height=int(40 * self.scale_factor),
                command=self.fresh,
            )
            self.cont_button.pack(pady=int(10 * self.scale_factor), padx=int(10 * self.scale_factor))

    def load(self, value):
        """Load data from a selected CSV file.

        Args:
            value: The name of the CSV file to load.
        """
        global PIRATE_URL, LOADED_USERS, LOADED_TERMS, CHOSEN_CSV
        self.root.title(f"{TITLE}: {value}")
        CHOSEN_CSV = value
        df = pd.read_csv(value)
        PIRATE_URL = df.at[0, "URL"]
        loaded_users = eval(df.at[0, "Usernames"])
        LOADED_USERS = ",".join(loaded_users)
        loaded_terms = eval(df.at[0, "Search_Terms"])
        LOADED_TERMS = [term + "," for term in loaded_terms]
        LOADED_TERMS = list(set(LOADED_TERMS))
        LOADED_TERMS[-1] = LOADED_TERMS[-1][:-1]
        self.del_button.place(in_=self.form_button, y=int(44 * self.scale_factor))
        self.fresh()

    def overwrite(self):
        """Overwrite the current CSV with new search data."""
        global PIRATE_URL, SEARCH_TERMS, USERNAMES, CHOSEN_CSV
        box = CTkMessagebox.CTkMessagebox(
            title="Warning",
            message="Are you sure you want to overwrite this search data?",
            font=("Open Sans", int(14 * self.scale_factor)),
            icon="warning",
            option_1="No",
            option_2="Yes",
            width=int(400 * self.scale_factor),
            height=int(200 * self.scale_factor),
            button_width=int(100 * self.scale_factor),
            button_height=int(30 * self.scale_factor),
            wraplength=int(350 * self.scale_factor),
            justify="left",
        )
        box.button_2.configure(width=int(100 * self.scale_factor))
        if box.get() == "Yes":
            if not self._validate_inputs():
                return
            PIRATE_URL = self.url_input.get()
            USERNAMES = self._process_input(self.user_input.get(), capitalize=True)
            SEARCH_TERMS = self._process_input(self.term_box.get("0.0", "end-1c"))
            df = pd.DataFrame({"URL": [PIRATE_URL], "Usernames": [USERNAMES], "Search_Terms": [SEARCH_TERMS]})
            df.to_csv(CHOSEN_CSV, index=False)
            CTkMessagebox.CTkMessagebox(
                title="Save Complete",
                message="Your dataset has been overwritten.",
                font=("Open Sans", int(14 * self.scale_factor)),
                icon="warning",
                option_1="OK",
                width=int(400 * self.scale_factor),
                height=int(200 * self.scale_factor),
                button_width=int(100 * self.scale_factor),
                button_height=int(30 * self.scale_factor),
                wraplength=int(350 * self.scale_factor),
                justify="left",
            )

    def save(self):
        """Save search data to a new CSV file."""
        global PIRATE_URL, SEARCH_TERMS, USERNAMES
        if not self._validate_inputs():
            return
        csv_files = [file for file in os.listdir() if file.endswith(".csv")]
        illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        while True:
            file_name = ctk.CTkInputDialog(
                text="Please give a name to this dataset:",
                title="Save as new",
                font=("Open Sans", int(14 * self.scale_factor)),
            )
            file_name = file_name.get_input()
            if not file_name:
                return
            file_name = file_name.lower().replace(".csv", "") + ".csv"
            if any(char in file_name for char in illegal_chars):
                msgbox = CTkMessagebox.CTkMessagebox(
                    title="Warning",
                    message="This name contains illegal characters.\nPlease choose a new file name.",
                    font=("Open Sans", int(14 * self.scale_factor)),
                    icon="warning",
                    option_1="OK",
                    width=int(400 * self.scale_factor),
                    height=int(200 * self.scale_factor),
                    button_width=int(100 * self.scale_factor),
                    button_height=int(30 * self.scale_factor),
                    wraplength=int(350 * self.scale_factor),
                    justify="left",
                )
                msgbox.wait_window()
                continue
            if file_name in csv_files:
                msgbox = CTkMessagebox.CTkMessagebox(
                    title="Warning",
                    message="This name already exists.\nPlease choose a new name.",
                    font=("Open Sans", int(14 * self.scale_factor)),
                    icon="warning",
                    option_1="OK",
                    width=int(400 * self.scale_factor),
                    height=int(200 * self.scale_factor),
                    button_width=int(100 * self.scale_factor),
                    button_height=int(30 * self.scale_factor),
                    wraplength=int(350 * self.scale_factor),
                    justify="left",
                )
                msgbox.wait_window()
                continue
            PIRATE_URL = self.url_input.get()
            USERNAMES = self._process_input(self.user_input.get(), capitalize=True)
            SEARCH_TERMS = self._process_input(self.term_box.get("0.0", "end-1c"))
            df = pd.DataFrame({"URL": [PIRATE_URL], "Usernames": [USERNAMES], "Search_Terms": [SEARCH_TERMS]})
            df.to_csv(file_name, index=False)
            CTkMessagebox.CTkMessagebox(
                title="Save Complete",
                message="Your dataset has been saved.",
                font=("Open Sans", int(14 * self.scale_factor)),
                icon="warning",
                option_1="OK",
                width=int(400 * self.scale_factor),
                height=int(200 * self.scale_factor),
                button_width=int(100 * self.scale_factor),
                button_height=int(30 * self.scale_factor),
                wraplength=int(350 * self.scale_factor),
                justify="left",
            )
            self.url_input.delete(0, ctk.END)
            self.user_input.delete(0, ctk.END)
            self.term_box.delete("0.0", "end-1c")
            self.load(file_name)
            break

    def _validate_inputs(self):
        """Validate that all input fields are filled.

        Returns:
            bool: True if all inputs are valid, False otherwise.
        """
        if not all([self.url_input.get(), self.user_input.get(), self.term_box.get("0.0", "end-1c")]):
            CTkMessagebox.CTkMessagebox(
                title="Warning",
                message="The form is incomplete.\nPlease fill in all three entries.",
                font=("Open Sans", int(14 * self.scale_factor)),
                icon="warning",
                option_1="OK",
                width=int(400 * self.scale_factor),
                height=int(200 * self.scale_factor),
                button_width=int(100 * self.scale_factor),
                button_height=int(30 * self.scale_factor),
                wraplength=int(350 * self.scale_factor),
                justify="left",
            )
            return False
        return True

    def _process_input(self, input_str, capitalize=False):
        """Process comma-separated input into a unique list.

        Args:
            input_str: The input string to process.
            capitalize: Whether to capitalize each item.

        Returns:
            list: A list of unique, processed items.
        """
        items = input_str.split(",")
        items = [item.strip() for item in items if item.strip()]
        if capitalize:
            items = [item.capitalize() for item in items]
        return list(set(items))

    def home(self):
        """Reset the application to the landing page."""
        global PIRATE_URL, USERNAMES, LOADED_TERMS, LOADED_USERS, SEARCH_TERMS, CHOSEN_CSV, BUTTON_EXIST
        self.root.title(TITLE)
        csv_files = [file for file in os.listdir() if file.endswith(".csv")]
        if csv_files:
            try:
                self.note_label.configure(text="Start a fresh search or select a dataset:\n")
                self.csv_combo.configure(values=csv_files)
                self.csv_combo.pack(pady=int(10 * self.scale_factor), padx=int(10 * self.scale_factor))
            except AttributeError:
                self.cont_button.configure(command=lambda: (self.fresh(), self.del_button.place_forget()))
                self.note_label.configure(text="Start a fresh search or select a dataset:\n")
                self.csv_combo = ctk.CTkComboBox(
                    self.landing_frame,
                    values=csv_files,
                    fg_color="#a01f8c",
                    text_color="white",
                    font=("Open Sans", int(15 * self.scale_factor)),
                    dropdown_fg_color="#a01f8c",
                    border_color="#a01f8c",
                    width=int(150 * self.scale_factor),
                    height=int(40 * self.scale_factor),
                    corner_radius=int(10 * self.scale_factor),
                    dropdown_font=("Open Sans", int(15 * self.scale_factor)),
                    command=self.load,
                )

                self.csv_combo.configure(values=csv_files)
                self.csv_combo.pack(pady=int(10 * self.scale_factor), padx=int(10 * self.scale_factor))
        else:
            self.note_label.configure(text="Start a fresh search below:")
            try:
                self.csv_combo.pack_forget()
            except AttributeError:
                pass
        PIRATE_URL = ""
        USERNAMES = []
        LOADED_USERS = ""
        SEARCH_TERMS = []
        LOADED_TERMS = ""
        CHOSEN_CSV = ""
        self.search_frame.lower()
        self.results_frame.lower()
        self.landing_frame.lift()
        self.refined_frame.lower()
        self.url_input.delete(0, ctk.END)
        self.user_input.delete(0, ctk.END)
        self.term_box.delete("0.0", "end-1c")
        self.results_box.delete("0.0", "end-1c")
        self.form_button.place_forget()
        self.home_button.place_forget()
        self.refine_button.place_forget()
        self.back_button.place_forget()
        BUTTON_EXIST = False
        self._hide_sort_buttons()
        self.de_select('non')

    def form(self):
        """Switch to the search form and clear previous data."""
        global PIRATE_URL, USERNAMES, LOADED_TERMS, LOADED_USERS, SEARCH_TERMS, CHOSEN_CSV
        PIRATE_URL = ""
        USERNAMES = []
        LOADED_USERS = ""
        SEARCH_TERMS = []
        LOADED_TERMS = ""
        self.search_frame.lift()
        self.results_frame.lower()
        self.landing_frame.lower()
        self.results_box.delete("0.0", "end-1c")
        self.refine_button.place_forget()
        self.back_button.place_forget()
        if CHOSEN_CSV:
            self.del_button.place(in_=self.form_button, y=int(44 * self.scale_factor))
        self._hide_sort_buttons()
        self.de_select('non')

    def delete(self):
        """Delete the selected CSV file."""
        box = CTkMessagebox.CTkMessagebox(
            title="Warning",
            message="Are you sure you want to delete this dataset?",
            font=("Open Sans", int(14 * self.scale_factor)),
            icon="warning",
            option_1="No",
            option_2="Yes",
            width=int(400 * self.scale_factor),
            height=int(200 * self.scale_factor),
            button_width=int(100 * self.scale_factor),
            button_height=int(30 * self.scale_factor),
            wraplength=int(350 * self.scale_factor),
            justify="left",
        )
        box.button_2.configure(width=int(100 * self.scale_factor))
        if box.get() == "Yes":
            os.remove(CHOSEN_CSV)
            self.home()

    def fresh(self):
        """Start a fresh search, updating UI and buttons."""
        global BUTTON_EXIST
        self.landing_frame.lower()
        self.search_frame.lift()
        self.overwrite_button.configure(state="normal" if CHOSEN_CSV else "disabled")
        if not BUTTON_EXIST:
            self.home_button.place(x=int(22 * self.scale_factor), y=int(7 * self.scale_factor))
            self.form_button.place(in_=self.home_button, y=int(44 * self.scale_factor))
            if CHOSEN_CSV:
                self.del_button.configure(command=self.delete)
                self.del_button.place(in_=self.form_button, y=int(44 * self.scale_factor))
            BUTTON_EXIST = True
            self.home_button.configure(command=self.home)
        self.search_button.configure(
            command=lambda: (
                self.lister(
                    self.url_input.get(),
                    self.user_input.get(),
                    self.term_box.get("1.0", "end-1c"),
                    self.search_frame,
                ),
                self.del_button.place_forget(),
            )
        )
        self.url_input.delete(0, ctk.END)
        self.url_input.insert(0, PIRATE_URL)
        self.user_input.delete(0, ctk.END)
        self.user_input.insert(0, LOADED_USERS)
        self.term_box.delete("0.0", "end-1c")
        self.term_box.insert("0.0", LOADED_TERMS)

    def proxy_checker(self, url):
        """Check if a Pirate Bay URL is valid.
        Args:
            url: The URL to check.
        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        global PIRATE_URL
        url = self._normalize_url(url)
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.ok:
                PIRATE_URL = url
                CTkMessagebox.CTkMessagebox(
                    title="Check",
                    message="The URL is working!",
                    font=("Open Sans", int(14 * self.scale_factor)),
                    icon="check",
                    option_1="OK",
                    width=int(400 * self.scale_factor),
                    height=int(200 * self.scale_factor),
                    button_width=int(100 * self.scale_factor),
                    button_height=int(30 * self.scale_factor),
                    wraplength=int(350 * self.scale_factor),
                    justify="left",
                )
                return True
        except requests.RequestException:
            CTkMessagebox.CTkMessagebox(
                title="Error",
                message="The URL is not working.\nPlease try another.",
                font=("Open Sans", int(14 * self.scale_factor)),
                icon="warning",
                option_1="OK",
                width=int(400 * self.scale_factor),
                height=int(200 * self.scale_factor),
                button_width=int(100 * self.scale_factor),
                button_height=int(30 * self.scale_factor),
                wraplength=int(350 * self.scale_factor),
                justify="left",
            )
            return False

    def proxy_search_checker(self, url):
        """Check if a Pirate Bay URL is valid for search.
        Args:
            url: The URL to check.
        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        global PIRATE_URL
        url = self._normalize_url(url)
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.ok:
                PIRATE_URL = url
                return True
        except requests.RequestException:
            CTkMessagebox.CTkMessagebox(
                title="Error",
                message="The URL is not working.\nPlease try another.",
                font=("Open Sans", int(14 * self.scale_factor)),
                icon="warning",
                option_1="OK",
                width=int(400 * self.scale_factor),
                height=int(200 * self.scale_factor),
                button_width=int(100 * self.scale_factor),
                button_height=int(30 * self.scale_factor),
                wraplength=int(350 * self.scale_factor),
                justify="left",
            )
            return False

    def _normalize_url(self, url):
        """Normalize URL format for consistency.
        Args:
            url: The URL to normalize.
        Returns:
            str: The normalized URL.
        """
        if url.startswith("www."):
            url = url.replace("www.", "")
        if not url.startswith("https://"):
            url = "https://" + url
        if url.endswith("index.html"):
            url = url.replace("index.html", "")
        return url

    def lister(self, url, names, terms, frame):
        """Process input and initiate torrent search.
        Args:
            url: The Pirate Bay URL.
            names: Comma-separated usernames.
            terms: Comma-separated search terms.
            frame: The current frame to lower.
        """
        global PIRATE_URL, USERNAMES, SEARCH_TERMS
        if self.proxy_search_checker(url):
            frame.lower()
            USERNAMES = self._process_input(names, capitalize=True)
            SEARCH_TERMS = self._process_input(terms)
            self.search(USERNAMES, SEARCH_TERMS)
        else:
            return

    def search(self, usernames, search_terms):
        """Search The Pirate Bay and display results.
        Args:
            usernames: List of usernames to filter by.
            search_terms: List of search terms to query.
        """
        self.results_frame.lift()
        self.results_box.delete("0.0", "end")
        self.results_box.insert("0.0", "Searching...\n")
        progress_bar = ctk.CTkProgressBar(
            self.results_frame,
            width=int(300 * self.scale_factor),
            height=int(15 * self.scale_factor),
            progress_color="#a01f8c",
            fg_color="#63003d",
        )
        progress_bar.pack(pady=int(10 * self.scale_factor))
        progress_bar.set(0.0)
        self.root.update()

        combined_data_list = []
        total_steps = len(search_terms) + 3
        current_step = 0

        for term in search_terms:
            params = {"q": term}
            response = requests.get("https://apibay.org/q.php", params=params)
            data = response.json()
            for user in usernames:
                filtered_data = [item for item in data if item["username"] == user]
                combined_data_list.append(filtered_data)
            current_step += 1
            progress_bar.set(current_step / total_steps)
            self.root.update()

        non_empty_data = [x for x in combined_data_list if x]
        dict_list = list(chain(*non_empty_data))
        for item in dict_list:
            item["added"] = int(item["added"])
            item["seeders"] = int(item["seeders"])
            item["size"] = int(item["size"])
        unique_list = []
        [unique_list.append(item) for item in dict_list if item not in unique_list]

        current_step += 1
        progress_bar.set(current_step / total_steps)
        self.root.update()

        counter = 0
        while True:
            try:
                if platform.system() == "Windows":
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                unique_list = asyncio.run(self.check_urls(unique_list))
                working_list = [item for item in unique_list if item["code"] != 404]
                current_step += 1
                progress_bar.set(current_step / total_steps)
                self.root.update()
                self.results_box.delete("0.0", "end")
                self.results_box.insert(
                    "0.0", f"Found {len(working_list)} working results.\n\nChoose a sorting option below:\n\n"
                )
                self._show_sort_buttons(working_list)
                break
            except Exception:
                counter += 1
                if counter > 3:
                    self.results_box.delete("0.0", "end")
                    self.results_box.insert(
                        "0.0",
                        f"Could not remove dead URLs.\n\nYou can continue with all {len(unique_list)} results.\n\n"
                        f"Choose a sorting option below: \n\n",
                    )
                    progress_bar.set(1.0)
                    self.root.update()
                    self._show_sort_buttons(unique_list)
                    break
                self.results_box.delete("0.0", "end")
                self.results_box.insert("0.0", f"Attempt: {counter}/3\nThe server disconnected. Trying again...\n")
                progress_bar.set(current_step / total_steps)
                self.root.update()
                time.sleep(1)

        progress_bar.pack_forget()

    def de_select(self, selected):
        """Highlight the selected sorting button and reset others.
        Args:
            selected: The key of the selected sorting button.
        """
        buttons = ["new", "old", "large", "small", "seed", "random"]
        for item in buttons:
            fg_color = "#63003d" if item == selected else "white"
            self.sort_buttons[item]["button"].configure(fg_color=fg_color)

    def _show_sort_buttons(self, item_list):
        """Display sorting buttons for search results.
        Args:
            item_list: The list of torrent items to sort.
        """
        # Newest
        self.sort_buttons["new"]["label"].place(
            in_=self.results_box, x=int(56 * self.scale_factor), y=int((HEIGHT - 100) * self.scale_factor)
        )
        self.sort_buttons["new"]["button"].configure(
            command=lambda: (self.sorter(item_list, "n", self.results_frame), self.de_select("new"))
        )
        self.sort_buttons["new"]["button"].place(
            in_=self.sort_buttons["new"]["label"], y=int(25 * self.scale_factor), x=int(8 * self.scale_factor)
        )

        # Oldest
        self.sort_buttons["old"]["label"].place(in_=self.sort_buttons["new"]["label"], x=int(75 * self.scale_factor))
        self.sort_buttons["old"]["button"].configure(
            command=lambda: (self.sorter(item_list, "o", self.results_frame), self.de_select("old"))
        )
        self.sort_buttons["old"]["button"].place(
            in_=self.sort_buttons["old"]["label"], y=int(25 * self.scale_factor), x=int(12 * self.scale_factor)
        )

        # Largest
        self.sort_buttons["large"]["label"].place(
            in_=self.sort_buttons["new"]["label"], x=int(75 * self.scale_factor)
        )
        self.sort_buttons["large"]["button"].configure(
            command=lambda: (self.sorter(item_list, "l", self.results_frame), self.de_select("large"))
        )
        self.sort_buttons["large"]["button"].place(
            in_=self.sort_buttons["large"]["label"], y=int(25 * self.scale_factor), x=int(8 * self.scale_factor)
        )

        # Smallest
        self.sort_buttons["small"]["label"].place(
            in_=self.sort_buttons["large"]["label"], x=int(75 * self.scale_factor)
        )
        self.sort_buttons["small"]["button"].configure(
            command=lambda: (self.sorter(item_list, "sm", self.results_frame), self.de_select("small"))
        )
        self.sort_buttons["small"]["button"].place(
            in_=self.sort_buttons["small"]["label"], y=int(25 * self.scale_factor), x=int(16 * self.scale_factor)
        )

        # Seeded
        self.sort_buttons["seed"]["label"].place(
            in_=self.sort_buttons["small"]["label"], x=int(85 * self.scale_factor)
        )
        self.sort_buttons["seed"]["button"].configure(
            command=lambda: (self.sorter(item_list, "s", self.results_frame), self.de_select("seed"))
        )
        self.sort_buttons["seed"]["button"].place(
            in_=self.sort_buttons["seed"]["label"], y=int(25 * self.scale_factor), x=int(10 * self.scale_factor)
        )

        # Random
        self.sort_buttons["random"]["label"].place(
            in_=self.sort_buttons["seed"]["label"], x=int(75 * self.scale_factor)
        )
        self.sort_buttons["random"]["button"].configure(
            command=lambda: (self.sorter(item_list, "r", self.results_frame), self.de_select("random"))
        )
        self.sort_buttons["random"]["button"].place(
            in_=self.sort_buttons["random"]["label"], y=int(25 * self.scale_factor), x=int(12 * self.scale_factor)
        )

    def _hide_sort_buttons(self):
        """Hide all sorting buttons from the results frame."""
        for button in self.sort_buttons.values():
            button["label"].place_forget()
            button["button"].place_forget()

    def refine(self, results):
        """Refine search results based on user input.
        Args:
            results: The list of torrent results to refine.
        """
        name_list = [item["name"] for item in results]
        to_find = ctk.CTkInputDialog(
            text="Search through the titles for:",
            title="To find",
            font=("Open Sans", int(14 * self.scale_factor)),
        )
        to_find = to_find.get_input()
        if not to_find:
            return
        collect_list = [item for item in name_list if to_find.lower() in item.lower()]
        refined_list = [item for item in results if item["name"] in collect_list]
        self.results_frame.lower()
        self.refined_frame.lift()
        self.ref_printer(refined_list, self.refined_frame, self.refined_box)
        self.back_button.place(in_=self.refine_button)

    def _return_to_results(self):
        """Return to the main results frame from refined results."""
        self.refined_frame.lower()
        self.results_frame.lift()
        self.back_button.place_forget()

    def ref_printer(self, results, frame, box):
        """Display refined search results.
        Args:
            results: The list of refined torrent results.
            frame: The frame to display the results in.
            box: The textbox to insert the results into.
        """
        box.delete("0.0", "end")
        box.insert("0.0", "\nHere are your refined results:\n\n\n")
        self._print_results(results, box)

    def printer(self, results, frame):
        """Display search results with sorting options.

        Args:
            results: The list of torrent results to display.
            frame: The frame to display the results in.
        """
        self.refine_button.configure(command=lambda: self.refine(results))
        self.refine_button.place(in_=self.form_button, y=int(44 * self.scale_factor))
        self.results_box.delete("0.0", "end")
        self.results_box.insert(
            "0.0",
            "\nNOTICE:\n\n"
            "The first 100 results include relevant URLs from the torrent's page\n(e.g., screenshots).\n\n"
            f"This is limited to the first {MAX_RESULTS_WITH_LINKS} results.\n\n"
            "To save time; the relevant URLs have not been checked.\n\n"
            "Enjoy the results and:\n\n- Re-sort at the bottom.\n\n- Return to form for saving at the side."
            "\n\n- Filter through the titles also at the side.\n\n\n\n"
        )
        self._print_results(results, self.results_box)

    def _print_results(self, results, box):
        """Insert torrent details into the specified textbox.

        Args:
            results: The list of torrent results to display.
            box: The textbox to insert the results into.
        """
        counter = 0
        for idx, item in enumerate(results):
            url = f"{PIRATE_URL}/torrent/{item['id']}"
            box.insert("end", f"{item['name']}\n\n")
            box.insert("end", f"Uploaded by: {item['username']}\n")
            box.insert("end", f"User status: {item['status']}\n")
            size_gb = item["size"] / 1073741824
            box.insert("end", f"File size: {round(size_gb, 2)} GB\n")
            upload_date = datetime.fromtimestamp(item["added"])
            box.insert("end", f"Uploaded: {upload_date}\n")
            box.insert("end", f"Number of seeders: {item['seeders']}\n")
            magnet_link = f"magnet:?xt=urn:btih:{item['info_hash']}"
            magnet_tag = f"magnet_tag_{idx}"
            box.insert("end", f"Hash: {item['info_hash']} ")
            box.insert("end", "🧲", (magnet_tag,))
            box.insert("end", "\n\n")
            box.tag_config(magnet_tag, foreground="red", relief="raised")
            box.tag_bind(magnet_tag, "<Button-1>", lambda e, u=magnet_link: webbrowser.open(u))
            box.tag_bind(magnet_tag, "<Enter>", lambda e: box.configure(cursor="hand2"))
            box.tag_bind(magnet_tag, "<Leave>", lambda e: box.configure(cursor=""))
            box.insert("end", "Site URL:\n\n")
            tag_name = f"button_tag_{idx}"
            box.insert("end", f"{url}", (tag_name,))
            box.insert("end", "\n\n")
            box.tag_config(tag_name, background="white", foreground="#1f6aa8", relief="raised")
            box.tag_bind(tag_name, "<Button-1>", lambda e, u=url: webbrowser.open(u))
            box.tag_bind(tag_name, "<Enter>", lambda e: box.configure(cursor="hand2"))
            box.tag_bind(tag_name, "<Leave>", lambda e: box.configure(cursor=""))

            if idx < MAX_RESULTS_WITH_LINKS:
                info = requests.get(f"https://apibay.org/t.php?id={item['id']}")
                info_data = info.json()
                description = info_data.get("descr", "")
                box.insert("end", "Relevant links:\n\n")
                for line in description.splitlines():
                    if "http" in line:
                        new_tag = f"new_tag_{counter}"
                        box.insert("end", f"{line}", (new_tag,))
                        box.insert("end", "\n\n")
                        box.tag_config(new_tag, background="white", foreground="#1f6aa8", relief="raised")
                        box.tag_bind(new_tag, "<Button-1>", lambda e, u=line: webbrowser.open(u))
                        box.tag_bind(new_tag, "<Enter>", lambda e: box.configure(cursor="hand2"))
                        box.tag_bind(new_tag, "<Leave>", lambda e: box.configure(cursor=""))
                        counter += 1

    def sorter(self, item_list, value, frame):
        """Sort search results based on user preference.
        Args:
            item_list: The list of torrent items to sort.
            value: The sorting criterion ('n', 'o', 's', 'l', 'sm', 'r').
            frame: The frame to display the sorted results in.
        """
        if value == "n":
            sorted_list = sorted(item_list, key=lambda x: x["added"], reverse=True)
        elif value == "o":
            sorted_list = sorted(item_list, key=lambda x: x["added"])
        elif value == "s":
            sorted_list = sorted(item_list, key=lambda x: x["seeders"], reverse=True)
        elif value == "l":
            sorted_list = sorted(item_list, key=lambda x: x["size"], reverse=True)
        elif value == "sm":
            sorted_list = sorted(item_list, key=lambda x: x["size"])
        elif value == "r":
            sorted_list = item_list.copy()
            random.shuffle(sorted_list)
        else:
            sorted_list = item_list
        self.printer(sorted_list, frame)

    async def check_urls(self, item_list):
        """Check torrent            item_list: The list of torrent items to check.
        Returns:
            list: The updated item list with status codes.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [session.get(f"{PIRATE_URL}/torrent/{item['id']}", ssl=False) for item in item_list]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for idx, item in enumerate(item_list):
                item["code"] = responses[idx].status if hasattr(responses[idx], "status") else 404
        return item_list

if __name__ == "__main__":
    root = ctk.CTk()
    app = PirateSearcherApp(root)
    app.init()
    root.mainloop()