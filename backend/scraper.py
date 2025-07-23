import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]  # limit text to 3000 characters
    except Exception as e:
        return f"Error scraping website: {str(e)}"
