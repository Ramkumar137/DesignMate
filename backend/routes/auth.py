from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db, User
from auth import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from utils.response_formatter import success_response
from auth import get_current_user

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, 
        expires_delta=timedelta(minutes=30)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=db_user.id,
        username=db_user.username
    )

@router.post("/signin", response_model=Token)
async def signin(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, 
        expires_delta=timedelta(minutes=30)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=db_user.id,
        username=db_user.username
    )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return success_response({
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat()
    })
