import os

from arceus.agents.claude import run_claude
from arceus.agents.prompts import (
    investigation_prompt,
    implementation_prompt,
)
from arceus.tools.jira import get_jira_ticket
from arceus.tools.git import (
    create_worktree,
    get_diff,
    commit_changes,
    push_branch,
)
from arceus.tools.github import create_pull_request
from arceus.utils import generate_branch_keyword

from arceus.config import ARCEUS_PROD_BRANCH


ARCEUS_PR_BRANCH = os.getenv(
    "ARCEUS_PR_BRANCH",
    "staging-no-training",
)


def run_arceus(ticket_key: str) -> dict:

    # ========================================
    # 1. JIRA
    # ========================================

    print(
        f"🎫 Fetching Jira ticket {ticket_key}..."
    )

    ticket = get_jira_ticket.invoke({
        "ticket_key": ticket_key,
    })

    print(
        f"✅ {ticket['key']}: "
        f"{ticket['summary']}"
    )

    # ========================================
    # 2. BRANCH
    # ========================================

    base_branch = ARCEUS_PROD_BRANCH

    keyword = generate_branch_keyword(
        ticket["summary"]
    )

    print(
        f"🌿 Worktree base: {base_branch}"
    )

    print(
        f"🏷️ Generated keyword: {keyword}"
    )

    # ========================================
    # 3. WORKTREE
    # ========================================

    print(
        "🌳 Creating/reusing worktree..."
    )

    worktree = create_worktree.invoke({
        "ticket_key": ticket["key"],
        "base_branch": base_branch,
        "keyword": keyword,
    })

    worktree_path = worktree["worktree_path"]
    branch_name = worktree["branch_name"]

    print(
        f"📁 Worktree: {worktree_path}"
    )

    print(
        f"🌿 Branch: {branch_name}"
    )

    working_directory = (
        f"{worktree_path}/packages/sop-web"
    )

    # ========================================
    # 4. INVESTIGATION
    # ========================================

    print(
        "\n🔍 Claude investigation..."
    )

    investigation = run_claude(
        working_directory=working_directory,
        prompt=investigation_prompt(ticket),
        allow_writes=False,
    )

    print("\n")
    print("=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)

    print(investigation)

    # ========================================
    # 5. IMPLEMENTATION
    # ========================================

    print(
        "\n🤖 Claude implementing..."
    )

    implementation = run_claude(
        working_directory=working_directory,
        prompt=implementation_prompt(
            ticket=ticket,
            investigation=investigation,
        ),
        allow_writes=True,
    )

    print("\n")
    print("=" * 80)
    print("IMPLEMENTATION COMPLETE")
    print("=" * 80)

    print(implementation)

    # ========================================
    # 6. DIFF
    # ========================================

    print(
        "\n🔎 Reviewing diff..."
    )

    diff = get_diff.invoke(
        worktree_path
    )

    if not diff.strip():
        raise RuntimeError(
            "Claude completed but no changes "
            "were detected."
        )

    print("\n")
    print("=" * 80)
    print("DIFF")
    print("=" * 80)

    print(diff)

    # ========================================
    # 7. COMMIT
    # ========================================

    print(
        "\n💾 Committing changes..."
    )

    commit_message = (
        f"{ticket['key']}: "
        f"{ticket['summary']}"
    )

    commit_result = commit_changes.invoke({
        "worktree_path": worktree_path,
        "commit_message": commit_message,
    })

    print(commit_result)

    # ========================================
    # 8. PUSH
    # ========================================

    print(
        "\n🚀 Pushing branch..."
    )

    push_result = push_branch.invoke({
        "worktree_path": worktree_path,
        "branch_name": branch_name,
    })

    print(push_result)

    # ========================================
    # 9. PR
    # ========================================

    print(
        "\n🔀 Creating PR..."
    )

    pr_title = (
        f"[ephemeral] {ticket['summary']}"
    )

    pr_body = f"""
## Jira

{ticket["key"]}

{ticket["description"]}

## Implementation

{implementation}

## Investigation

{investigation}
"""

    pr_url = create_pull_request.invoke({
        "worktree_path": worktree_path,
        "title": pr_title,
        "base_branch": ARCEUS_PROD_BRANCH,
        "body": pr_body,
    })

    print("\n")
    print("=" * 80)
    print("PR CREATED")
    print("=" * 80)

    print(pr_url)

    return {
        "ticket_key": ticket["key"],
        "summary": ticket["summary"],
        "branch_name": branch_name,
        "worktree_path": worktree_path,
        "pr_url": pr_url,
        "base_branch": base_branch,
        "pr_base_branch": ARCEUS_PROD_BRANCH,
    }