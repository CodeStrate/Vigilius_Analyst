from fastapi import Depends, APIRouter, HTTPException, status
from prisma import Prisma
from backend.models.userModel import UserLoginModel
from utils.db_dependency import get_db

router = APIRouter()

@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def sign_up_user(payload: UserLoginModel, db: Prisma = Depends(get_db)):
    try:
        logged_in_user = await db.user.find_first(
            where={
                "email": payload.email,
                "password": payload.password
            }
        )
        if not logged_in_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    except HTTPException as http_ex:
        raise http_ex    
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    return {"message": "User logged in successfully", "currently_logged_in_as": {"name" : logged_in_user.name, "email" : logged_in_user.email}}