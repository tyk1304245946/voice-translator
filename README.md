# Voice Translator — 中文口播转英文语音工具

将中文口播文本翻译成英文，并用 ElevenLabs 生成自然的英文语音。

## 功能

- **翻译**：中文 → 英文（火山方舟 ark-code-latest）
- **语音**：英文文本转语音（ElevenLabs API），支持播放 & 下载
- **短视频优化**：句子更短、更口语化，适合 Reels / TikTok 场景
- **批量处理**：一次提交多条文案，逐条生成翻译和音频
- **飞书同步**：从多维表格批量读取中文脚本，自动回填英文脚本和英文音频附件
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
# 编辑 .env，填入你的 ARK_API_KEY 和 ELEVENLABS_API_KEY
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
| 火山方舟    | https://www.volcengine.com/product/ark | 按平台计费策略执行 |
| ElevenLabs  | https://elevenlabs.io             | 每月 10,000 字符免费           |

## ElevenLabs Voice ID

默认使用 `Rachel`（ID: `21m00Tcm4TlvDq8ikWAM`）。

其他免费声音可在 [ElevenLabs 控制台](https://elevenlabs.io/app/voice-library) 查找。
在 `.env` 中修改 `ELEVENLABS_VOICE_ID` 即可切换。

## 飞书多维表格批量同步

后端支持两种方式同步飞书多维表格：

- 手动触发：调用接口一次处理 N 条
- 自动轮询：服务启动后按固定间隔自动处理

### 1. 环境变量

在 `.env` 中补充以下配置：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_BITABLE_APP_TOKEN=bascnxxxxxxxxxxxx
FEISHU_TABLE_ID=tblxxxxxxxxxxxx

FEISHU_CHINESE_FIELD=中文脚本
FEISHU_ENGLISH_FIELD=英文脚本
FEISHU_AUDIO_FIELD=音频

FEISHU_POLL_ENABLED=false
FEISHU_POLL_INTERVAL_SECONDS=60
FEISHU_BATCH_SIZE=3

FEISHU_TRANSLATE_MODE=short_video
# FEISHU_VOICE_ID=

# 降级模式：音频失败时，仍写回英文脚本
FEISHU_FALLBACK_TEXT_ONLY_ON_AUDIO_FAIL=true
```

处理规则：处理“中文脚本非空，且（英文脚本为空或音频为空）”的记录；若英文已存在仅补传音频，不重复翻译。

### 2. 手动触发接口

`POST /api/feishu/sync`

请求体示例：

```json
{
	"limit": 3,
	"mode": "short_video",
	"voice_id": null,
	"audio_only": false
}
```

`audio_only=true` 时仅补传音频，不触发翻译。

返回示例：

```json
{
	"scanned": 35,
	"processed": 20,
	"downgraded": 3,
	"skipped": 15,
	"failed": 0,
	"errors": []
}
```

其中 `downgraded` 表示“音频失败但已成功回填英文脚本”的记录数。

### 3. 自动轮询

将 `FEISHU_POLL_ENABLED=true` 后，后端启动时会自动开启轮询任务：

- 每次最多处理 `FEISHU_BATCH_SIZE` 条
- 间隔 `FEISHU_POLL_INTERVAL_SECONDS` 秒
- 后端关闭时自动停止

前端页面也支持在线查看/调整轮询配置，对应接口：

- `GET /api/feishu/polling-config`
- `PATCH /api/feishu/polling-config`

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
│   │       ├── translation.py   # 火山方舟翻译
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
