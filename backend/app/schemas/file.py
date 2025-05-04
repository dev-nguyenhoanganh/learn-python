from pydantic import BaseModel, Field
from datetime import datetime

class FileResponse(BaseModel):
  """
  Mô hình dữ liệu cho phản hồi từ hệ thống xử lý tệp.
  """
  filename: str = Field(..., description="Tên của tệp đã được tải lên")
  content_type: str = Field(..., description="Loại nội dung của tệp")
  text_content: str = Field(..., description="Nội dung văn bản của tệp")

class FileInfo(BaseModel):
    """
    Mô hình dữ liệu cho thông tin tệp.
    """
    filename: str = Field(..., description="Tên tệp")
    size: int = Field(..., description="Kích thước tệp (byte)")
    uploaded_at: datetime = Field(..., description="Thời gian tải lên tệp")
