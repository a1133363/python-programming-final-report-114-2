import os
import yaml

from dotenv import load_dotenv

from gateways.cli import run


def main():
    load_dotenv()

    with open("config.yaml", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    model = os.getenv("MODEL")

    print(f"\n已啟動，目前模型：{model}")
    print("可用指令：")
    print("  chat    開啟 CLI 對話")
    print("  models  查看並切換模型")
    print("  exit    結束程式")

    while True:
        try:
            command = input("\n指令：").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            return

        if not command:
            continue

        if command == "chat":
            run(model, config)
        elif command == "models":

            try:
                model = input(
                    "輸入模型 ID（直接 Enter 取消）："
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n已取消切換模型。")
                continue

            if not model:
                print("已取消切換模型。")
                continue

            print(f"已切換模型：{model}")
        elif command == "help":
            print(f"\n目前模型：{model}")
            print("可用指令：chat、models、help、exit")
        elif command in {"exit", "quit"}:
            print("再見！")
            return
        else:
            print(f"未知指令：{command}")


if __name__ == "__main__":
    main()
