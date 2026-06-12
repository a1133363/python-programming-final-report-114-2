import os

from llm.openai import generate
from openai import OpenAI

def run(model, config):
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")
    
    client = OpenAI(api_key=api_key, base_url=api_url)
    messages = []

    messages.append({"role": "system", "content": config["model_config"]["system_prompt"]})

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

        messages.append({"role": "user", "content": user_input})
        assistant_message = generate(client, model, messages)
        messages.append({"role": "assistant", "content": assistant_message})
        print(f"AI：{assistant_message}")
