def run_tool(tool_call):

    if tool_call.function.name == "say_hi":
        return f"TOOL CALL ({tool_call.function.name})\nTOOL: hi"