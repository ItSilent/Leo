"""
GIF Handler for Action Commands
"""
import requests
import random

async def get_gif(search_term):
    """Fetch a random GIF from multiple sources without requiring API keys"""
    
    try:
        giphy_url = "https://api.giphy.com/v1/gifs/search"
        params = {
            'api_key': 'dc6zaTOxFJmzC',
            'q': f"anime {search_term}",
            'limit': 20,
            'rating': 'g'
        }
        
        response = requests.get(giphy_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                gif = random.choice(data['data'])
                gif_url = gif['images']['original']['url']
                print(f"Using Giphy GIF for: {search_term}")
                return gif_url
    except Exception as e:
        print(f"Giphy API error: {e}")
    
    print(f"Using curated GIF for: {search_term}")
    anime_gifs = {
        'hug': [
            'https://media.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif',
            'https://media.giphy.com/media/lrr9rHuoJOE0w/giphy.gif',
            'https://media.giphy.com/media/ZBQhoZC0nqknSviPqT/giphy.gif'
        ],
        'kiss': [
            'https://media.giphy.com/media/bm2O3nXTcKJeU/giphy.gif',
            'https://media.giphy.com/media/nyNS6Cfrnkdj2/giphy.gif',
            'https://media.giphy.com/media/KH1CTZtw1iP3W/giphy.gif'
        ],
        'slap': [
            'https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif',
            'https://media.giphy.com/media/mEtSQlxVDay1u/giphy.gif',
            'https://media.giphy.com/media/i3RA5wLyWjCRa/giphy.gif'
        ],
        'poke': [
            'https://media.giphy.com/media/k1uYB5LvlBZqU/giphy.gif',
            'https://media.giphy.com/media/XtydbjSSwkC7K/giphy.gif',
            'https://media.giphy.com/media/SqmkZ5IdwzTP2/giphy.gif'
        ],
        'pat head': [
            'https://media.giphy.com/media/KZQlfylo73AMU/giphy.gif',
            'https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif',
            'https://media.giphy.com/media/L2qukNXGjccyuAYd3W/giphy.gif'
        ],
        'cuddle': [
            'https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif',
            'https://media.giphy.com/media/3o6nUXaNE5377A7HXi/giphy.gif',
            'https://media.giphy.com/media/PQKlfexeEpnTq/giphy.gif'
        ],
        'dance': [
            'https://media.giphy.com/media/MEjjxknS7VtjZyvFqc/giphy.gif',
            'https://media.giphy.com/media/H4uE6w9G1uK4M/giphy.gif',
            'https://media.giphy.com/media/ZXGNKclZthsZ2/giphy.gif'
        ],
        'wave hello': [
            'https://media.giphy.com/media/MUeQeEQaDCjE4/giphy.gif',
            'https://media.giphy.com/media/P7JmDW7IkB7TW/giphy.gif',
            'https://media.giphy.com/media/w0vFxYaCcvvJm/giphy.gif'
        ]
    }
    
    gif_list = anime_gifs.get(search_term, anime_gifs['hug'])
    return random.choice(gif_list)