from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    """
    Mô hình dữ liệu cho một tin nhắn trong chat.
    """
    # id: int
    # sender_id: int
    # receiver_id: int
    # timestamp: datetime
    text: str
    context_files: Optional[List[str]] = None

class ChatResponse(BaseModel):
    """
    Mô hình dữ liệu cho phản hồi từ hệ thống chat.
    """
    response: Optional[str] = None
    timestamp: datetime = datetime.now()