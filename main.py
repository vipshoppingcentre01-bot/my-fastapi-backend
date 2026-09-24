import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

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
        if mode == "quick":
            # Quick mode: standard fast response without live search
            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Provide a quick, concise direct answer for: {query}",
            )
            return {
                "query": query,
                "ai_summary": response.text,
                "web_sources": [],
            }

        # Deep mode: Uses native Google Search grounding
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                f"Perform a live search and answer this query: '{query}'. "
                "Format the response into 3 sections:\n"
                "1. 💡 Direct Answer\n"
                "2. 📌 Key Takeaways\n"
                "3. 🔍 Related Insights"
            ),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )

        # Extract source URLs from grounding metadata if available
        sources = []
        try:
            grounding_chunks = (
                response.candidates[0]
                .grounding_metadata.grounding_chunks
            )
            if grounding_chunks:
                for chunk in grounding_chunks:
                    if chunk.web:
                        sources.append({
                            "title": chunk.web.title or chunk.web.uri,
                            "href": chunk.web.uri,
                            "body": "Google Search Source",
                        })
        except Exception:
            sources = []

        return {
            "query": query,
            "ai_summary": response.text,
            "web_sources": sources,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")