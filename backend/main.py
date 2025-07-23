from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from scraper import scrape_website

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# CORS setup to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-answer-bot-ge24.vercel.app"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class AskRequest(BaseModel):
    url: HttpUrl
    question: str

# POST endpoint to handle user questions
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

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to get response from OpenRouter", "status_code": response.status_code, "details": response.text}

    try:
        res_json = response.json()
        return {"answer": res_json["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": "Failed to parse OpenRouter response", "details": str(e)}
