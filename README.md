# AI CLI

使用 OpenAI Python SDK 製作的命令列 AI 對話程式。

## 安裝

```powershell
uv sync
```

## 設定

將 `.env.example` 複製為 `.env`，並填入模型與對應供應商的 API Key。

以 OpenAI 相容的 API 端點為例：

```dotenv
API_URL=https://example.com/v1
API_KEY=your-api-key
MODEL=openai/gpt-4o-mini
```

`MODEL` 應使用該端點 `/v1/models` 回傳的完整模型 ID，程式會將該 ID
原樣傳給 API。

若直接連線 OpenAI 而不設定 `API_URL`，可以改用 SDK 標準的
`OPENAI_API_KEY` 環境變數：

```dotenv
MODEL=gpt-5.1
OPENAI_API_KEY=your-api-key
```

也可以使用 `API_BASE` 或 `OPENAI_BASE_URL` 取代 `API_URL`。

## 執行

```powershell
uv run main.py
```

啟動後可輸入以下指令：

- `chat`：開啟 CLI 對話。對話中輸入 `exit` 或 `quit` 返回指令頁。
- `models`：取得模型列表，並以編號或模型 ID 切換模型。
- `exit` 或 `quit`：結束程式。

每次輸入 `chat` 都會建立全新的對話，不會保留上一次的對話紀錄。

`llm/openai.py` 以同步 generator 產生通用事件，包含 AI 文字、
工具開始、工具完成、最終回答與錯誤。Gateway 只需處理輸入和事件顯示，
不需管理 OpenAI 的工具呼叫 context。

## 架構

```text
gateways/cli.py    CLI 輸入與事件顯示
llm/openai.py      對話 context、OpenAI API 與工具調用迴圈
tools/tool_call.py 工具執行處理
tools/tools.json   OpenAI tools 定義
main.py            程式入口、環境設定與指令處理
```
