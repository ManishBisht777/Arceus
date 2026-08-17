import subprocess

from langchain.tools import tool


@tool
def create_pull_request(
    worktree_path: str,
    title: str,
    base_branch: str,
    body: str,
) -> str:
    """Create a GitHub pull request."""

    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            base_branch,
            "--title",
            title,
            "--body",
            body,
        ],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to create PR:\n{result.stderr}"
        )

    return result.stdout.strip()