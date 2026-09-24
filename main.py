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

# List of models to try in sequence if one is unavailable or rate-limited
MODEL_FALLBACKS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-flash-latest",
]


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

    prompt = (
        f"You are a real-time web search assistant. Answer the user query clearly and comprehensively.\n\n"
        f"User Query: '{query}'\n\n"
        "Format the response into 3 clear sections:\n"
        "1. 💡 Direct Answer\n"
        "2. 📌 Key Details & Concepts\n"
        "3. 🔍 Related Topics & Ideas to Explore"
    )

    last_exception = None

    # Try each model in sequence
    for model_name in MODEL_FALLBACKS:
        try:
            response = ai_client.models.generate_content(
                model=model_name, contents=prompt
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
            print(f"Model {model_name} failed: {str(e)}. Retrying next fallback...")
            last_exception = e

    # If all models fail, raise error details
    error_details = traceback.format_exc()
    print(f"ALL MODELS FAILED: {error_details}")
    raise HTTPException(
        status_code=500, detail=f"Search Error: {str(last_exception)}"
    )