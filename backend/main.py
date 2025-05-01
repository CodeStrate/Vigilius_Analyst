from fastapi import FastAPI
from prisma import Prisma
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routes import (
    sign_up_route,
    log_in_route,
    health
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prisma = Prisma()
    await app.state.prisma.connect()
    yield
    await app.state.prisma.disconnect()

app = FastAPI(title="Chatbot App API", version="0.1beta", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sign_up_route.router, prefix="/api/v1", tags=["User Sign Up"])
app.include_router(log_in_route.router, prefix="/api/v1", tags=["User Log In"])
app.include_router(health.router, prefix="/api/v1", tags=["Health Check"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot App API!"}