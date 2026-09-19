import requests
import random
from app.config import Config

def get_weather(location):
    """Fetch weather data for a given location"""
    if not Config.WEATHER_API_KEY:
        return {"error": "Weather API key not configured"}
    
    params = {
        'q': location,
        'appid': Config.WEATHER_API_KEY,
        'units': 'metric'  # Celsius
    }
    
    try:
        response = requests.get(Config.WEATHER_API_URL, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'location': data['name'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'country': data['sys']['country']
            }
        else:
            return {'error': data.get('message', 'Location not found')}
    except Exception as e:
        return {'error': str(e)}

def get_random_quote():
    """Return a random quote"""
    quotes = [
        {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"quote": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
        {"quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
        {"quote": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
        {"quote": "Life is what happens to you while you're busy making other plans.", "author": "John Lennon"},
        {"quote": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
        {"quote": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
        {"quote": "The secret of getting ahead is getting started.", "author": "Mark Twain"}
    ]
    return random.choice(quotes)
