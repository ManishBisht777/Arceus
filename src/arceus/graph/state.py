from typing import TypedDict


class JiraTicket(TypedDict):
    key: str
    summary: str
    description: str
    status: str
    comments: list[dict]


class AgentState(TypedDict):
    # Request
    ticket_key: str
    requested_branch: str | None

    # Jira
    ticket: JiraTicket

    # Resolved Git configuration
    base_branch: str

    # Worktree
    worktree_path: str
    branch_name: str

    # Implementation
    implementation_summary: str
    test_result: str
    diff: str

    # Approval
    diff_approved: bool
    pr_approved: bool

    # PR
    pr_url: str | None