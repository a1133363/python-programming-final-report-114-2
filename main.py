import asyncio
import os
from pathlib import Path

import yaml

from dotenv import load_dotenv

from gateways.cli import run


CONFIG_PATH = Path(__file__).with_name("config.yaml")


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
                await run(model, config)
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