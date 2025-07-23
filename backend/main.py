from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_website
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# CORS config (use your actual frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-answer-bot-ge24.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class AskRequest(BaseModel):
    url: HttpUrl
    question: str

@app.post("/ask")
async def ask_question(data: AskRequest):
    scraped_text = scrape_website(str(data.url))

    prompt = f"""
You are an AI assistant. A user has visited this website and wants to know:

Website Content:
{scraped_text}

User Question:
{data.question}

Answer clearly and concisely.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "moonshotai/kimi-k2:free",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {"answer": data["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": "OpenRouter API failed", "details": str(e)}
