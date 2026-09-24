import hashlib
from fastapi import Depends, FastAPI, HTTPException, Header

# 1. Initialize our API app
app = FastAPI(title="My Universal API")

# 2. This is our master secret API Key
# In real life, you give this key to your future app!
MASTER_API_KEY = "my_super_secret_app_key_123"

# Save the hashed secret code (like we learned before)
VALID_KEY_HASH = hashlib.sha256(MASTER_API_KEY.encode()).hexdigest()


# 3. The Guard Function: Checks incoming API Keys
def verify_api_key(x_api_key: str = Header(...)):
    """This function acts like a bouncer at the door."""
    # Hash the incoming key sent by the caller
    incoming_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    # Compare it to our saved secret code
    if incoming_hash != VALID_KEY_HASH:
        # Block them with a 401 Unauthorized error
        raise HTTPException(
            status_code=401, detail="Stop! Invalid or missing API Key."
        )

    return x_api_key


# 4. Public Route (Anyone can visit this without an API Key)
@app.get("/")
def home():
    return {"message": "Welcome! The API is live and running."}


# 5. Protected Route (Requires a valid API Key)
@app.get("/secret-data", dependencies=[Depends(verify_api_key)])
def get_secret_data():
    return {
        "status": "Success",
        "data": "Hello future app! You unlocked this private data using your API key.",
    }