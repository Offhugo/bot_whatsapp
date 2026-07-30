from fastapi import FastAPI

from app.routers.webhook import router as webhook_router

app = FastAPI(
    title="WhatsApp Bot API"
)

app.include_router(webhook_router)