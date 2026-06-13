import asyncio
import os
import random
from pathlib import Path

import yaml

from dotenv import load_dotenv

from gateways.cli import run


CONFIG_PATH = Path(__file__).with_name("config.yaml")
sessions = []


def create_session(gateway_name, system_prompt):
    while True:
        random_id = random.randint(1_000_000_000, 9_999_999_999)
        session_id = f"{gateway_name}:{random_id}"

        if not any(
            session["session_id"] == session_id
            for session in sessions
        ):
            break

    session = {
        "session_id": session_id,
        "context": [
            {
                "role": "system",
                "content": system_prompt,
            }
        ],
    }
    sessions.append(session)
    return session_id


def get_context(session_id):
    for session in sessions:
        if session["session_id"] == session_id:
            return session["context"]

    return f"找不到 session：{session_id}"


async def main():
    load_dotenv()
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    model = os.getenv("MODEL")

    print(
        f"\n已啟動，目前模型：{model}\n"
        "可用指令：\n"
        "  chat    開啟 CLI 對話\n"
        "  models  查看並切換模型\n"
        "  exit    結束程式"
    )

    while True:
        command = (await asyncio.to_thread(input, "\n指令：")).strip().lower()

        match command:
            case "":
                continue
            case "chat":
                session_id = create_session("cli", config["model_config"]["system_prompt"])
                await run(model, session_id, get_context(session_id))
            case "models":
                model = (await asyncio.to_thread(input, "輸入模型 ID（直接 Enter 取消）：")).strip()
                if not model:
                    print("已取消切換模型。")
                else:
                    print(f"已切換模型：{model}")
                continue
            case "exit" | "quit":
                print("再見！")
                return
            case _:
                print(f"未知指令：{command}")

if __name__ == "__main__":
    asyncio.run(main())
