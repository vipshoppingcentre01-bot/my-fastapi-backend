import os
from duckduckgo_search import DDGS
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI(title="Master AI Controller Hub")

# Enable CORS so your web frontends can call this API directly
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
def search_engine(query: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API key."
        )

    try:
        # Step 1: Get raw web search results
        ddg = DDGS()
        raw_results = list(ddg.text(query, max_results=5))

        # Step 2: Pass search results to Gemini AI to synthesize a smart summary
        prompt = (
            f"User asked: '{query}'\n\n"
            f"Here are top web search results:\n{raw_results}\n\n"
            "Provide a concise, direct, and well-structured answer based on these web results. "
            "Include key takeaways and cite relevant URLs if useful."
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