import google.generativeai as genai

from fastapi import APIRouter, Query
from app.schemas.gemini import DataRequest, DataResponse
from app.services.gemini_service import send_async

router = APIRouter()

@router.get("/gemini", response_model=DataResponse)
def get_gemini_response(prompt: str = Query(...)):
    """
    Gửi yêu cầu đến mô hình Gemini và nhận phản hồi.

    Args:
        prompt (str): Chuỗi đầu vào để gửi đến mô hình Gemini.

    Returns:
        str: Phản hồi từ mô hình Gemini.
    """
    try:
        print(f"Prompt: {prompt}")
        # Gọi hàm send_async để gửi yêu cầu đến mô hình Gemini
        return DataResponse(response=send_async(prompt))
    except Exception as e:
        raise Exception(f"Error generating response from Gemini: {str(e)}")