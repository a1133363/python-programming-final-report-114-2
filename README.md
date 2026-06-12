# AI CLI

使用 OpenAI Python SDK 製作的基礎命令列 AI 對話程式。

## 安裝

```powershell
uv sync
```

## 設定

將 `.env.example` 複製為 `.env`，並填入模型與對應供應商的 API Key。

以 OpenAI 相容的 API 端點為例：

```dotenv
API_BASE=https://example.com/v1
API_KEY=your-api-key
MODEL=openai/gpt-4o-mini
```

`MODEL` 應使用該端點 `/v1/models` 回傳的完整模型 ID，程式會將該 ID
原樣傳給 API。

若直接連線 OpenAI 而不設定 `API_BASE`，可以改用 SDK 標準的
`OPENAI_API_KEY` 環境變數：

```dotenv
MODEL=gpt-5.1
OPENAI_API_KEY=your-api-key
```

也可以使用 `OPENAI_BASE_URL` 取代 `API_BASE`。

## 執行

```powershell
uv run main.py
```

輸入 `exit` 或 `quit` 即可結束程式。
