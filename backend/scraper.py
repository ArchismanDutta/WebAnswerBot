import requests
from bs4 import BeautifulSoup

def scrape_website(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")
        return text[:6000]  # Limit to 6000 characters for LLM
    except Exception as e:
        return f"Error scraping website: {e}"
