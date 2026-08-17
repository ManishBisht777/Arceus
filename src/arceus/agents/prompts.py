def investigation_prompt(ticket: dict) -> str:

    comments = "\n".join(
        f"- {comment['author']}: {comment['body']}"
        for comment in ticket.get("comments", [])
    )

    return f"""
You are investigating Jira ticket {ticket["key"]}.

Repository:
sop-fe

IMPORTANT SCOPE:

Only inspect:

packages/sop-web

Do NOT modify any files.

Do NOT run git commands.

Do NOT create a plan file.

Do NOT create or modify files under ~/.claude/plans/.

Your job is to investigate the Jira ticket and return an
implementation plan directly in your response.

JIRA CONTEXT
============

Key:
{ticket["key"]}

Summary:
{ticket["summary"]}

Status:
{ticket["status"]}

Description:
{ticket["description"]}

Comments:
{comments}

INVESTIGATION
=============

1. Inspect packages/sop-web.
2. Identify relevant files.
3. Read those files.
4. Trace the relevant code flow.
5. Understand the existing implementation.
6. Identify the root cause.
7. Determine the smallest appropriate fix.
8. Identify tests that should be added or updated.

Return ONLY this structure:

## Relevant Files

List the files you inspected and why they matter.

## Current Implementation

Explain the existing code flow.

## Problem

Explain the root cause of the Jira issue.

## Proposed Solution

Explain the exact changes required.

## Tests

Explain the tests that should be run or added.

## Risks

Mention any potential regression risks.

Again:

DO NOT MODIFY FILES.
DO NOT RUN GIT COMMANDS.
DO NOT CREATE A PLAN FILE.
"""



def implementation_prompt(
    ticket: dict,
    investigation: str,
) -> str:

    comments = "\n".join(
        f"- {comment['author']}: {comment['body']}"
        for comment in ticket.get("comments", [])
    )

    return f"""
You are the coding agent for Jira ticket {ticket["key"]}.

Repository:
sop-fe

IMPORTANT:

You are working inside an isolated git worktree.

Only modify:

packages/sop-web

Never modify files outside packages/sop-web.

JIRA TICKET
===========

Key:
{ticket["key"]}

Summary:
{ticket["summary"]}

Status:
{ticket["status"]}

Description:
{ticket["description"]}

Comments:
{comments}

INVESTIGATION
=============

{investigation}

IMPLEMENTATION
==============

Implement the proposed solution.

Rules:

1. Inspect the relevant code before modifying it.
2. Follow existing project patterns.
3. Make the smallest change necessary.
4. Do not refactor unrelated code.
5. Add/update tests when appropriate.
6. Run relevant tests.
7. Fix failures caused by your changes.
8. Review your final implementation.

Git rules:

- Do NOT commit.
- Do NOT push.
- Do NOT create a PR.
- Arceus handles Git operations after you finish.

At the end return:

## Implementation Summary

## Files Changed

## Tests Run

## Test Results

## Remaining Issues
"""