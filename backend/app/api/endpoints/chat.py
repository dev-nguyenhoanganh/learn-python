from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.chat_service import process_chat_message
from asyncio import TimeoutError, wait_for

router = APIRouter()

# Constants for chat processing
MAX_MESSAGE_SIZE = 1024  # 1 KB

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """
    Xử lý yêu cầu trò chuyện và trả về phản hồi.

    Hàm này nhận một tin nhắn trò chuyện từ người dùng, xử lý tin nhắn đó và trả về phản
    hồi dưới dạng đối tượng `ChatResponse`. Nếu có lỗi xảy ra trong quá trình xử lý,
    nó sẽ trả về một HTTPException với mã lỗi 500.

    Args:
        message (ChatMessage): Đối tượng chứa nội dung tin nhắn từ người dùng.

    Returns:
        ChatResponse: Đối tượng chứa phản hồi từ hệ thống.

    Raises:
        HTTPException: Nếu xảy ra lỗi trong quá trình xử lý tin nhắn, trả về mã lỗi 500
            và chi tiết lỗi.
    """
    try:
        answer_msg = await process_chat_message(message.text)
        return ChatResponse(response=answer_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    Xử lý kết nối WebSocket cho trò chuyện.

    Hàm này thiết lập một kết nối WebSocket và lắng nghe các tin nhắn từ người dùng.
    Khi nhận được một tin nhắn, nó sẽ xử lý tin nhắn đó và gửi phản hồi trở lại cho
    người dùng. Nếu có lỗi xảy ra trong quá trình xử lý, nó sẽ đóng kết nối WebSocket.

    Args:
        websocket (WebSocket): Đối tượng WebSocket để giao tiếp với người dùng.

    Raises:
        WebSocketDisconnect: Nếu kết nối WebSocket bị ngắt.
    """
    # Chấp nhận kết nối WebSocket. Nếu không gọi dòng này thì không thể giao tiếp.
    # Thông thường sẽ cần kiểm tra JWT token ở đây để xác thực người dùng.
    await websocket.accept()
    try:
        while True:
            # Nhận tin nhắn từ WebSocket. Nếu không có tin nhắn trong 30 giây, sẽ timeout.
            received_text = await wait_for(websocket.receive_text(), timeout=30)  # 30s

            # Chống tấn công DoS (Denial of Service) bằng cách giới hạn kích thước message
            if len(received_text) > MAX_MESSAGE_SIZE:
                await websocket.send_text(ChatResponse(response="Message too large").json())
                continue

            # Check dữ liệu đầu vào để đảm bảo dữ liệu hợp lệ và tránh lỗi không mong muốn
            if not received_text.strip():
                await websocket.send_text(ChatResponse(response="Empty message").json())
                continue

            # Chuyển đổi tin nhắn nhận được thành object ChatMessage
            # (được định nghĩa trong app.schemas.chat) để đảm bảo dữ liệu hợp lệ.
            message = ChatMessage.model_validate_json({"text": received_text})
            answer_msg = await process_chat_message(message.text)

            # Nếu không thể chuyển đổi thành ChatMessage, gửi phản hồi lỗi về cho người dùng.
            if not isinstance(answer_msg, str):
                answer_msg = "Invalid response from server"

            response = ChatResponse(response=answer_msg)
            await websocket.send_text(response.json())

            # Dừng kết nối WebSocket nếu người dùng gửi tin nhắn "exit".
            if received_text == "exit":
                await websocket.close()
                break
    except WebSocketDisconnect:
        print("WebSocket connection closed")
    except TimeoutError:
        await websocket.close()
        print("WebSocket connection closed due to timeout")
    except Exception as e:
        res = ChatResponse(response=f"Error processing WebSocket message: {str(e)}")
        await websocket.send_text(res.json())
