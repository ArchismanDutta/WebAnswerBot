from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import os
from openai import OpenAI
from scraper import scrape_website

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

app = FastAPI()

# ✅ Allow your frontend domain hosted on Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web-answer-bot-ge24.vercel.app",  # ⬅️ change this to match your frontend URL
        "http://localhost:3000"  # optional for local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    url: HttpUrl
    question: str

@app.post("/ask")
async def ask_question(data: RequestData):
    content = scrape_website(data.url)

    if content.startswith("Error"):
        raise HTTPException(status_code=400, detail=content)

    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on website content.",
            },
            {
                "role": "user",
                "content": f"Content from the website:\n{content}\n\nQuestion: {data.question}",
            },
        ]

        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b",
            messages=messages,
            temperature=0.5,
        )

        return {"answer": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get response from OpenRouter: {str(e)}")
