import os
from ddgs import DDGS
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI(title="Master AI Controller Hub")

# Enable CORS so your local HTML frontend can communicate with Render
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
        raw_results = []
        with DDGS() as ddg:
            results = ddg.text(query, max_results=5)
            if results:
                raw_results = list(results)

        if mode == "quick":
            return {
                "query": query,
                "ai_summary": "Quick Web Mode active. Direct web search results retrieved below.",
                "web_sources": raw_results,
            }

        prompt = (
            f"User Query: '{query}'\n\n"
            f"Web Results:\n{raw_results}\n\n"
            "Format the response into 3 clear sections:\n"
            "1. 💡 Direct Answer\n"
            "2. 📌 Key Takeaways\n"
            "3. 🔍 Follow-Up Questions"
        )

        ai_response = ai_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        return {
            "query": query,
            "ai_summary": ai_response.text,
            "web_sources": raw_results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")