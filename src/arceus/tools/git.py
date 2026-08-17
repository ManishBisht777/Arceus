import subprocess
from pathlib import Path
from langchain.tools import tool
from arceus.config import ARCEUS_REPO_PATH


import subprocess
from pathlib import Path

from langchain.tools import tool

from arceus.config import ARCEUS_REPO_PATH


def _run_git(
    args: list[str],
    cwd: Path,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed:\n"
            f"git {' '.join(args)}\n\n"
            f"{result.stderr}"
        )

    return result


@tool
def create_worktree(
    ticket_key: str,
    base_branch: str,
    keyword: str,
) -> dict:
    """
    Create or reuse a worktree for a Jira ticket.

    Always fetches the latest origin/base branch first.
    Existing worktrees are updated/rebased onto the latest base branch.
    """

    repo = Path(ARCEUS_REPO_PATH)

    if not repo.exists():
        raise RuntimeError(
            f"Repository does not exist: {repo}"
        )

    # Verify repository
    _run_git(
        ["rev-parse", "--show-toplevel"],
        repo,
    )

    branch_name = f"{ticket_key}-{keyword}"

    worktree_root = repo.parent / "worktrees"
    worktree_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    worktree_path = worktree_root / branch_name

    # ----------------------------------------
    # ALWAYS FETCH LATEST REMOTE
    # ----------------------------------------

    print("📡 Fetching latest branches...")

    _run_git(
        ["fetch", "origin"],
        repo,
    )

    base_ref = f"origin/{base_branch}"

    # ----------------------------------------
    # CHECK EXISTING WORKTREE
    # ----------------------------------------

    if worktree_path.exists():

        print(
            f"♻️ Reusing existing worktree: "
            f"{worktree_path}"
        )

        # Verify Git knows about this worktree.
        worktree_list = _run_git(
            ["worktree", "list", "--porcelain"],
            repo,
        )

        if str(worktree_path) not in worktree_list.stdout:
            raise RuntimeError(
                f"Directory exists but is not a "
                f"registered Git worktree:\n"
                f"{worktree_path}"
            )

        # ----------------------------------------
        # CHECK FOR LOCAL CHANGES
        # ----------------------------------------

        status = _run_git(
            ["status", "--porcelain"],
            worktree_path,
        )

        if status.stdout.strip():
            raise RuntimeError(
                "Existing worktree contains uncommitted "
                "changes.\n\n"
                "Arceus will not rebase or reset it because "
                "that could destroy Claude's work.\n\n"
                f"Worktree: {worktree_path}"
            )

        # ----------------------------------------
        # MAKE SURE WE ARE ON EXPECTED BRANCH
        # ----------------------------------------

        current_branch = _run_git(
            ["branch", "--show-current"],
            worktree_path,
        ).stdout.strip()

        if current_branch != branch_name:
            raise RuntimeError(
                f"Worktree is on unexpected branch.\n"
                f"Expected: {branch_name}\n"
                f"Found: {current_branch}"
            )

        # ----------------------------------------
        # UPDATE EXISTING BRANCH
        # ----------------------------------------

        print(
            f"🔄 Rebasing {branch_name} "
            f"onto latest {base_ref}..."
        )

        _run_git(
            [
                "rebase",
                base_ref,
            ],
            worktree_path,
        )

        print(
            f"✅ Worktree updated from "
            f"{base_ref}"
        )

        return {
            "branch_name": branch_name,
            "worktree_path": str(worktree_path),
            "base_branch": base_branch,
            "reused": True,
            "updated_from": base_ref,
        }

    # ----------------------------------------
    # CREATE NEW WORKTREE
    # ----------------------------------------

    print(
        f"🌳 Creating worktree from {base_ref}..."
    )

    _run_git(
        [
            "worktree",
            "add",
            str(worktree_path),
            "-b",
            branch_name,
            base_ref,
        ],
        repo,
    )

    print(
        f"✅ Created {branch_name} "
        f"from {base_ref}"
    )

    return {
        "branch_name": branch_name,
        "worktree_path": str(worktree_path),
        "base_branch": base_branch,
        "reused": False,
        "updated_from": base_ref,
    }


@tool
def get_diff(worktree_path: str) -> str:
    """Get the current diff for the sop-web package."""

    result = subprocess.run(
        [
            "git",
            "diff",
            "--",
            "packages/sop-web",
        ],
        cwd=worktree_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout


@tool
def commit_changes(
    worktree_path: str,
    commit_message: str,
) -> str:
    """Commit changes in the worktree."""

    subprocess.run(
        [
            "git",
            "add",
            "--",
            "packages/sop-web",
        ],
        cwd=worktree_path,
        check=True,
    )

    result = subprocess.run(
        [
            "git",
            "commit",
              "--no-verify",
            "-m",
            commit_message,
        ],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
      raise RuntimeError(
        f"Failed to commit:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    return result.stdout


@tool
def push_branch(
    worktree_path: str,
    branch_name: str,
) -> str:
    """Push the current branch to origin."""

    result = subprocess.run(
        [
            "git",
            "push",
            "-u",
            "origin",
            branch_name,
        ],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to push branch:\n{result.stderr}"
        )

    return result.stdout