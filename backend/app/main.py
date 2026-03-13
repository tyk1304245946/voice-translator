import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routers import translate, tts, history, feishu
from app.services.feishu_bitable_service import start_feishu_polling, stop_feishu_polling

# 确保 audio/dbdata 目录在模块加载时就存在（StaticFiles 需要目录存在）
os.makedirs("audio", exist_ok=True)
os.makedirs("dbdata", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await start_feishu_polling()
    yield
    await stop_feishu_polling()


app = FastAPI(
    title="Voice Translator API",
    description="Chinese to English translation + ElevenLabs TTS",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件：音频
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# 路由
app.include_router(translate.router, prefix="/api", tags=["translate"])
app.include_router(tts.router, prefix="/api", tags=["tts"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(feishu.router, prefix="/api", tags=["feishu"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
