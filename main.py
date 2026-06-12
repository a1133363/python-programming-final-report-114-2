import os

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    load_dotenv()

    model = os.getenv("MODEL")
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")

    if not model:
        print("缺少 MODEL，請先建立 .env 並完成設定。")
        return

    if not api_key:
        print("缺少 API_KEY 或 OPENAI_API_KEY，請先完成 .env 設定。")
        return

    client = OpenAI(api_key=api_key, base_url=api_url)
    messages = []

    print(f"已啟動，目前模型：{model}")
    print("輸入 exit 或 quit 結束對話。")

    while True:
        try:
            user_input = input("\n你:").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("再見！")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            assistant_message = response.choices[0].message.content or ""
        except Exception as error:
            messages.pop()
            print(f"發生錯誤：{error}")
            continue

        messages.append({"role": "assistant", "content": assistant_message})
        print(f"AI：{assistant_message}")


if __name__ == "__main__":
    main()
