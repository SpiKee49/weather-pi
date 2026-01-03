#!/usr/bin/env python3
import tkinter as tk
from tkinter import font
import requests
from datetime import datetime, timedelta
import json


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Display")

        # Fullscreen na LCD (480x320)
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.geometry('480x320')

        # Skry kurzor
        self.root.config(cursor="none")

        # Súradnice - budú sa automaticky zistiť
        self.LATITUDE = None
        self.LONGITUDE = None
        self.CITY = "Loading..."

        # Auto-rotate timer
        self.auto_rotate_enabled = True
        self.auto_rotate_interval = 10000  # 10 sekúnd
        self.auto_rotate_timer = None

        # Aktuálna stránka
        self.current_page = 0
        self.pages = []

        # Hlavný container
        self.main_container = tk.Frame(self.root, bg='black', height=290)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.main_container.pack_propagate(False)

        # Vytvor stránky
        self.create_pages()

        # Načítaj počasie
        self.weather_data = None
        self.forecast_data = None

        # Najprv získaj polohu, potom počasie
        self.get_location()

        # Navigačné tlačidlá (na spodku)
        self.create_navigation()

        # ESC pre ukončenie
        self.root.bind('<Escape>', lambda e: self.root.quit())

        # Zobraz prvú stránku
        self.show_page(0)

        # Spusti auto-rotate
        self.start_auto_rotate()

    def get_location(self):
        """Automaticky zisti polohu pomocou IP geolokácie"""
        try:
            response = requests.get('http://ip-api.com/json/', timeout=10)
            data = response.json()

            if data['status'] == 'success':
                self.LATITUDE = data['lat']
                self.LONGITUDE = data['lon']
                self.CITY = f"{data['city']}, {data['countryCode']}"

                print(
                    f"Location detected: {self.CITY} ({self.LATITUDE}, {self.LONGITUDE})")

                # Aktualizuj city label
                self.city_label.config(text=self.CITY)

                # Teraz môžeme načítať počasie
                self.update_weather()
            else:
                self.use_fallback_location()
        except Exception as e:
            print(f"Error getting location: {e}")
            self.use_fallback_location()

    def use_fallback_location(self):
        """Použije predvolenú polohu ak zlyhá automatická detekcia"""
        self.LATITUDE = 48.9333
        self.LONGITUDE = 21.9000
        self.CITY = "Humenné, SK"
        print(f"Using fallback location: {self.CITY}")
        self.city_label.config(text=self.CITY)
        self.update_weather()

    def manual_location_search(self):
        """Fullscreen stránka pre vyhľadávanie mesta"""
        # Zastaviť auto-rotate počas vyhľadávania
        self.stop_auto_rotate()

        # Vytvor fullscreen search page
        search_page = tk.Frame(self.main_container, bg='black')

        # Nadpis
        title = tk.Label(
            search_page,
            text="Search Location",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=5)

        # Entry field s textom
        entry_frame = tk.Frame(search_page, bg='black')
        entry_frame.pack(pady=5)

        entry_var = tk.StringVar()
        entry_display = tk.Label(
            entry_frame,
            textvariable=entry_var,
            font=('Arial', 12),
            width=30,
            height=1,
            bg='#2a2a2a',
            fg='white',
            relief=tk.SUNKEN,
            anchor='w',
            padx=5
        )
        entry_display.pack()

        result_label = tk.Label(
            search_page,
            text="",
            font=('Arial', 9),
            fg='yellow',
            bg='black'
        )
        result_label.pack(pady=2)

        # Virtuálna klávesnica
        keyboard_frame = tk.Frame(search_page, bg='black')
        keyboard_frame.pack(pady=5)

        # Rozloženie klávesnice - všetky písmená a číslice
        keyboard_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', ',']
        ]

        def key_press(key):
            current = entry_var.get()
            if key == '⌫':
                entry_var.set(current[:-1])
            elif key == 'SPACE':
                entry_var.set(current + ' ')
            elif key == 'CLEAR':
                entry_var.set('')
            else:
                entry_var.set(current + key.lower())

        # Vytvor tlačidlá klávesnice
        for row_idx, row in enumerate(keyboard_layout):
            row_frame = tk.Frame(keyboard_frame, bg='black')
            row_frame.pack()

            for key in row:
                btn = tk.Button(
                    row_frame,
                    text=key,
                    font=('Arial', 9, 'bold'),
                    width=3,
                    height=1,
                    bg='#2a2a2a',
                    fg='white',
                    activebackground='#3a3a3a',
                    relief=tk.RAISED,
                    command=lambda k=key: key_press(k)
                )
                btn.pack(side=tk.LEFT, padx=1, pady=1)

        # Spodný riadok - Space, Backspace, Clear
        bottom_row = tk.Frame(keyboard_frame, bg='black')
        bottom_row.pack()

        backspace_btn = tk.Button(
            bottom_row,
            text='⌫',
            font=('Arial', 9, 'bold'),
            width=6,
            height=1,
            bg='#7a2a2a',
            fg='white',
            activebackground='#8a3a3a',
            relief=tk.RAISED,
            command=lambda: key_press('⌫')
        )
        backspace_btn.pack(side=tk.LEFT, padx=1, pady=1)

        space_btn = tk.Button(
            bottom_row,
            text='SPACE',
            font=('Arial', 9, 'bold'),
            width=18,
            height=1,
            bg='#2a2a2a',
            fg='white',
            activebackground='#3a3a3a',
            relief=tk.RAISED,
            command=lambda: key_press('SPACE')
        )
        space_btn.pack(side=tk.LEFT, padx=1, pady=1)

        clear_btn = tk.Button(
            bottom_row,
            text='CLEAR',
            font=('Arial', 9, 'bold'),
            width=6,
            height=1,
            bg='#7a2a2a',
            fg='white',
            activebackground='#8a3a3a',
            relief=tk.RAISED,
            command=lambda: key_press('CLEAR')
        )
        clear_btn.pack(side=tk.LEFT, padx=1, pady=1)

        def search_city():
            city_name = entry_var.get().strip()
            if not city_name:
                result_label.config(text="Please enter a city name", fg='red')
                return

            result_label.config(text="Searching...", fg='yellow')
            search_page.update()

            try:
                url = "https://geocoding-api.open-meteo.com/v1/search"
                params = {'name': city_name, 'count': 1,
                          'language': 'en', 'format': 'json'}
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    self.LATITUDE = result['latitude']
                    self.LONGITUDE = result['longitude']

                    city = result['name']
                    country = result.get('country', '')
                    self.CITY = f"{city}, {country}"

                    print(
                        f"Location set to: {self.CITY} ({self.LATITUDE}, {self.LONGITUDE})")

                    self.city_label.config(text=self.CITY)
                    self.update_weather()

                    close_search()
                else:
                    result_label.config(
                        text="City not found. Try again.", fg='red')
            except Exception as e:
                print(f"Error searching city: {e}")
                result_label.config(text="Search failed. Try again.", fg='red')

        def close_search():
            search_page.pack_forget()
            self.show_page(self.current_page)
            self.start_auto_rotate()

        # Tlačidlá Search a Cancel
        btn_frame = tk.Frame(search_page, bg='black')
        btn_frame.pack(pady=5)

        cancel_btn = tk.Button(
            btn_frame,
            text="✖ CANCEL",
            font=('Arial', 11, 'bold'),
            bg='#7a2a2a',
            fg='white',
            width=15,
            height=2,
            command=close_search
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        search_btn = tk.Button(
            btn_frame,
            text="✓ SEARCH",
            font=('Arial', 11, 'bold'),
            bg='#2a7a2a',
            fg='white',
            width=15,
            height=2,
            command=search_city
        )
        search_btn.pack(side=tk.LEFT, padx=5)

        # Skry aktuálnu stránku a zobraz search
        for page in self.pages:
            page.pack_forget()
        search_page.pack(fill=tk.BOTH, expand=True)

    def start_auto_rotate(self):
        """Spusti automatické prepínanie stránok"""
        if self.auto_rotate_enabled:
            self.stop_auto_rotate()
            self.auto_rotate_timer = self.root.after(
                self.auto_rotate_interval, self.auto_next_page)

    def stop_auto_rotate(self):
        """Zastaví automatické prepínanie"""
        if self.auto_rotate_timer:
            self.root.after_cancel(self.auto_rotate_timer)
            self.auto_rotate_timer = None

    def auto_next_page(self):
        """Automaticky prejde na ďalšiu stránku v loope"""
        next_page = (self.current_page + 1) % len(self.pages)
        self.show_page(next_page)
        self.start_auto_rotate()

    def create_combined_weather_page(self, parent):
        # ===== HORNÁ POLOVICA - Aktuálne počasie =====
        top_half = tk.Frame(parent, bg='black', height=145)
        top_half.pack(fill=tk.X)
        top_half.pack_propagate(False)

        # Hlavička
        header = tk.Frame(top_half, bg='black')
        header.pack(fill=tk.X, pady=2)

        self.city_label = tk.Label(
            header,
            text="Loading...",
            font=('Arial', 11, 'bold'),
            fg='white',
            bg='black'
        )
        self.city_label.pack()

        self.current_date_label = tk.Label(
            header,
            text="",
            font=('Arial', 8),
            fg='lightgray',
            bg='black'
        )
        self.current_date_label.pack()

        # Hlavné info - teplota a ikona vedľa seba
        main_frame = tk.Frame(top_half, bg='black')
        main_frame.pack(expand=True)

        # Ľavá strana - ikona a popis
        left_side = tk.Frame(main_frame, bg='black')
        left_side.pack(side=tk.LEFT, padx=10)

        self.weather_icon_label = tk.Label(
            left_side,
            text="",
            font=('Arial', 40),
            fg='white',
            bg='black'
        )
        self.weather_icon_label.pack()

        self.current_desc_label = tk.Label(
            left_side,
            text="Loading...",
            font=('Arial', 9),
            fg='lightgray',
            bg='black'
        )
        self.current_desc_label.pack()

        # Pravá strana - teplota a detaily
        right_side = tk.Frame(main_frame, bg='black')
        right_side.pack(side=tk.LEFT, padx=10)

        self.current_temp_label = tk.Label(
            right_side,
            text="--°",
            font=('Arial', 42, 'bold'),
            fg='white',
            bg='black'
        )
        self.current_temp_label.pack()

        # Detaily v 2 stĺpcoch
        details_grid = tk.Frame(right_side, bg='black')
        details_grid.pack()

        self.current_feels_label = tk.Label(
            details_grid,
            text="Feels: --°",
            font=('Arial', 7),
            fg='orange',
            bg='black'
        )
        self.current_feels_label.grid(row=0, column=0, padx=5, sticky='w')

        self.current_humidity_label = tk.Label(
            details_grid,
            text="💧 --%",
            font=('Arial', 7),
            fg='cyan',
            bg='black'
        )
        self.current_humidity_label.grid(row=0, column=1, padx=5, sticky='w')

        self.current_wind_label = tk.Label(
            details_grid,
            text="💨 --",
            font=('Arial', 7),
            fg='lightblue',
            bg='black'
        )
        self.current_wind_label.grid(row=1, column=0, padx=5, sticky='w')

        self.current_pressure_label = tk.Label(
            details_grid,
            text="🌡 --",
            font=('Arial', 7),
            fg='yellow',
            bg='black'
        )
        self.current_pressure_label.grid(row=1, column=1, padx=5, sticky='w')

        # ===== DOLNÁ POLOVICA - 5-dňová predpoveď =====
        bottom_half = tk.Frame(parent, bg='black', height=145)
        bottom_half.pack(fill=tk.BOTH, expand=True)
        bottom_half.pack_propagate(False)

        # Nadpis
        forecast_title = tk.Label(
            bottom_half,
            text="5-Day Forecast",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='black'
        )
        forecast_title.pack(pady=2)

        # Frame pre predpoveď
        self.forecast_frame = tk.Frame(bottom_half, bg='black')
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, padx=3)

        # Vytvor 5 stĺpcov pre dni
        self.forecast_labels = []
        for i in range(5):
            day_frame = tk.Frame(self.forecast_frame,
                                 bg='#1a1a1a', relief=tk.RAISED, borderwidth=1)
            day_frame.grid(row=0, column=i, padx=1, pady=2, sticky='nsew')

            # Deň
            day_label = tk.Label(
                day_frame,
                text="---",
                font=('Arial', 8, 'bold'),
                fg='white',
                bg='#1a1a1a'
            )
            day_label.pack(pady=1)

            # Ikona
            icon_label = tk.Label(
                day_frame,
                text="",
                font=('Arial', 20),
                fg='white',
                bg='#1a1a1a'
            )
            icon_label.pack(pady=1)

            # Max teplota
            max_temp_label = tk.Label(
                day_frame,
                text="--°",
                font=('Arial', 10, 'bold'),
                fg='#ff6b6b',
                bg='#1a1a1a'
            )
            max_temp_label.pack()

            # Min teplota
            min_temp_label = tk.Label(
                day_frame,
                text="--°",
                font=('Arial', 8),
                fg='#4dabf7',
                bg='#1a1a1a'
            )
            min_temp_label.pack()

            # Rain
            rain_label = tk.Label(
                day_frame,
                text="💧 --%",
                font=('Arial', 7),
                fg='cyan',
                bg='#1a1a1a'
            )
            rain_label.pack(pady=1)

            self.forecast_labels.append({
                'day': day_label,
                'icon': icon_label,
                'max_temp': max_temp_label,
                'min_temp': min_temp_label,
                'rain': rain_label
            })

        # Nakonfiguruj grid
        for i in range(5):
            self.forecast_frame.grid_columnconfigure(i, weight=1)

        # Aktualizuj čas
        self.update_current_time()

    def create_pages(self):
        # Stránka 1: Aktuálne počasie + 5-dňová predpoveď
        page1 = tk.Frame(self.main_container, bg='black')
        self.create_combined_weather_page(page1)
        self.pages.append(page1)

        # Stránka 2: Grafy
        page2 = tk.Frame(self.main_container, bg='black')
        self.create_graphs_page(page2)
        self.pages.append(page2)

    def create_current_weather_page(self, parent):
        # Hlavička
        header = tk.Frame(parent, bg='black')
        header.pack(fill=tk.X, pady=3)

        self.city_label = tk.Label(
            header,
            text="Loading...",
            font=('Arial', 13, 'bold'),
            fg='white',
            bg='black'
        )
        self.city_label.pack()

        self.current_date_label = tk.Label(
            header,
            text="",
            font=('Arial', 9),
            fg='lightgray',
            bg='black'
        )
        self.current_date_label.pack()

        # Hlavná teplota a ikona
        main_frame = tk.Frame(parent, bg='black')
        main_frame.pack(expand=True)

        self.weather_icon_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 50),
            fg='white',
            bg='black'
        )
        self.weather_icon_label.pack()

        self.current_temp_label = tk.Label(
            main_frame,
            text="--°",
            font=('Arial', 56, 'bold'),
            fg='white',
            bg='black'
        )
        self.current_temp_label.pack()

        self.current_desc_label = tk.Label(
            main_frame,
            text="Loading...",
            font=('Arial', 12),
            fg='lightgray',
            bg='black'
        )
        self.current_desc_label.pack()

        # Detaily - 2 riadky
        details_frame = tk.Frame(parent, bg='black')
        details_frame.pack(fill=tk.X, pady=5)

        row1 = tk.Frame(details_frame, bg='black')
        row1.pack()

        self.current_humidity_label = tk.Label(
            row1,
            text="💧 --%",
            font=('Arial', 9),
            fg='cyan',
            bg='black'
        )
        self.current_humidity_label.pack(side=tk.LEFT, padx=12)

        self.current_wind_label = tk.Label(
            row1,
            text="💨 -- km/h",
            font=('Arial', 9),
            fg='lightblue',
            bg='black'
        )
        self.current_wind_label.pack(side=tk.LEFT, padx=12)

        row2 = tk.Frame(details_frame, bg='black')
        row2.pack()

        self.current_pressure_label = tk.Label(
            row2,
            text="🌡 -- hPa",
            font=('Arial', 9),
            fg='yellow',
            bg='black'
        )
        self.current_pressure_label.pack(side=tk.LEFT, padx=12)

        self.current_feels_label = tk.Label(
            row2,
            text="Feels: --°C",
            font=('Arial', 9),
            fg='orange',
            bg='black'
        )
        self.current_feels_label.pack(side=tk.LEFT, padx=12)

        # Aktualizuj čas
        self.update_current_time()

    def create_forecast_page(self, parent):
        # Nadpis
        title = tk.Label(
            parent,
            text="5-Day Forecast",
            font=('Arial', 13, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=5)

        # Frame pre predpoveď
        self.forecast_frame = tk.Frame(parent, bg='black')
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Vytvor 5 stĺpcov pre dni
        self.forecast_labels = []
        for i in range(5):
            day_frame = tk.Frame(self.forecast_frame,
                                 bg='#1a1a1a', relief=tk.RAISED, borderwidth=1)
            day_frame.grid(row=0, column=i, padx=2, pady=5, sticky='nsew')

            # Deň
            day_label = tk.Label(
                day_frame,
                text="---",
                font=('Arial', 9, 'bold'),
                fg='white',
                bg='#1a1a1a'
            )
            day_label.pack(pady=2)

            # Ikona
            icon_label = tk.Label(
                day_frame,
                text="",
                font=('Arial', 28),
                fg='white',
                bg='#1a1a1a'
            )
            icon_label.pack(pady=2)

            # Max teplota
            max_temp_label = tk.Label(
                day_frame,
                text="--°",
                font=('Arial', 11, 'bold'),
                fg='#ff6b6b',
                bg='#1a1a1a'
            )
            max_temp_label.pack()

            # Min teplota
            min_temp_label = tk.Label(
                day_frame,
                text="--°",
                font=('Arial', 9),
                fg='#4dabf7',
                bg='#1a1a1a'
            )
            min_temp_label.pack()

            # Rain
            rain_label = tk.Label(
                day_frame,
                text="💧 --%",
                font=('Arial', 8),
                fg='cyan',
                bg='#1a1a1a'
            )
            rain_label.pack(pady=2)

            self.forecast_labels.append({
                'day': day_label,
                'icon': icon_label,
                'max_temp': max_temp_label,
                'min_temp': min_temp_label,
                'rain': rain_label
            })

        # Nakonfiguruj grid
        for i in range(5):
            self.forecast_frame.grid_columnconfigure(i, weight=1)

    def create_graphs_page(self, parent):
        # Nadpis
        title = tk.Label(
            parent,
            text="24h Trends",
            font=('Arial', 13, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=3)

        # Canvas pre graf teploty
        temp_frame = tk.Frame(parent, bg='black')
        temp_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=3)

        temp_title = tk.Label(
            temp_frame,
            text="Temperature",
            font=('Arial', 10, 'bold'),
            fg='#ff6b6b',
            bg='black'
        )
        temp_title.pack()

        self.temp_canvas = tk.Canvas(
            temp_frame,
            bg='#1a1a1a',
            highlightthickness=0,
            height=100
        )
        self.temp_canvas.pack(fill=tk.BOTH, expand=True)

        # Canvas pre graf vlhkosti
        humidity_frame = tk.Frame(parent, bg='black')
        humidity_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=3)

        humidity_title = tk.Label(
            humidity_frame,
            text="Humidity",
            font=('Arial', 10, 'bold'),
            fg='cyan',
            bg='black'
        )
        humidity_title.pack()

        self.humidity_canvas = tk.Canvas(
            humidity_frame,
            bg='#1a1a1a',
            highlightthickness=0,
            height=100
        )
        self.humidity_canvas.pack(fill=tk.BOTH, expand=True)

    def create_navigation(self):
        nav_frame = tk.Frame(self.root, bg='#1a1a1a', height=30)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X)
        nav_frame.pack_propagate(False)

        # Ľavá šípka
        left_btn = tk.Button(
            nav_frame,
            text="◀",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='white',
            activebackground='#3a3a3a',
            activeforeground='white',
            relief=tk.FLAT,
            command=self.manual_prev_page,
            width=3
        )
        left_btn.pack(side=tk.LEFT, padx=5, pady=3)

        # Tlačidlo pre search (🔍)
        search_btn = tk.Button(
            nav_frame,
            text="🔍",
            font=('Arial', 12),
            bg='#2a2a2a',
            fg='white',
            activebackground='#3a3a3a',
            activeforeground='white',
            relief=tk.FLAT,
            command=self.manual_location_search,
            width=3
        )
        search_btn.pack(side=tk.LEFT, padx=2, pady=3)

        # Indikátory stránok (v strede)
        self.page_indicators = []
        indicator_frame = tk.Frame(nav_frame, bg='#1a1a1a')
        indicator_frame.pack(side=tk.LEFT, expand=True)

        for i in range(len(self.pages)):
            dot = tk.Label(
                indicator_frame,
                text="●",
                font=('Arial', 10),
                fg='gray',
                bg='#1a1a1a'
            )
            dot.pack(side=tk.LEFT, padx=4)
            self.page_indicators.append(dot)

        # Pravá šípka
        right_btn = tk.Button(
            nav_frame,
            text="▶",
            font=('Arial', 14, 'bold'),
            bg='#2a2a2a',
            fg='white',
            activebackground='#3a3a3a',
            activeforeground='white',
            relief=tk.FLAT,
            command=self.manual_next_page,
            width=3
        )
        right_btn.pack(side=tk.RIGHT, padx=5, pady=3)

    def manual_prev_page(self):
        """Manuálne prepnutie na predchádzajúcu stránku"""
        self.stop_auto_rotate()
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
        else:
            self.show_page(len(self.pages) - 1)
        self.start_auto_rotate()

    def manual_next_page(self):
        """Manuálne prepnutie na ďalšiu stránku"""
        self.stop_auto_rotate()
        next_page = (self.current_page + 1) % len(self.pages)
        self.show_page(next_page)
        self.start_auto_rotate()

    def show_page(self, page_num):
        # Skry všetky stránky
        for page in self.pages:
            page.pack_forget()

        # Zobraz vybranú stránku
        self.current_page = page_num
        self.pages[page_num].pack(fill=tk.BOTH, expand=True)

        # Aktualizuj indikátory
        for i, dot in enumerate(self.page_indicators):
            if i == page_num:
                dot.config(fg='white')
            else:
                dot.config(fg='gray')

    def update_current_time(self):
        now = datetime.now()
        date_str = now.strftime("%A, %b %d")
        time_str = now.strftime("%H:%M:%S")
        self.current_date_label.config(text=f"{date_str}  {time_str}")
        self.root.after(1000, self.update_current_time)

    def get_weather_icon(self, weather_code):
        """Vráti textovú ikonu podľa WMO weather code"""
        icons = {
            0: "☀",   # Clear sky (slnko)
            1: "🌤",   # Mainly clear
            2: "⛅",   # Partly cloudy
            3: "☁",   # Overcast (oblačno)
            45: "≡",  # Foggy (hmla)
            48: "≡",  # Rime fog
            51: "∴",  # Light drizzle (mrholenie)
            53: "∴",  # Moderate drizzle
            55: ":::",  # Dense drizzle
            61: "🌧",   # Slight rain (dážď)
            63: "🌧",   # Moderate rain
            65: "🌧",   # Heavy rain
            71: "❄",   # Slight snow (sneh)
            73: "❄",   # Moderate snow
            75: "❄❄",  # Heavy snow
            77: "❄",   # Snow grains
            80: "∴",  # Slight rain showers
            81: ":::",  # Moderate rain showers
            82: "⚡",  # Violent rain showers
            85: "❄",   # Slight snow showers
            86: "❄❄",  # Heavy snow showers
            95: "⚡",  # Thunderstorm (búrka)
            96: "⚡❄",  # Thunderstorm with hail
            99: "⚡⚡"   # Severe thunderstorm
        }
        return icons.get(weather_code, "?")

    def get_weather_description(self, weather_code):
        """Prevedie WMO weather code na popis"""
        descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
            80: "Rain showers", 81: "Moderate showers", 82: "Heavy showers",
            85: "Snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Severe thunderstorm"
        }
        return descriptions.get(weather_code, "Unknown")

    def get_weather(self):
        if self.LATITUDE is None or self.LONGITUDE is None:
            return None

        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': self.LATITUDE,
                'longitude': self.LONGITUDE,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m',
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max',
                'timezone': 'auto',
                'forecast_days': 7
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if response.status_code == 200:
                return data
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None

    def update_weather(self):
        data = self.get_weather()

        if data:
            self.weather_data = data
            self.update_current_weather(data)
            self.update_forecast(data)
            self.update_graphs(data)

        # Aktualizuj každých 10 minút
        self.root.after(600000, self.update_weather)

    def update_current_weather(self, data):
        current = data['current']

        temp = round(current['temperature_2m'])
        feels_like = round(current['apparent_temperature'])
        humidity = current['relative_humidity_2m']
        pressure = round(current['surface_pressure'])
        wind = round(current['wind_speed_10m'], 1)
        weather_code = current['weather_code']

        self.current_temp_label.config(text=f"{temp}°C")
        self.weather_icon_label.config(
            text=self.get_weather_icon(weather_code))
        self.current_desc_label.config(
            text=self.get_weather_description(weather_code))
        self.current_humidity_label.config(text=f"💧 {humidity}%")
        self.current_wind_label.config(text=f"💨 {wind} km/h")
        self.current_pressure_label.config(text=f"🌡 {pressure} hPa")
        self.current_feels_label.config(text=f"Feels: {feels_like}°C")

    def update_forecast(self, data):
        daily = data['daily']

        for i in range(5):
            if i < len(daily['time']):
                date = datetime.fromisoformat(daily['time'][i])
                day_name = date.strftime("%a")

                weather_code = daily['weather_code'][i]
                max_temp = round(daily['temperature_2m_max'][i])
                min_temp = round(daily['temperature_2m_min'][i])
                rain_prob = daily['precipitation_probability_max'][i]

                labels = self.forecast_labels[i]
                labels['day'].config(text=day_name)
                labels['icon'].config(text=self.get_weather_icon(weather_code))
                labels['max_temp'].config(text=f"{max_temp}°")
                labels['min_temp'].config(text=f"{min_temp}°")
                labels['rain'].config(text=f"💧 {rain_prob}%")

    def update_graphs(self, data):
        hourly = data['hourly']

        temps = hourly['temperature_2m'][:24]
        humidity = hourly['relative_humidity_2m'][:24]

        self.draw_graph(self.temp_canvas, temps, '#ff6b6b',
                        min(temps) - 2, max(temps) + 2)
        self.draw_graph(self.humidity_canvas, humidity, 'cyan', 0, 100)

    def draw_graph(self, canvas, data, color, min_val, max_val):
        canvas.delete('all')

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1:
            width = 450
        if height <= 1:
            height = 100

        padding = 10
        graph_width = width - 2 * padding
        graph_height = height - 2 * padding

        if len(data) < 2:
            return

        points = []
        for i, value in enumerate(data):
            x = padding + (i / (len(data) - 1)) * graph_width
            normalized = (value - min_val) / (max_val -
                                              min_val) if max_val != min_val else 0.5
            y = height - padding - (normalized * graph_height)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=2, smooth=True)

        canvas.create_text(padding + 5, padding + 5,
                           text=f"{max_val:.0f}", fill=color, font=('Arial', 8), anchor='nw')
        canvas.create_text(padding + 5, height - padding - 5,
                           text=f"{min_val:.0f}", fill=color, font=('Arial', 8), anchor='sw')


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
