import json
from pathlib import Path

from openai import OpenAIError
from tools.tool_call import run_tool


TOOLS_PATH = Path(__file__).resolve().parent.parent / "tools" / "tools.json"
MAX_TOOL_ROUNDS = 10

with TOOLS_PATH.open(encoding="utf-8") as tools_file:
    tools = json.load(tools_file)


def create_context(system_prompt):
    return [{"role": "system", "content": system_prompt}]


def _assistant_message_to_context(message):
    context_message = {
        "role": "assistant",
        "content": message.content,
    }

    if message.tool_calls:
        context_message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in message.tool_calls
        ]

    return context_message


def _parse_tool_arguments(tool_call):
    try:
        return json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        return {}


def generate(client, model, messages, user_input):
    messages.append({"role": "user", "content": user_input})

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
            )
        except OpenAIError as error:
            yield {
                "type": "error",
                "message": f"OpenAI API 呼叫失敗：{error}",
            }
            return

        message = response.choices[0].message
        messages.append(_assistant_message_to_context(message))

        if not message.tool_calls:
            yield {
                "type": "final_answer",
                "content": message.content or "",
            }
            return

        if message.content:
            yield {
                "type": "assistant_text",
                "content": message.content,
            }

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = _parse_tool_arguments(tool_call)

            yield {
                "type": "tool_started",
                "name": tool_name,
                "arguments": arguments,
            }

            result = run_tool(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

            yield {
                "type": "tool_finished",
                "name": tool_name,
                "arguments": arguments,
                "result": result,
                "success": not result.startswith("工具執行失敗"),
            }

    limit_message = "工具調用次數已達上限，已停止此次請求。"
    messages.append({"role": "assistant", "content": limit_message})
    yield {
        "type": "error",
        "message": limit_message,
    }
