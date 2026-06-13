# Advanced Weather Dashboard (integrated version)
# Requires: requests, matplotlib, pillow, geocoder

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geocoder

class AdvancedWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather Dashboard")
        self.root.geometry("1100x750")
        self.root.configure(bg='#2c3e50')

        self.api_key = "6eb2825962f2c09a0bbf61ff6218cdf4"
        self.base_url = "https://api.openweathermap.org/data/2.5/"
        self.temp_unit = "Celsius"

        self.weather_icons = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
            "Drizzle": "🌦️", "Thunderstorm": "⛈️",
            "Snow": "❄️", "Mist": "🌫️", "Fog": "🌫️"
        }

        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#34495e")
        header.pack(fill=tk.X)

        tk.Label(header, text="🌦 Advanced Weather Dashboard",
                 font=("Arial", 22, "bold"),
                 bg="#34495e", fg="white").pack(pady=15)

        search = tk.Frame(self.root, bg="#2c3e50")
        search.pack(fill=tk.X, pady=10)

        self.location_entry = tk.Entry(search, width=30)
        self.location_entry.pack(side=tk.LEFT, padx=10)

        tk.Button(search, text="Search",
                  command=self.get_weather).pack(side=tk.LEFT, padx=5)

        tk.Button(search, text="📍 My Location",
                  command=self.detect_location).pack(side=tk.LEFT, padx=5)

        self.unit_var = tk.StringVar(value="Celsius")
        ttk.Combobox(search, textvariable=self.unit_var,
                     values=["Celsius", "Fahrenheit"],
                     state="readonly", width=12).pack(side=tk.LEFT, padx=10)

        self.result = tk.Label(self.root, bg="#2c3e50",
                               fg="white", justify="left",
                               font=("Arial", 12))
        self.result.pack(pady=10)

        self.chart_frame = tk.Frame(self.root)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        self.status_bar = tk.Label(self.root, text="Ready",
                                   anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def detect_location(self):
        try:
            g = geocoder.ip("me")
            if g.city:
                self.location_entry.delete(0, tk.END)
                self.location_entry.insert(0, g.city)
                self.get_weather()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_weather(self):
        city = self.location_entry.get().strip()
        if not city:
            return

        units = "metric" if self.unit_var.get() == "Celsius" else "imperial"
        symbol = "°C" if units == "metric" else "°F"

        try:
            current = requests.get(
                f"{self.base_url}weather?q={city}&appid={self.api_key}&units={units}"
            ).json()

            if str(current.get("cod")) != "200":
                messagebox.showerror("Error", "City not found")
                return

            sunrise = datetime.fromtimestamp(
                current["sys"]["sunrise"]).strftime("%H:%M")
            sunset = datetime.fromtimestamp(
                current["sys"]["sunset"]).strftime("%H:%M")

            lat = current["coord"]["lat"]
            lon = current["coord"]["lon"]

            aqi_data = requests.get(
                f"{self.base_url}air_pollution?lat={lat}&lon={lon}&appid={self.api_key}"
            ).json()

            aqi = aqi_data["list"][0]["main"]["aqi"]

            text = f"""
Location: {current['name']}, {current['sys']['country']}
Temperature: {current['main']['temp']}{symbol}
Feels Like: {current['main']['feels_like']}{symbol}
Weather: {current['weather'][0]['description']}
Humidity: {current['main']['humidity']}%
Pressure: {current['main']['pressure']} hPa
Wind: {current['wind']['speed']} m/s
Sunrise: {sunrise}
Sunset: {sunset}
AQI: {aqi}
"""
            self.result.config(text=text)

            forecast = requests.get(
                f"{self.base_url}forecast?q={city}&appid={self.api_key}&units=metric"
            ).json()

            self.show_chart(forecast)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_chart(self, data):
        for w in self.chart_frame.winfo_children():
            w.destroy()

        times = [x["dt_txt"][11:16] for x in data["list"][:8]]
        temps = [x["main"]["temp"] for x in data["list"][:8]]

        fig = plt.Figure(figsize=(7, 4))
        ax = fig.add_subplot(111)
        ax.plot(times, temps, marker="o")
        ax.set_title("24 Hour Forecast")

        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def main():
    root = tk.Tk()
    app = AdvancedWeatherApp(root)
    root.after(1500, app.detect_location)
    root.mainloop()

if __name__ == "__main__":
    main()
