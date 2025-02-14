from fastapi.security import OAuth2PasswordBearer   
from passlib.context import CryptContext  
from models import User  
from jose import JWTError, jwt  
from datetime import datetime, timedelta, timezone  
from data import refresh_tokens  
from typing import Annotated  
from fastapi import Depends, HTTPException, status  
from data import fake_users_db, refresh_tokens  
from pydantic import ValidationError
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  
  
SECRET_KEY = "hdhfh5jdnb7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  
ALGORITHM = "HS256"  
  
def get_user(db, username: str):  
    for user in db:
        if user["username"] == username:
            return User(**user)
    return None  # Return None if the user is not found

  
def authenticate_user(fake_db, username: str, password: str):  
    user = get_user(fake_db, username)  
    if not user:
        print(f"User {username}  not found")  
        return False  
    if not pwd_context.verify(password, user.hashed_password):  
        print("Password {password} verification failed")
        return False  
    return user  
  
  
def create_token(data: dict, expires_delta: timedelta | None = None):  
    to_encode = data.copy()  
    if expires_delta:  
        expire = datetime.now(timezone.utc) + expires_delta  
    else:  
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)  
    to_encode.update({"exp": expire})  
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  
    return encoded_jwt  
  
  
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):  
    credentials_exception = HTTPException(  
        status_code=status.HTTP_401_UNAUTHORIZED,  
        detail="Could not validate credentials",  
        headers={"WWW-Authenticate": "Bearer"},  
    )  
    try:  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        username: str = payload.get("sub")  
        if username is None:  
            raise credentials_exception  
    except JWTError:  
        raise credentials_exception  
    user = get_user(fake_users_db, username=username)  
    if user is None:  
        raise credentials_exception  
    return user  
  
  
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):  
    if current_user.disabled:  
        raise HTTPException(status_code=400, detail="Inactive user")  
    return current_user  
  
  
async def validate_refresh_token(token: Annotated[str, Depends(oauth2_scheme)]):  
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")  
    try:  
        if token in refresh_tokens:  
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
            username: str = payload.get("sub")  
            role: str = payload.get("role")  
            if username is None or role is None:  
                raise credentials_exception  
        else:  
            raise credentials_exception  
  
    except (JWTError, ValidationError):  
        raise credentials_exception  
    user = get_user(fake_users_db, username=username)  
    if user is None:  
        raise credentials_exception  
    return user, token  
  
  
class RoleChecker:  
  def __init__(self, allowed_roles):  
    self.allowed_roles = allowed_roles  
  
  def __call__(self, user: Annotated[User, Depends(get_current_active_user)]):  
    if user.role in self.allowed_roles:  
      return True  
    raise HTTPException(  
status_code=status.HTTP_401_UNAUTHORIZED,   
detail="You don't have enough permissions")  
