import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-001",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def send_async(prompt: str) -> str:
    """
    Gửi yêu cầu đến mô hình Gemini và nhận phản hồi không đồng bộ.

    Args:
        prompt (str): Chuỗi đầu vào để gửi đến mô hình Gemini.

    Returns:
        str: Phản hồi từ mô hình Gemini.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Error generating response from Gemini: {str(e)}")
