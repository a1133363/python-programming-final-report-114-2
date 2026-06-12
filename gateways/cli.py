import os

from openai import OpenAI

from llm.openai import create_context, generate

TOOL_LABELS = {
    "read_file": "查看檔案",
    "search_files": "搜尋檔案",
    "create_file": "新增檔案",
}


def _print_tool_started(event):
    tool_name = event["name"]
    arguments = event["arguments"]
    label = TOOL_LABELS.get(tool_name, tool_name)
    target = arguments.get("path") or arguments.get("pattern")
    target_text = f"：{target}" if target else ""
    print(f"AI 使用工具：{label}{target_text}")


def _print_tool_finished(event):
    tool_name = event["name"]
    result = event["result"]

    if not event["success"]:
        print(result)
    elif tool_name == "search_files":
        if result == "找不到符合條件的檔案。":
            print(result)
        else:
            match_count = len(result.splitlines())
            print(f"工具完成：找到 {match_count} 個檔案")
    else:
        print("工具完成。")


def _print_event(event):
    event_type = event["type"]

    if event_type in {"assistant_text", "final_answer"}:
        print(f"AI：{event['content']}")
    elif event_type == "tool_started":
        _print_tool_started(event)
    elif event_type == "tool_finished":
        _print_tool_finished(event)
    elif event_type == "error":
        print(event["message"])


def run(model, config):
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")
    
    client = OpenAI(api_key=api_key, base_url=api_url)
    messages = create_context(config["model_config"]["system_prompt"])

    print(f"\n已進入對話模式，目前模型：{model}")
    print("輸入 exit 或 quit 返回指令頁。")

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已返回指令頁。")
            return

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("已返回指令頁。")
            return

        for event in generate(client, model, messages, user_input):
            _print_event(event)
