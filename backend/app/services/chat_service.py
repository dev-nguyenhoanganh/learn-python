import os
import numpy as np

from app.core.config import settings
from typing import List, Optional

def load_context_from_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Đọc nội dung file và trả về nội dung dưới dạng chuỗi.

    Tham số:
        file_path (str): Đường dẫn tới tệp cần tải.
    Trả về:
        str: Nội dung của tệp dưới dạng chuỗi. Trả về chuỗi rỗng nếu tệp không tồn tại
        hoặc nếu xảy ra lỗi trong quá trình đọc tệp.
    Ngoại lệ:
        Exception: Bắt và ghi lại bất kỳ ngoại lệ nào xảy ra trong quá trình đọc tệp.
    """
    # Kiểm tra xem file_path có phải là chuỗi hợp lệ không
    if not isinstance(file_path, str) or not file_path.strip():
        print("Invalid file path provided.")
        return ""

    try:
        # Đọc nội dung file và trả về nội dung dưới dạng chuỗi
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()

    except FileNotFoundError:
        print(f"File {file_path} does not exist.")
        return ""
    except PermissionError:
        print(f"Permission denied for file {file_path}.")
        return ""
    except IOError as e:
        print(f"I/O error while reading file {file_path}: {str(e)}")
        return ""
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        return ""

async def find_relevant_context(message: str, context_files: Optional[List[str]] = None, ext: str = ".txt") -> str:
    """
    Tìm kiếm ngữ cảnh liên quan từ các tệp được cung cấp dựa trên tin nhắn đầu vào.

    Tham số:
        message (str): Tin nhắn đầu vào từ người dùng.
        context_files (Optional[List[str]]): Danh sách các tệp chứa ngữ cảnh.
        ext (str): Đuôi tệp cần tìm kiếm. Mặc định là ".txt".

    Trả về:
        str: Ngữ cảnh liên quan được tìm thấy từ các tệp. Nếu không tìm thấy, trả về chuỗi rỗng.
    """
    all_context = ""

    if context_files is None:
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith(".txt"):
                content = await load_context_from_file(os.path.join(settings.UPLOAD_DIR, filename))

                # TODO: TEST - find the context that is most relevant to the message
                if message in content:
                    all_context = content
                    break
    else:
        for filename in context_files:
            file_path = os.path.join(settings.UPLOAD_DIR, filename + ext)
            if os.path.exists(file_path):
                content = await load_context_from_file(file_path)

                # TODO: TEST - find the context that is most relevant to the message
                if message in content:
                    all_context = content
                    break

                # all_context += content + "\n\n"

    return all_context

async def process_chat_message(message: str, context_files: Optional[List[str]] = None) -> str:
    """
    Process a chat message and return a response
    """
    try:
        # Get relevant context from uploaded files. extension is .vector
        context = await find_relevant_context(message, context_files, ".txt")

        # For now, return a simple response
        # TODO: Implement actual chat processing logic
        if context:
            return f"I found some relevant information from the uploaded files: {context[:200]}..."
        else:
            return "I don't have any relevant information from the uploaded files to answer your question."

    except Exception as e:
        raise Exception(f"Error processing chat message: {str(e)}")
