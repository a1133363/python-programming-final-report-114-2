import asyncio
import os

from openai import AsyncOpenAI

from llm.openai import create_context, generate, load_tools

TOOL_LABELS = {
    "read_file": "查看檔案",
    "search_files": "搜尋檔案",
    "create_file": "新增檔案",
}


async def read(prompt=""):
    return await asyncio.to_thread(input, prompt)


async def write(*values, sep=" ", end="\n"):
    await asyncio.to_thread(print, *values, sep=sep, end=end)


async def _print_tool_started(event):
    tool_name = event["name"]
    arguments = event["arguments"]
    label = TOOL_LABELS.get(tool_name, tool_name)
    target = arguments.get("path") or arguments.get("pattern")
    target_text = f"：{target}" if target else ""
    await write(f"AI 使用工具：{label}{target_text}")


async def _print_tool_finished(event):
    tool_name = event["name"]
    result = event["result"]

    if not event["success"]:
        await write(result)
    elif tool_name == "search_files":
        if result == "找不到符合條件的檔案。":
            await write(result)
        else:
            match_count = len(result.splitlines())
            await write(f"工具完成：找到 {match_count} 個檔案")
    else:
        await write("工具完成。")


async def _print_event(event):
    event_type = event["type"]

    if event_type in {"assistant_text", "final_answer"}:
        await write(f"AI：{event['content']}")
    elif event_type == "tool_started":
        await _print_tool_started(event)
    elif event_type == "tool_finished":
        await _print_tool_finished(event)
    elif event_type == "error":
        await write(event["message"])


async def run(model, config):
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")
    messages = create_context(config["model_config"]["system_prompt"])
    tools = await load_tools()

    await write(
        f"\n已進入對話模式，目前模型：{model}\n"
        "輸入 exit 或 quit 返回指令頁。"
    )

    async with AsyncOpenAI(api_key=api_key, base_url=api_url) as client:
        while True:
            try:
                user_input = (await read("\n你：")).strip()
            except (EOFError, KeyboardInterrupt):
                await write("\n已返回指令頁。")
                return

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                await write("已返回指令頁。")
                return

            async for event in generate(
                client,
                model,
                messages,
                tools,
                user_input,
            ):
                await _print_event(event)
