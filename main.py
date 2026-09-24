import os
from fastapi import FastAPI, Header, HTTPException
from google import genai

app = FastAPI(title="Master AI Controller Hub")

# Your master security key for your personal apps
API_KEY = "my secret api key"

# Initialize Google GenAI client (automatically reads GEMINI_API_KEY from environment)
ai_client = genai.Client()


@app.get("/")
def home():
    return {
        "message": "Master AI Controller Hub is online!",
        "status": "Ready to route requests to satellite apps.",
    }


@app.get("/secret-data")
def get_secret_data(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return {
        "status": "Success",
        "data": "Hello future app! You unlocked this private data using your API key.",
    }


@app.post("/ai-command")
def process_command(prompt: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")

    try:
        # Route user prompt through Gemini model
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "You are the Central AI Controller for a suite of personal apps "
                "(Search Engine, Notes, Fitness Tracker). "
                f"Analyze this command and respond helpfully: {prompt}"
            ),
        )
        return {
            "status": "Success",
            "prompt": prompt,
            "ai_response": response.text,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI Processing failed: {str(e)}"
        )