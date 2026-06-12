import asyncio
import json
from functools import cache
from pathlib import Path

from openai import OpenAIError
from tools.tool_call import run_tool


TOOLS_PATH = Path(__file__).resolve().parent.parent / "tools" / "tools.json"
MAX_TOOL_ROUNDS = 10


@cache
def _load_tools_sync():
    with TOOLS_PATH.open(encoding="utf-8") as tools_file:
        return json.load(tools_file)


async def load_tools():
    return await asyncio.to_thread(_load_tools_sync)


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


async def _execute_tool(index, tool_name, arguments):
    result = await run_tool(tool_name, arguments)
    return index, result


async def generate(client, model, messages, tools, user_input):
    messages.append({"role": "user", "content": user_input})

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = await client.chat.completions.create(
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

        tool_requests = []

        for index, tool_call in enumerate(message.tool_calls):
            tool_name = tool_call.function.name
            arguments = _parse_tool_arguments(tool_call)
            tool_requests.append((index, tool_call, tool_name, arguments))

            yield {
                "type": "tool_started",
                "name": tool_name,
                "arguments": arguments,
            }

        tasks = [
            asyncio.create_task(
                _execute_tool(index, tool_name, arguments)
            )
            for index, _, tool_name, arguments in tool_requests
        ]
        results = [None] * len(tasks)

        try:
            for completed_task in asyncio.as_completed(tasks):
                index, result = await completed_task
                results[index] = result
                _, _, tool_name, arguments = tool_requests[index]

                yield {
                    "type": "tool_finished",
                    "name": tool_name,
                    "arguments": arguments,
                    "result": result,
                    "success": not result.startswith("工具執行失敗"),
                }
        finally:
            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        for (_, tool_call, _, _), result in zip(
            tool_requests,
            results,
            strict=True,
        ):
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    limit_message = "工具調用次數已達上限，已停止此次請求。"
    messages.append({"role": "assistant", "content": limit_message})
    yield {
        "type": "error",
        "message": limit_message,
    }
