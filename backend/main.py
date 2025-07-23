from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from scraper import scrape_website  # Make sure this file exists

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

# ✅ Update with your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-answer-bot-ge24.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        data = response.json()
        return {"answer": data["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": "Failed to get answer", "details": str(e)}
