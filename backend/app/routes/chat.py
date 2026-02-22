from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services import gemini_service
from fastapi.responses import StreamingResponse

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Pass the messages to Gemini and stream the response
    generator = gemini_service.generate_chat_stream(request.messages)
    return StreamingResponse(generator, media_type="text/event-stream")
