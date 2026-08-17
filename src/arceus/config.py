import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ARCEUS_REPO_PATH = os.getenv("ARCEUS_REPO_PATH")
ARCEUS_WORKING_DIR = os.getenv("ARCEUS_WORKING_DIR")
ARCEUS_PROD_BRANCH = os.getenv(
    "ARCEUS_PROD_BRANCH",
    "main",
)

def get_working_directory(worktree_path: str) -> str:
    working_dir = (
        Path(worktree_path)
        / ARCEUS_WORKING_DIR
    )

    if not working_dir.exists():
        raise RuntimeError(
            f"Working directory does not exist: "
            f"{working_dir}"
        )

    return str(working_dir)

if not ARCEUS_REPO_PATH:
    raise RuntimeError(
        "ARCEUS_REPO_PATH is not configured"
    )

if not ARCEUS_WORKING_DIR:
    raise RuntimeError(
        "ARCEUS_WORKING_DIR is not configured"
    )