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

        # Súradnice - budú sa automaticky zistiť
        self.LATITUDE = None
        self.LONGITUDE = None
        self.CITY = "Loading..."

        # Aktuálna stránka
        self.current_page = 0
        self.pages = []

        # Hlavný container
        self.main_container = tk.Frame(self.root, bg='black')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Vytvor stránky
        self.create_pages()

        # Načítaj počasie
        self.weather_data = None
        self.forecast_data = None

        # Najprv získaj polohu, potom počasie
        self.get_location()

        # Navigačné tlačidlá
        self.create_navigation()

        # Touch/Click eventy pre swipe
        self.start_x = 0
        self.root.bind('<Button-1>', self.on_touch_start)
        self.root.bind('<B1-Motion>', self.on_touch_move)

        # ESC pre ukončenie
        self.root.bind('<Escape>', lambda e: self.root.quit())

        # Zobraz prvú stránku
        self.show_page(0)

    def get_location(self):
        """Automaticky zisti polohu pomocou IP geolokácie"""
        try:
            # Použijeme ip-api.com - zadarmo, bez API kľúča
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
                # Fallback na Humenné
                self.use_fallback_location()
        except Exception as e:
            print(f"Error getting location: {e}")
            # Fallback na Humenné
            self.use_fallback_location()

    def use_fallback_location(self):
        """Použije predvolenú polohu ak zlyhá automatická detekcia"""
        self.LATITUDE = 48.9333
        self.LONGITUDE = 21.9000
        self.CITY = "Humenné, SK"
        print(f"Using fallback location: {self.CITY}")
        self.city_label.config(text=self.CITY)
        self.update_weather()

    def create_pages(self):
        # Stránka 1: Aktuálne počasie
        page1 = tk.Frame(self.main_container, bg='black')
        self.create_current_weather_page(page1)
        self.pages.append(page1)

        # Stránka 2: 5-dňová predpoveď
        page2 = tk.Frame(self.main_container, bg='black')
        self.create_forecast_page(page2)
        self.pages.append(page2)

        # Stránka 3: Grafy
        page3 = tk.Frame(self.main_container, bg='black')
        self.create_graphs_page(page3)
        self.pages.append(page3)

    def create_current_weather_page(self, parent):
        # Hlavička
        header = tk.Frame(parent, bg='black')
        header.pack(fill=tk.X, pady=5)

        self.city_label = tk.Label(
            header,
            text="Loading location...",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='black'
        )
        self.city_label.pack()

        self.current_date_label = tk.Label(
            header,
            text="",
            font=('Arial', 11),
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
            font=('Arial', 60),
            fg='white',
            bg='black'
        )
        self.weather_icon_label.pack()

        self.current_temp_label = tk.Label(
            main_frame,
            text="--°",
            font=('Arial', 72, 'bold'),
            fg='white',
            bg='black'
        )
        self.current_temp_label.pack()

        self.current_desc_label = tk.Label(
            main_frame,
            text="Loading...",
            font=('Arial', 14),
            fg='lightgray',
            bg='black'
        )
        self.current_desc_label.pack()

        # Detaily
        details_frame = tk.Frame(parent, bg='black')
        details_frame.pack(fill=tk.X, pady=10)

        details_grid = tk.Frame(details_frame, bg='black')
        details_grid.pack()

        self.current_humidity_label = tk.Label(
            details_grid,
            text="💧 --%",
            font=('Arial', 10),
            fg='cyan',
            bg='black'
        )
        self.current_humidity_label.grid(row=0, column=0, padx=10)

        self.current_wind_label = tk.Label(
            details_grid,
            text="💨 -- km/h",
            font=('Arial', 10),
            fg='lightblue',
            bg='black'
        )
        self.current_wind_label.grid(row=0, column=1, padx=10)

        self.current_pressure_label = tk.Label(
            details_grid,
            text="🌡 -- hPa",
            font=('Arial', 10),
            fg='yellow',
            bg='black'
        )
        self.current_pressure_label.grid(row=1, column=0, padx=10, pady=5)

        self.current_feels_label = tk.Label(
            details_grid,
            text="Feels: --°C",
            font=('Arial', 10),
            fg='orange',
            bg='black'
        )
        self.current_feels_label.grid(row=1, column=1, padx=10, pady=5)

        # Aktualizuj čas
        self.update_current_time()

    def create_forecast_page(self, parent):
        # Nadpis
        title = tk.Label(
            parent,
            text="5-Day Forecast",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=10)

        # Frame pre predpoveď
        self.forecast_frame = tk.Frame(parent, bg='black')
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Vytvor 5 stĺpcov pre dni
        self.forecast_labels = []
        for i in range(5):
            day_frame = tk.Frame(self.forecast_frame,
                                 bg='#1a1a1a', relief=tk.RAISED, borderwidth=1)
            day_frame.grid(row=0, column=i, padx=3, pady=5, sticky='nsew')

            # Deň
            day_label = tk.Label(
                day_frame,
                text="---",
                font=('Arial', 10, 'bold'),
                fg='white',
                bg='#1a1a1a'
            )
            day_label.pack(pady=3)

            # Ikona
            icon_label = tk.Label(
                day_frame,
                text="",
                font=('Arial', 30),
                fg='white',
                bg='#1a1a1a'
            )
            icon_label.pack()

            # Max teplota
            max_temp_label = tk.Label(
                day_frame,
                text="--°",
                font=('Arial', 12, 'bold'),
                fg='#ff6b6b',
                bg='#1a1a1a'
            )
            max_temp_label.pack()

            # Min teplota
            min_temp_label = tk.Label(
                day_frame,
                text="--°",
                font=('Arial', 10),
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
            text="Temperature & Humidity Trends",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=5)

        # Canvas pre graf teploty
        temp_frame = tk.Frame(parent, bg='black')
        temp_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        temp_title = tk.Label(
            temp_frame,
            text="Temperature (24h)",
            font=('Arial', 11, 'bold'),
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
        humidity_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        humidity_title = tk.Label(
            humidity_frame,
            text="Humidity (24h)",
            font=('Arial', 11, 'bold'),
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

        # Indikátory stránok
        self.page_indicators = []
        indicator_frame = tk.Frame(nav_frame, bg='#1a1a1a')
        indicator_frame.pack(expand=True)

        for i in range(len(self.pages)):
            dot = tk.Label(
                indicator_frame,
                text="●",
                font=('Arial', 12),
                fg='gray',
                bg='#1a1a1a'
            )
            dot.pack(side=tk.LEFT, padx=5)
            self.page_indicators.append(dot)

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

    def on_touch_start(self, event):
        self.start_x = event.x

    def on_touch_move(self, event):
        delta = event.x - self.start_x

        # Swipe vpravo (predchádzajúca stránka)
        if delta > 100:
            if self.current_page > 0:
                self.show_page(self.current_page - 1)
            self.start_x = event.x

        # Swipe vľavo (ďalšia stránka)
        elif delta < -100:
            if self.current_page < len(self.pages) - 1:
                self.show_page(self.current_page + 1)
            self.start_x = event.x

    def update_current_time(self):
        now = datetime.now()
        date_str = now.strftime("%A, %B %d")
        time_str = now.strftime("%H:%M:%S")
        self.current_date_label.config(text=f"{date_str}  {time_str}")
        self.root.after(1000, self.update_current_time)

    def get_weather_icon(self, weather_code):
        """Vráti emoji ikonu podľa WMO weather code"""
        icons = {
            0: "☀️",   # Clear sky
            1: "🌤️",   # Mainly clear
            2: "⛅",   # Partly cloudy
            3: "☁️",   # Overcast
            45: "🌫️",  # Foggy
            48: "🌫️",  # Rime fog
            51: "🌦️",  # Light drizzle
            53: "🌦️",  # Moderate drizzle
            55: "🌧️",  # Dense drizzle
            61: "🌧️",  # Slight rain
            63: "🌧️",  # Moderate rain
            65: "🌧️",  # Heavy rain
            71: "🌨️",  # Slight snow
            73: "🌨️",  # Moderate snow
            75: "❄️",   # Heavy snow
            77: "🌨️",  # Snow grains
            80: "🌦️",  # Slight rain showers
            81: "🌧️",  # Moderate rain showers
            82: "⛈️",   # Violent rain showers
            85: "🌨️",  # Slight snow showers
            86: "❄️",   # Heavy snow showers
            95: "⛈️",   # Thunderstorm
            96: "⛈️",   # Thunderstorm with hail
            99: "⛈️"    # Severe thunderstorm
        }
        return icons.get(weather_code, "🌡️")

    def get_weather_description(self, weather_code):
        """Prevedie WMO weather code na popis"""
        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Rain showers",
            81: "Moderate showers",
            82: "Heavy showers",
            85: "Snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm + hail",
            99: "Severe thunderstorm"
        }
        return descriptions.get(weather_code, "Unknown")

    def get_weather(self):
        # Ak ešte nemáme súradnice, počkaj
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

        # Zobraz len posledných 24 hodín
        temps = hourly['temperature_2m'][:24]
        humidity = hourly['relative_humidity_2m'][:24]

        # Graf teploty
        self.draw_graph(
            self.temp_canvas,
            temps,
            '#ff6b6b',
            min(temps) - 2,
            max(temps) + 2
        )

        # Graf vlhkosti
        self.draw_graph(
            self.humidity_canvas,
            humidity,
            'cyan',
            0,
            100
        )

    def draw_graph(self, canvas, data, color, min_val, max_val):
        canvas.delete('all')

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1:
            width = 440
        if height <= 1:
            height = 100

        padding = 10
        graph_width = width - 2 * padding
        graph_height = height - 2 * padding

        if len(data) < 2:
            return

        # Vypočítaj body
        points = []
        for i, value in enumerate(data):
            x = padding + (i / (len(data) - 1)) * graph_width
            normalized = (value - min_val) / (max_val -
                                              min_val) if max_val != min_val else 0.5
            y = height - padding - (normalized * graph_height)
            points.extend([x, y])

        # Nakresli čiaru
        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=2, smooth=True)

        # Pridaj min/max hodnoty
        canvas.create_text(
            padding + 5,
            padding + 5,
            text=f"{max_val:.0f}",
            fill=color,
            font=('Arial', 8),
            anchor='nw'
        )

        canvas.create_text(
            padding + 5,
            height - padding - 5,
            text=f"{min_val:.0f}",
            fill=color,
            font=('Arial', 8),
            anchor='sw'
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
