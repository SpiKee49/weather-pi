#!/usr/bin/env python3
import tkinter as tk
from tkinter import font
import requests
from datetime import datetime
import json

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Display")
        
        # Fullscreen na LCD (480x320)
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.geometry('480x320')
        
        # Súradnice pre Humenné, SK
        self.LATITUDE = 48.9333
        self.LONGITUDE = 21.9000
        
        # Vytvor GUI
        self.create_widgets()
        
        # Aktualizuj počasie
        self.update_weather()
        
        # ESC pre ukončenie (pre testovanie)
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def create_widgets(self):
        # Hlavný kontajner
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mesto
        self.city_label = tk.Label(
            main_frame,
            text="Humenné, SK",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='black'
        )
        self.city_label.pack(pady=5)
        
        # Dátum a čas
        self.date_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 12),
            fg='white',
            bg='black'
        )
        self.date_label.pack(pady=5)
        
        # Teplota (veľké číslo)
        self.temp_label = tk.Label(
            main_frame,
            text="--°",
            font=('Arial', 72, 'bold'),
            fg='white',
            bg='black'
        )
        self.temp_label.pack(pady=10)
        
        # Popis počasia
        self.desc_label = tk.Label(
            main_frame,
            text="Loading...",
            font=('Arial', 14),
            fg='white',
            bg='black'
        )
        self.desc_label.pack()
        
        # Spodný frame pre detaily
        details_frame = tk.Frame(main_frame, bg='black')
        details_frame.pack(pady=15)
        
        # Vlhkosť
        self.humidity_label = tk.Label(
            details_frame,
            text="💧 --",
            font=('Arial', 11),
            fg='cyan',
            bg='black'
        )
        self.humidity_label.grid(row=0, column=0, padx=15)
        
        # Vietor
        self.wind_label = tk.Label(
            details_frame,
            text="💨 --",
            font=('Arial', 11),
            fg='lightblue',
            bg='black'
        )
        self.wind_label.grid(row=0, column=1, padx=15)
        
        # Tlak
        self.pressure_label = tk.Label(
            details_frame,
            text="🌡 --",
            font=('Arial', 11),
            fg='yellow',
            bg='black'
        )
        self.pressure_label.grid(row=1, column=0, padx=15, pady=5)
        
        # Pocitová teplota
        self.feels_label = tk.Label(
            details_frame,
            text="Feels: --",
            font=('Arial', 11),
            fg='orange',
            bg='black'
        )
        self.feels_label.grid(row=1, column=1, padx=15, pady=5)
        
        # Aktualizuj čas každú sekundu
        self.update_time()
    
    def update_time(self):
        now = datetime.now()
        date_str = now.strftime("%A, %B %d")
        time_str = now.strftime("%H:%M:%S")
        self.date_label.config(text=f"{date_str}  {time_str}")
        self.root.after(1000, self.update_time)
    
    def get_weather_description(self, weather_code):
        """Prevedie WMO weather code na popis"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
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
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, "Unknown")
    
    def get_weather(self):
        try:
            # Open-Meteo API - úplne zadarmo, bez kľúča
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': self.LATITUDE,
                'longitude': self.LONGITUDE,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m',
                'timezone': 'Europe/Bratislava'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                current = data['current']
                return {
                    'temp': round(current['temperature_2m']),
                    'feels_like': round(current['apparent_temperature']),
                    'humidity': current['relative_humidity_2m'],
                    'pressure': round(current['surface_pressure']),
                    'wind': round(current['wind_speed_10m'], 1),
                    'description': self.get_weather_description(current['weather_code']),
                    'precipitation': current['precipitation']
                }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def update_weather(self):
        weather = self.get_weather()
        
        if weather:
            self.temp_label.config(text=f"{weather['temp']}°C")
            self.desc_label.config(text=weather['description'])
            self.humidity_label.config(text=f"💧 {weather['humidity']}%")
            self.wind_label.config(text=f"💨 {weather['wind']} km/h")
            self.pressure_label.config(text=f"🌡 {weather['pressure']} hPa")
            self.feels_label.config(text=f"Feels: {weather['feels_like']}°C")
        else:
            self.desc_label.config(text="No connection")
        
        # Aktualizuj každých 10 minút
        self.root.after(600000, self.update_weather)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
