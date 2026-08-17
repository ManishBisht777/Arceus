import subprocess


def run_claude(
    working_directory: str,
    prompt: str,
    allow_writes: bool = False,
) -> str:

    command = [
        "claude",
        "-p",
        prompt,
    ]

    if allow_writes:
        command.extend([
            "--permission-mode",
            "acceptEdits",
        ])

    result = subprocess.run(
        command,
        cwd=working_directory,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Claude Code failed:\n{result.stderr}"
        )

    return result.stdout