from fastapi import FastAPI
from prisma import Prisma
import ngrok, os
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routes import (
    sign_up_route,
    log_in_route,
    health,
    chat_route
)
from dotenv import load_dotenv
load_dotenv()

NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
APPLICATION_PORT = int(os.getenv("BACKEND_PORT", "8000"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prisma = Prisma()
    logger.info("Connecting to Prisma...")
    if NGROK_AUTH_TOKEN:
        logger.info("Starting ngrok tunnel...")
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        tunnel = await ngrok.forward(APPLICATION_PORT)
        logger.success(f"ngrok tunnel started at: {tunnel.url()}")
    else:
        logger.warning("NGROK_AUTH_TOKEN not set. Ngrok tunnel will not be started.")
    
    await app.state.prisma.connect()
    logger.success("Connected to Prisma.")
    yield
    logger.info("Disconnecting from Prisma...")
    await app.state.prisma.disconnect()
    await ngrok.disconnect()
    logger.info("Ngrok tunnel disconnected.")

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
app.include_router(chat_route.router, prefix="/api/v1", tags=["Chatbot"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot App API!"}