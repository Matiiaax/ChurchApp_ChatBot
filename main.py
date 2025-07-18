from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
import os

# ==== konfiguracja ====
OPENAI_API_KEY = os.getenv("API_KEY")
MODEL = "gpt-3.5-turbo"   # lub "gpt-4o"

# ==== stały prompt z faktami ====
def load_prompt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

# ===== Inicjalizacja =====
SYSTEM_PROMPT = load_prompt("prompt.txt")
# ==== inicjalizacja ====
client = OpenAI(api_key=OPENAI_API_KEY)
app    = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== endpoint /chat ====
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return JSONResponse({"reply": "Nie otrzymałem pytania."}, status_code=400)

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=250,
        )
        answer = res.choices[0].message.content.strip()
        return JSONResponse({"reply": answer}, media_type="application/json; charset=utf-8")

    except Exception as e:
        return JSONResponse({"reply": f"Błąd serwera: {e}"}, status_code=500)
