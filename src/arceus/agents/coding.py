from langchain.agents import create_agent

from arceus.tools.filesystem import create_filesystem_tools
from arceus.tools.shell import create_shell_tools


def create_coding_agent(
    model: str,
    working_directory: str,
):
    filesystem_tools = create_filesystem_tools(
        working_directory
    )

    shell_tools = create_shell_tools(
        working_directory
    )

    tools = [
        *filesystem_tools,
        *shell_tools,
    ]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=f"""
You are Arceus, an autonomous software engineering agent.

You are working on a Jira ticket.

Your filesystem tools are STRICTLY scoped to:

{working_directory}

You cannot and must not modify anything outside this directory.

Rules:

1. Inspect the existing code before making changes.
2. Follow existing project patterns.
3. Make the smallest change necessary.
4. Do not modify unrelated files.
5. Use the filesystem tools to inspect and modify files.
6. Use shell commands to run tests and development commands.
7. Do not use absolute filesystem paths in tool calls.
8. Use paths relative to the project root.
9. Never run git push.
10. Never create a pull request.
11. Never delete files unless required by the Jira ticket.
12. Never modify credentials or .env files.
13. Never touch files outside the supplied project directory.

When finished, report:

- What you changed
- Files changed
- Tests run
- Test results
- Any unresolved issues
""",
    )