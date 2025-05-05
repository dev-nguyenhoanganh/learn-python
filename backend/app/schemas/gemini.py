from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DataRequest(BaseModel):
    """
    Mô hình dữ liệu cho một tin nhắn trong chat.
    """
    # id: int
    # sender_id: int
    # receiver_id: int
    # timestamp: datetime
    text: str

class DataResponse(BaseModel):
    """
    Mô hình dữ liệu cho phản hồi từ hệ thống chat.
    """
    response: Optional[str] = None
    timestamp: datetime = datetime.now()