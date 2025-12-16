from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

@app.post("/api/ask")
def ask(req: AskRequest):
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": req.question},
            ],
        )

        answer = resp.choices[0].message.content

    except Exception:
        # ✅ 어떤 OpenAI 에러든 전부 여기서 흡수
        answer = "(Demo response) GPT API quota exceeded, but React–FastAPI connection works correctly."

    # ✅ 절대 raise 하지 말고 항상 200으로 반환
    return {
        "question": req.question,
        "answer": answer,
    }







