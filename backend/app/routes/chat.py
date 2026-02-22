# backend/app/routes/chat.py
# OPTION A — Backend speaks Vercel AI SDK stream protocol.
# Keeps useChat on the frontend untouched.
# Vercel AI SDK expects chunks prefixed with: 0:"text here"\n
# (the "0:" prefix means "text delta", which is what useChat renders)

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import json

from app.services import gemini_service

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def vercel_stream():
        async for chunk in gemini_service.generate_chat_stream(request.messages):
            # Vercel AI SDK data stream protocol: 0:"<escaped text>"\n
            # json.dumps handles all escaping (quotes, newlines, unicode)
            yield f"0:{json.dumps(chunk)}\n"

    return StreamingResponse(
        vercel_stream(),
        media_type="text/plain",          # useChat expects text/plain, not text/event-stream
        headers={"x-vercel-ai-data-stream": "v1"},  # required header for useChat to parse
    )