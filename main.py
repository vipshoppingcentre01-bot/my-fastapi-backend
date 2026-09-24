import os
import traceback
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI(title="Master AI Controller Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "my_super_secret_app_key_123"
ai_client = genai.Client()


@app.get("/")
def home():
    return {"message": "Master AI Controller Hub is online!"}


@app.get("/search")
def search_engine(
    query: str, mode: str = "ai_overview", x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API key."
        )

    try:
        prompt = (
            f"You are a real-time web search assistant. Answer the user query clearly and comprehensively.\n\n"
            f"User Query: '{query}'\n\n"
            "Format the response into 3 clear sections:\n"
            "1. 💡 Direct Answer\n"
            "2. 📌 Key Details & Concepts\n"
            "3. 🔍 Related Topics & Ideas to Explore"
        )

        # Uses the active model name
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        return {
            "query": query,
            "ai_summary": response.text,
            "web_sources": [
                {
                    "title": f"Google Search Results for '{query}'",
                    "href": f"https://www.google.com/search?q={query}",
                    "body": "Direct link to full web results.",
                }
            ],
        }

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"ERROR IN /search: {error_details}")
        raise HTTPException(status_code=500, detail=f"Search Error: {str(e)}")