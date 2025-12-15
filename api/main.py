from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

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

import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str

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

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=q,
        )
        answer_text = (resp.output_text or "").strip()
        return AskResponse(question=q, answer=answer_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get answer: {type(e).__name__}")
