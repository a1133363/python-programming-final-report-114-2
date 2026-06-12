import asyncio
import os
from pathlib import Path

import yaml

from dotenv import load_dotenv

from gateways.cli import run


CONFIG_PATH = Path(__file__).with_name("config.yaml")


async def read(prompt=""):
    return await asyncio.to_thread(input, prompt)


async def write(*values, sep=" ", end="\n"):
    await asyncio.to_thread(print, *values, sep=sep, end=end)


def _load_config_sync():
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    return config


async def main():
    await asyncio.to_thread(load_dotenv)
    config = await asyncio.to_thread(_load_config_sync)
    model = os.getenv("MODEL")

    await write(
        f"\n已啟動，目前模型：{model}\n"
        "可用指令：\n"
        "  chat    開啟 CLI 對話\n"
        "  models  查看並切換模型\n"
        "  exit    結束程式"
    )

    while True:
        try:
            command = (await read("\n指令：")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            await write("\n再見！")
            return

        if not command:
            continue

        if command == "chat":
            await run(model, config)
        elif command == "models":
            try:
                model = (await read(
                    "輸入模型 ID（直接 Enter 取消）："
                )).strip()
            except (EOFError, KeyboardInterrupt):
                await write("\n已取消切換模型。")
                continue

            if not model:
                await write("已取消切換模型。")
                continue

            await write(f"已切換模型：{model}")
        elif command == "help":
            await write(
                f"\n目前模型：{model}\n"
                "可用指令：chat、models、help、exit"
            )
        elif command in {"exit", "quit"}:
            await write("再見！")
            return
        else:
            await write(f"未知指令：{command}")


if __name__ == "__main__":
    asyncio.run(main())
