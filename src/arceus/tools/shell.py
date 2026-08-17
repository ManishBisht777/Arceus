import subprocess
from pathlib import Path

from langchain.tools import tool


def create_shell_tools(
    working_directory: str,
):
    root = Path(working_directory).resolve()

    if not root.exists():
        raise RuntimeError(
            f"Working directory does not exist: {root}"
        )

    @tool
    def run_command(command: str) -> str:
        """
        Run a shell command from the project directory.
        """

        result = subprocess.run(
            command,
            cwd=root,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
        )

        output = result.stdout

        if result.stderr:
            output += "\nSTDERR:\n"
            output += result.stderr

        output += f"\nEXIT CODE: {result.returncode}"

        return output

    return [run_command]