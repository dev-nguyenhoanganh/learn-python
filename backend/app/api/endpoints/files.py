import os
import aiofiles
import numpy as np

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.core.config import settings
from app.services.file_processor import process_file
from app.schemas.file import FileResponse, FileInfo
from datetime import datetime

router = APIRouter()

async def convert_text_to_vector(text: str) -> bytes:
    """
    Convert text file to vector representation.
    This is a placeholder function. Replace with actual vectorization logic.
    """
    # Simple vectorization using numpy
    vector = np.array([ord(c) for c in text], dtype=np.float32)
    return vector.tobytes()

@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Xử lý việc tải lên, xử lý và trích xuất nội dung từ một file.

    Hàm này hỗ trợ các định dạng file cụ thể (ví dụ: DOCX, XLSX) và thực hiện các bước sau:
    1. Kiểm tra phần mở rộng của file để đảm bảo được phép.
    2. Lưu file đã tải lên vào thư mục chỉ định.
    3. Trích xuất nội dung văn bản từ file.
    4. Chuyển đổi nội dung văn bản đã trích xuất thành vector.
    5. Lưu nội dung văn bản và dữ liệu vector vào các file riêng biệt.

    Args:
        file (UploadFile): File được tải lên. Đây là một đối tượng `UploadFile` của FastAPI.

    Returns:
        FileResponse: Phản hồi chứa metadata của file đã tải lên và nội dung văn bản đã trích xuất.

    Raises:
        HTTPException: Nếu phần mở rộng của file không được phép (mã trạng thái 400).
    """
    # Lấy phần mở rộng của file
    file_extension = file.filename.split(".")[-1].lower()

    # Kiểm tra xem phần mở rộng có được phép không
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Loại file không được phép. Các loại file được phép: {settings.ALLOWED_EXTENSIONS}"
        )

    # Tạo thư mục upload nếu chưa tồn tại
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Lưu file vào thư mục uploads
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    try:
        # Sử dụng aiofiles để ghi file bất đồng bộ
        async with aiofiles.open(file_path, "wb") as buffer:
            # Đọc nội dung file
            content = await file.read()
            # Ghi nội dung file vào đường dẫn đã chỉ định
            await buffer.write(content)

        # Xử lý file và trích xuất nội dung văn bản
        extracted_text = await process_file(file_path, file_extension)

        # Ghi nội dung văn bản đã trích xuất vào file .txt trong thư mục uploads
        text_file_path = os.path.join(settings.UPLOAD_DIR, file.filename + ".txt")
        async with aiofiles.open(text_file_path, "w") as text_file:
            await text_file.write(extracted_text)

        # Chuyển đổi nội dung văn bản đã trích xuất thành vector (phù hợp cho mô hình)
        vector_data = await convert_text_to_vector(extracted_text)

        # Lưu dữ liệu vector vào file .vector
        vector_file_path = os.path.join(settings.UPLOAD_DIR, file.filename + ".vector")
        async with aiofiles.open(vector_file_path, "wb") as vector_file:
            await vector_file.write(vector_data)

        # Trả về thông tin file đã upload
        return FileResponse(
            filename=file.filename,
            content_type=file.content_type,
            text_content=extracted_text
        )
    except Exception as e:
        # Xóa file đã upload nếu có lỗi xảy ra
        if os.path.exists(file_path):
            os.remove(file_path)
        # Ném lỗi HTTPException với thông tin chi tiết
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lưu file: {str(e)}"
        )

@router.get("/files", response_model=List[FileInfo])
async def list_files():
    """
    Liệt kê danh sách file trong thư mục upload một cách bất đồng bộ, lọc bỏ các file đã xử lý
    và đảm bảo các file liên quan cần thiết tồn tại.

    Hàm này quét thư mục được chỉ định trong `settings.UPLOAD_DIR` và thu thập thông tin
    về các file đáp ứng các tiêu chí sau:
    - File không có phần mở rộng `.vector`.
    - File có các file liên quan `.txt` và `.vector` trong cùng thư mục.

    Danh sách file trả về được sắp xếp theo thời gian tải lên giảm dần.

    Returns:
        List[FileInfo]: Danh sách các đối tượng `FileInfo` chứa thông tin chi tiết về các file.

    Raises:
        HTTPException: Nếu xảy ra lỗi khi liệt kê file, trả về mã trạng thái 500
        kèm thông báo lỗi chi tiết.

    Lưu ý:
        - Hàm này bỏ qua các file được coi là "đã xử lý" (ví dụ: các file có phần mở rộng `.vector`).
        - Các file không có các file liên quan cần thiết `.txt` hoặc `.vector` sẽ bị bỏ qua.

    Ví dụ:
        >>> files = await list_files()
        >>> for file in files:
        >>>     print(file.filename, file.size, file.uploaded_at)

    """
    # Sử dụng để lưu trữ thông tin về các file hợp lệ.
    files = []
    try:
        # Duyệt tất cả các file trong thư mục upload
        for filename in os.listdir(settings.UPLOAD_DIR):
            # Bỏ qua các file có phần mở rộng .vector, vì đây là các file đã được xử lý.
            if not filename.endswith(('.vector')):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                # Kiểm tra xem file hiện tại có các file liên quan .txt và .vector hay không
                # - File .txt chứa nội dung văn bản đã trích xuất.
                # - File .vector chứa dữ liệu vector hóa.
                if not os.path.exists(file_path + ".txt")  or not os.path.exists(file_path + ".vector"):
                    continue

                # Nếu file hiện tại không phải là file đã xử lý, lấy thông tin về nó
                stats = os.stat(file_path)
                # Lưu trữ thông tin về file hợp lệ vào danh sách files
                files.append(FileInfo(
                    filename=filename,
                    size=stats.st_size,
                    uploaded_at=datetime.fromtimestamp(stats.st_mtime)
                ))
        # Sắp xếp danh sách file theo thời gian tải lên giảm dần (reverse=True),
        # để các file mới nhất xuất hiện trước.
        return sorted(files, key=lambda x: x.uploaded_at, reverse=True)
    except Exception as e:
        # Nếu xảy ra lỗi trong quá trình quét thư mục hoặc xử lý file, trả về lỗi
        # HTTP 500 với thông báo chi tiết.
        raise HTTPException(
            status_code=500,
            detail=f"Could not list files: {str(e)}"
        )

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Xóa một tệp tin và các tệp liên quan dựa trên tên tệp được cung cấp.
    Hàm này kiểm tra sự tồn tại của tệp trong thư mục tải lên, sau đó xóa tệp chính
    và các tệp liên quan (.txt và .vector). Nếu tệp không tồn tại hoặc xảy ra lỗi
    trong quá trình xóa, một HTTPException sẽ được ném ra.
    Args:
        filename (str): Tên của tệp cần xóa.
    Returns:
        dict: Một thông báo xác nhận rằng tệp đã được xóa thành công.
    Raises:
        HTTPException:
            - Nếu tệp không tồn tại (status_code=404).
            - Nếu có lỗi trong quá trình xóa tệp (status_code=500).
    """
    try:
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"File {filename} not found"
            )

        # Xóa file
        os.remove(file_path)
        os.remove(file_path + ".txt")
        os.remove(file_path + ".vector")

        return {"message": f"File {filename} deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )
