from fastapi import APIRouter, status

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify if the server is running.
    """
    return {"status": "ok", "message": "Server is running!"}