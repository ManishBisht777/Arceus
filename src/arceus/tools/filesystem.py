from pathlib import Path

from langchain.tools import tool


def _validate_path(
    working_directory: str,
    relative_path: str,
) -> Path:
    root = Path(working_directory).resolve()

    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise RuntimeError(
            f"Path is outside working directory: {relative_path}"
        )

    return target


def create_filesystem_tools(
    working_directory: str,
):
    """
    Create filesystem tools scoped to one directory.
    """

    root = Path(working_directory).resolve()

    if not root.exists():
        raise RuntimeError(
            f"Working directory does not exist: {root}"
        )

    if not root.is_dir():
        raise RuntimeError(
            f"Working directory is not a directory: {root}"
        )

    @tool
    def list_files(relative_path: str = ".") -> list[str]:
        """List files and directories in the project."""

        directory = _validate_path(
            str(root),
            relative_path,
        )

        if not directory.exists():
            raise RuntimeError(
                f"Directory does not exist: {relative_path}"
            )

        if not directory.is_dir():
            raise RuntimeError(
                f"Not a directory: {relative_path}"
            )

        return sorted(
            item.name
            for item in directory.iterdir()
        )

    @tool
    def read_file(relative_path: str) -> str:
        """Read a file from the project."""

        file_path = _validate_path(
            str(root),
            relative_path,
        )

        if not file_path.exists():
            raise RuntimeError(
                f"File does not exist: {relative_path}"
            )

        if not file_path.is_file():
            raise RuntimeError(
                f"Not a file: {relative_path}"
            )

        return file_path.read_text()

    @tool
    def write_file(
        relative_path: str,
        content: str,
    ) -> str:
        """Write a file to the project."""

        file_path = _validate_path(
            str(root),
            relative_path,
        )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(content)

        return f"Updated {relative_path}"

    return [
        list_files,
        read_file,
        write_file,
    ]