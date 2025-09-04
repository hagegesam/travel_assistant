#!/usr/bin/env python3
"""
Test script for external APIs used by the Travel Assistant
"""

from app.external_api import geocode_city, fetch_weather_summary, country_info_by_name
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def test_geocoding():
    """Test geocoding API with various cities"""
    console.print(Panel("🌍 Testing Geocoding API", style="blue"))
    
    cities = ["Paris", "Tokyo", "New York", "Invalid City Name"]
    table = Table(title="Geocoding Results")
    table.add_column("City", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Result", style="white")
    
    for city in cities:
        try:
            result = geocode_city(city)
            if result:
                table.add_row(
                    city, 
                    "✅ Success", 
                    f"Lat: {result['lat']}, Lon: {result['lon']}, Country: {result['country']}"
                )
            else:
                table.add_row(city, "❌ Not Found", "No results")
        except Exception as e:
            table.add_row(city, "🚨 Error", str(e)[:50])
    
    console.print(table)
    console.print()

def test_weather():
    """Test weather API with known coordinates"""
    console.print(Panel("☀️ Testing Weather API", style="yellow"))
    
    locations = [
        ("Paris", 48.8566, 2.3522),
        ("Tokyo", 35.6762, 139.6503),
        ("New York", 40.7128, -74.0060)
    ]
    
    table = Table(title="Weather Forecast Results")
    table.add_column("Location", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Forecast Sample", style="white")
    
    for name, lat, lon in locations:
        try:
            result = fetch_weather_summary(lat, lon)
            if result and result.get('days'):
                first_day = result['days'][0]
                sample = f"T: {first_day['t_min']}-{first_day['t_max']}°C, Rain: {first_day['precip_prob']}%"
                table.add_row(name, "✅ Success", sample)
            else:
                table.add_row(name, "❌ No Data", "No forecast available")
        except Exception as e:
            table.add_row(name, "🚨 Error", str(e)[:50])
    
    console.print(table)
    console.print()

def test_country_info():
    """Test country info API"""
    console.print(Panel("🏛️ Testing Country Info API", style="green"))
    
    countries = ["France", "Japan", "USA", "United States", "Invalid Country"]
    table = Table(title="Country Information Results")
    table.add_column("Country", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Info", style="white")
    
    for country in countries:
        try:
            result = country_info_by_name(country)
            if result:
                info = f"Capital: {result['capital']}, Currency: {', '.join(result['currencies'])}"
                table.add_row(country, "✅ Success", info)
            else:
                table.add_row(country, "❌ Not Found", "No information available")
        except Exception as e:
            table.add_row(country, "🚨 Error", str(e)[:50])
    
    console.print(table)
    console.print()

def main():
    console.print(Panel.fit(
        "🧪 External API Test Suite\n" +
        "Testing Open-Meteo (Weather) and REST Countries APIs",
        style="bold blue"
    ))
    console.print()
    
    test_geocoding()
    test_weather() 
    test_country_info()
    
    console.print(Panel(
        "✅ API testing complete! All working APIs will be used by the travel assistant.",
        style="bold green"
    ))

if __name__ == "__main__":
    main()