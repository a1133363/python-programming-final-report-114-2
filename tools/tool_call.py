import asyncio
from pathlib import Path


WORKSPACE_ROOT = Path.cwd().resolve()
SEARCH_RESULT_LIMIT = 100


def _resolve_workspace_path(path):
    resolved_path = (WORKSPACE_ROOT / path).resolve()

    try:
        resolved_path.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise ValueError("路徑不可超出專案目錄。") from error

    return resolved_path


def _read_file_sync(path):
    file_path = _resolve_workspace_path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"找不到檔案：{path}")

    return file_path.read_text(encoding="utf-8")


async def read_file(path):
    return await asyncio.to_thread(_read_file_sync, path)


def _search_files_sync(pattern):
    if not pattern.strip():
        raise ValueError("搜尋條件不可為空白。")

    pattern_path = Path(pattern)

    if pattern_path.is_absolute() or ".." in pattern_path.parts:
        raise ValueError("搜尋條件不可超出專案目錄。")

    matches = []

    for file_path in WORKSPACE_ROOT.rglob(pattern):
        relative_path = file_path.relative_to(WORKSPACE_ROOT)

        if file_path.is_file() and ".git" not in relative_path.parts:
            matches.append(relative_path.as_posix())

        if len(matches) >= SEARCH_RESULT_LIMIT:
            break

    if not matches:
        return "找不到符合條件的檔案。"

    return "\n".join(sorted(matches))


async def search_files(pattern):
    return await asyncio.to_thread(_search_files_sync, pattern)


def _create_file_sync(path, content):
    file_path = _resolve_workspace_path(path)

    if file_path.exists():
        raise FileExistsError(f"檔案已存在：{path}")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("x", encoding="utf-8") as new_file:
            new_file.write(content)
    except FileExistsError as error:
        raise FileExistsError(f"檔案已存在：{path}") from error

    return f"已新增檔案：{file_path.relative_to(WORKSPACE_ROOT).as_posix()}"


async def create_file(path, content):
    return await asyncio.to_thread(_create_file_sync, path, content)


TOOL_HANDLERS = {
    "read_file": read_file,
    "search_files": search_files,
    "create_file": create_file,
}


async def run_tool(tool_name, arguments):
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:
        return f"工具執行失敗：不支援的工具：{tool_name}"

    try:
        result = await handler(**arguments)
    except (OSError, TypeError, UnicodeError, ValueError) as error:
        return f"工具執行失敗：{error}"

    return str(result)
