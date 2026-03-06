import os
import time
import uvicorn
import pyotp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory of project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to secret.txt
SECRET_FILE = os.path.join(BASE_DIR, "secret.txt")


def get_secret() -> str:
    # First check environment variable (Render)
    secret = os.getenv("TOTP_SECRET")

    if secret:
        return secret

    # Fallback to file for local development
    if not os.path.exists(SECRET_FILE):
        raise HTTPException(status_code=500, detail="secret.txt not found")

    with open(SECRET_FILE, "r", encoding="utf-8") as f:
        secret = f.read().strip()

    if not secret:
        raise HTTPException(status_code=500, detail="Secret is empty")

    return secret


@app.get("/otp")
def get_otp() -> dict:
    try:
        secret = get_secret()
        totp = pyotp.TOTP(secret)

        current_otp = totp.now()
        remaining = 30 - (int(time.time()) % 30)

        return {
            "otp": current_otp,
            "expires_in": remaining
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Secure TOTP API running"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)