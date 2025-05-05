from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from prisma import Prisma
from prisma.errors import UniqueViolationError
from backend.models.userModel import UserSignupModel
from utils.db_dependency import get_db

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up_user(payload: UserSignupModel, db: Prisma = Depends(get_db)):
    try:
        new_user = await db.user.create({"name" : payload.name, "email":payload.email, "password": payload.password})
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    return JSONResponse(content={"message": "User created successfully", "new_user": {"name" : new_user.name, "email" : new_user.email}})