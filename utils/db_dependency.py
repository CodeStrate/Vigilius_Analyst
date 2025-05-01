from fastapi import Request

async def get_db(request: Request):
    """Get a database session from the request state."""
    return request.app.state.prisma