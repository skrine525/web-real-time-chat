import datetime
from fastapi.routing import APIRouter
from fastapi import  Depends, HTTPException, status
from jose import jwt
from app.utils import auth
from app.schemas import token as token_schema
from app.schemas import user as user_schema
from sqlalchemy import orm
from app.database import operations, get_db


router = APIRouter(prefix="/auth") 


@router.post("/register", response_model=token_schema.Token)
def create_user_endpoint(user: user_schema.UserAuth, db: orm.Session = Depends(get_db)):
    db_user = operations.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    db_user = operations.create_user(db=db, user=user)

    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = jwt.encode(
        {"sub": db_user.username, "exp": datetime.datetime.now(datetime.timezone.utc) + access_token_expires},
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM,
    )
    
    return {"access_token": access_token}

@router.post("/login", response_model=token_schema.Token)
async def login_endpoint(credentials: user_schema.UserAuth, db: orm.Session = Depends(get_db)):
    user = operations.get_user_by_username(db, username=credentials.username)
    if not user or not auth.pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = jwt.encode(
        {"sub": user.username, "exp": datetime.datetime.now(datetime.timezone.utc) + access_token_expires},
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM,
    )
    
    return {"access_token": access_token}
