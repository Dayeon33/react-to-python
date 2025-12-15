from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = FastAPI()

# CORS: allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AskRequest(BaseModel):
    question: str  # The question must be provided in English

class AskResponse(BaseModel):
    question: str
    answer: str

def assert_english(text: str) -> None:
    """
    Enforce that the input question is written in English.
    This is a lightweight heuristic (not perfect) but good for assignment requirements.
    """
    # If it contains Japanese (Hiragana/Katakana/Kanji), reject.
    if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", text):
        raise HTTPException(
            status_code=400,
            detail="question must be provided in English (Japanese characters detected)",
        )

def to_kansai(answer: str) -> str:
    """
    Force Kansai dialect style for all responses.
    This post-processing guarantees consistent Kansai-style output.
    """
    if not answer:
        return "ちょっと今うまく答えられへんわ。"
    # If it already ends with common Kansai endings, keep it.
    if answer.endswith(("やで。", "やで", "やねん。", "やねん", "やん。", "やん")):
        return answer
    return f"{answer} やで。"

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

    # Enforce English input
    assert_english(q)

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            # Force Kansai dialect at the model level as well (belt-and-suspenders)
            input=[
                {"role": "system", "content": "You must respond in Kansai dialect Japanese."},
                {"role": "user", "content": q},
            ],
        )
        answer_text = (resp.output_text or "").strip()

        # Guarantee Kansai dialect output
        answer_text = to_kansai(answer_text)

        return AskResponse(question=q, answer=answer_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get answer: {type(e).__name__}")


