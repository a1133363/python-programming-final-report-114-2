import json

with open("tools/tools.json", encoding="utf-8") as tools_file:
    tools = json.load(tools_file)


def generate(client, model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )

    message = response.choices[0].message
    tool_call = message.tool_calls[0] if message.tool_calls else None

    if tool_call and tool_call.function.name == "say_hi":
        return "TOOL CALL\nTOOL: hi"

    return message.content or ""
