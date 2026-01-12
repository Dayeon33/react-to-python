from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

# CORS: allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str  # The question must be provided in English

class AskResponse(BaseModel):
    question: str
    answer: str

def assert_english(text: str) -> None:
    # If it contains Japanese (Hiragana/Katakana/Kanji), reject.
    if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", text):
        raise HTTPException(
            status_code=400,
            detail="question must be provided in English (Japanese characters detected)",
        )

def to_kansai(answer: str) -> str:
    if not answer:
        return "ちょっと今うまく答えられへんわ。"
    if answer.endswith(("やで。", "やで", "やねん。", "やねん", "やん。", "やん")):
        return answer
    return f"{answer} やで。"

def get_openai_client() -> OpenAI:
    """
    Create OpenAI client lazily to avoid crashing the container at import/startup time.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    q = (req.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="question is required")
    if len(q) > 2000:
        raise HTTPException(status_code=400, detail="question is too long")

    assert_english(q)

    try:
        client = get_openai_client()
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": "You must respond in Kansai dialect Japanese."},
                {"role": "user", "content": q},
            ],
        )
        answer_text = (resp.output_text or "").strip()
        answer_text = to_kansai(answer_text)
        return AskResponse(question=q, answer=answer_text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get answer: {type(e).__name__}")

# ✅ Cloud Run: listen on $PORT (default 8080)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)




