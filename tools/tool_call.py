from pathlib import Path


async def read_file(path):
    workspace_root = Path.cwd().resolve()
    file_path = (workspace_root / path).resolve()

    try:
        file_path.relative_to(workspace_root)
    except ValueError as error:
        raise ValueError("路徑不可超出專案目錄。") from error

    if not file_path.is_file():
        raise FileNotFoundError(f"找不到檔案：{path}")

    return file_path.read_text(encoding="utf-8")


async def search_files(pattern):
    workspace_root = Path.cwd().resolve()
    pattern_path = Path(pattern)
    matches = []

    if not pattern.strip():
        raise ValueError("搜尋條件不可為空白。")

    if pattern_path.is_absolute() or ".." in pattern_path.parts:
        raise ValueError("搜尋條件不可超出專案目錄。")

    for file_path in workspace_root.rglob(pattern):
        relative_path = file_path.relative_to(workspace_root)

        if file_path.is_file() and ".git" not in relative_path.parts:
            matches.append(relative_path.as_posix())

        if len(matches) >= 100:
            break

    if not matches:
        return "找不到符合條件的檔案。"

    return "\n".join(sorted(matches))


async def create_file(path, content):
    workspace_root = Path.cwd().resolve()
    file_path = (workspace_root / path).resolve()

    try:
        file_path.relative_to(workspace_root)
    except ValueError as error:
        raise ValueError("路徑不可超出專案目錄。") from error

    if file_path.exists():
        raise FileExistsError(f"檔案已存在：{path}")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("x", encoding="utf-8") as new_file:
            new_file.write(content)
    except FileExistsError as error:
        raise FileExistsError(f"檔案已存在：{path}") from error

    return f"已新增檔案：{file_path.relative_to(workspace_root).as_posix()}"


async def run_tool(tool_name, arguments):
    try:
        if tool_name == "read_file":
            result = await read_file(**arguments)
        elif tool_name == "search_files":
            result = await search_files(**arguments)
        elif tool_name == "create_file":
            result = await create_file(**arguments)
        else:
            return f"工具執行失敗：不支援的工具：{tool_name}"
    except (OSError, TypeError, UnicodeError, ValueError) as error:
        return f"工具執行失敗：{error}"

    return str(result)
