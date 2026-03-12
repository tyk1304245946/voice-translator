# Voice Translator — 中文口播转英文语音工具

将中文口播文本翻译成英文，并用 ElevenLabs 生成自然的英文语音。

## 功能

- **翻译**：中文 → 英文（OpenAI GPT-4o-mini）
- **语音**：英文文本转语音（ElevenLabs API），支持播放 & 下载
- **短视频优化**：句子更短、更口语化，适合 Reels / TikTok 场景
- **批量处理**：一次提交多条文案，逐条生成翻译和音频
- **历史记录**：本地 SQLite 存储，随时回放/删除

## 技术栈

| 层     | 技术                         |
|--------|------------------------------|
| 后端   | Python + FastAPI + SQLAlchemy (SQLite) |
| 环境管理 | [uv](https://docs.astral.sh/uv/) |
| 前端   | React + TypeScript + Vite + Tailwind CSS |
| 运行   | Docker + Docker Compose       |

## 快速开始

### 1. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY 和 ELEVENLABS_API_KEY
```

### 2. Docker 启动（推荐）

```bash
docker-compose up --build
```

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 3. 本地开发

**后端**
```bash
cd backend
uv sync
cp ../.env.example .env   # 或直接使用根目录 .env
uv run uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## API Keys 获取

| 服务        | 注册地址                          | 免费额度                      |
|-------------|-----------------------------------|-------------------------------|
| OpenAI      | https://platform.openai.com       | 按量计费，gpt-4o-mini 极低价  |
| ElevenLabs  | https://elevenlabs.io             | 每月 10,000 字符免费           |

## ElevenLabs Voice ID

默认使用 `Rachel`（ID: `21m00Tcm4TlvDq8ikWAM`）。

其他免费声音可在 [ElevenLabs 控制台](https://elevenlabs.io/app/voice-library) 查找。
在 `.env` 中修改 `ELEVENLABS_VOICE_ID` 即可切换。

## 项目结构

```
voice-translator/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 环境变量配置
│   │   ├── database.py      # SQLite 模型 & 会话
│   │   ├── schemas.py       # Pydantic 请求/响应模型
│   │   ├── routers/         # API 路由
│   │   │   ├── translate.py
│   │   │   ├── tts.py
│   │   │   └── history.py
│   │   └── services/        # 业务逻辑
│   │       ├── translation.py   # OpenAI 翻译
│   │       └── elevenlabs_service.py  # ElevenLabs TTS
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── TranslatorForm.tsx
│   │   │   ├── ResultPanel.tsx
│   │   │   ├── AudioPlayer.tsx
│   │   │   └── HistoryPanel.tsx
│   │   ├── api/client.ts
│   │   └── types/index.ts
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```
