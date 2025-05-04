# Module: app.api.endpoints.auth
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

# Utils
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configurations
SECRET_KEY = "radom_secret_key"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Tạo một JSON Web Token (JWT) access token.

    Hàm này tạo một JWT access token bằng cách mã hóa dữ liệu được cung cấp với
    thời gian hết hạn. Thời gian hết hạn có thể được tùy chỉnh bằng cách truyền
    một đối tượng `timedelta`; nếu không, thời gian hết hạn mặc định sẽ được sử dụng.

    Args:
        data (dict):
            Đây là dữ liệu (payload) sẽ được mã hóa vào token.
            Thường chứa thông tin người dùng hoặc các thông tin cần thiết khác.
        expires_delta (Optional[timedelta]):
            Thời gian hết hạn của token. Nếu không được cung cấp,
            hàm sẽ sử dụng giá trị mặc định.

    Returns:
        str: JWT đã được mã hóa dưới dạng chuỗi.
    """
    # Tạo một bản sao của dữ liệu để tránh thay đổi dữ liệu gốc.
    to_encode = data.copy()

    if expires_delta:
        # Nếu `expires_delta` được cung cấp,
        # Thời gian hết hạn của token sẽ được tính dựa trên giá trị này.
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        # Nếu không, thời gian hết hạn mặc định là ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Thêm trường "exp" (expiration) vào payload.
    # Đây là một chuẩn trong JWT để chỉ định thời gian hết hạn của token.
    to_encode.update({"exp": expire})
    # Mã hóa payload (to_encode) thành một JWT.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Trả về JWT đã được mã hóa
    return encoded_jwt

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Hàm login xử lý yêu cầu đăng nhập của người dùng.

    Chức năng:
        - Giả lập việc đăng nhập bằng cách kiểm tra username và password từ form_data.
        - Nếu thông tin hợp lệ, tạo một access token
        - Nếu thông tin không hợp lệ, trả về lỗi HTTP 401.

    Args:
        form_data (OAuth2PasswordRequestForm): Dữ liệu đăng nhập (username, password, ...)
    Returns:
        dict: Trả về một dictionary chứa access_token nếu đăng nhập thành công.
    Raises:
        HTTPException: Nếu thông tin đăng nhập không hợp lệ, trả về lỗi HTTP 401
    """

    # Giả lập việc đăng nhập bằng dummy user (username: any, password: any)
    username = form_data.username
    password = form_data.password

    # Giả lập việc xác thực người dùng, trong thực tế sẽ cần query DB để check
    if username and password:
        if len(username) > 8:
            access_token = create_access_token(
                data={"sub": form_data.username},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Username must be more than 8 characters",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
