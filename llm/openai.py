import json

from tools.tool_call import run_tool


async def generate(client, model, context, tools, user_input):
    context.append({"role": "user", "content": user_input})

    for i in range(10):
        response = await client.chat.completions.create(
            model=model,
            messages=context,
            tools=tools,
            parallel_tool_calls=False,
        )

        message = response.choices[0].message
        context_message = {
            "role": "assistant",
            "content": message.content,
        }

        if not message.tool_calls:
            context.append(context_message)
            yield {
                "type": "final_answer",
                "content": message.content or "",
            }
            return

        tool_call = message.tool_calls[0]
        context_message["tool_calls"] = [{
            "id": tool_call.id,
            "type": tool_call.type,
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }]
        context.append(context_message)

        if message.content:
            yield {
                "type": "assistant_text",
                "content": message.content,
            }

        tool_name = tool_call.function.name

        if tool_call.function.arguments:
            arguments = json.loads(tool_call.function.arguments)
        else:
            arguments = {}

        yield {
            "type": "tool_started",
            "name": tool_name,
            "arguments": arguments,
        }

        result = await run_tool(tool_name, arguments)

        yield {
            "type": "tool_finished",
            "name": tool_name,
            "arguments": arguments,
            "result": result,
            "success": not result.startswith("工具執行失敗"),
        }

        context.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )

    limit_message = "工具調用次數已達上限，已停止此次請求。"
    context.append({"role": "assistant", "content": limit_message})
    yield {
        "type": "error",
        "message": limit_message,
    }
