import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.stripped_strings
        return " ".join(list(texts)[:1000])  # Limit for performance
    except Exception as e:
        return ""
