from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from scraper import scrape_website  # Make sure this file exists and works

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# FastAPI app
app = FastAPI()

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-answer-bot-ge24.vercel.app"],  # Your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class AskRequest(BaseModel):
    url: HttpUrl
    question: str

# Endpoint
@app.post("/ask")
async def ask_question(data: AskRequest):
    scraped_text = scrape_website(str(data.url))

    if not scraped_text:
        return {"error": "Failed to scrape content from the website."}

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
        data = response.json()
        return {"answer": data["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": "Failed to get response from OpenRouter", "details": str(e)}
