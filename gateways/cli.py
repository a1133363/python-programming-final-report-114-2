import os
import asyncio

from openai import AsyncOpenAI

from llm.openai import generate


async def run(model, session_id, context, tools):
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")

    print(
        f"\n已進入對話模式，目前模型：{model}\n"
        f"Session ID：{session_id}\n"
        "輸入 exit 或 quit 返回指令頁。"
    )

    async with AsyncOpenAI(api_key=api_key, base_url=api_url) as client:
        while True:
            try:
                user_input = (await asyncio.to_thread(input, "\n你：")).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n已返回指令頁。")
                return

            if not user_input:
                continue
            elif user_input.lower() in {"exit", "quit"}:
                print("已返回指令頁。")
                return
            else:
                async for event in generate(client, model, context, tools, user_input):
                    if event["type"] in {"assistant_text", "final_answer"}:
                        print(f"AI：{event['content']}")
                    elif event["type"] == "tool_started":
                        print(f"AI 使用工具：{event['name']}")
                    elif event["type"] == "tool_finished":
                        if not event["success"]:
                            print(f"工具 {event['name']} 執行失敗：{event['result']}")
                        else:
                            print(f"工具 {event['name']} 執行成功：{event['result']}")
                    elif event["type"] == "error":
                        print(event["message"])
