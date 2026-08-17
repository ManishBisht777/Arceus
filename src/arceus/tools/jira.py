import os

import requests
from langchain.tools import tool


def _get_jira_auth():
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not email or not api_token:
        raise RuntimeError(
            "JIRA_EMAIL and JIRA_API_TOKEN must be set"
        )

    return email, api_token


def _extract_adf_text(node):
    """Extract readable text from Atlassian Document Format."""

    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")

        return " ".join(
            _extract_adf_text(child)
            for child in node.get("content", [])
        )

    if isinstance(node, list):
        return " ".join(_extract_adf_text(item) for item in node)

    return ""


@tool
def get_jira_ticket(ticket_key: str) -> dict:
    """Fetch a Jira ticket including summary, description, status and comments."""

    base_url = os.getenv("JIRA_BASE_URL")

    if not base_url:
        raise RuntimeError("JIRA_BASE_URL must be set")

    email, api_token = _get_jira_auth()

    issue_url = f"{base_url}/rest/api/3/issue/{ticket_key}"

    response = requests.get(
        issue_url,
        auth=(email, api_token),
        headers={
            "Accept": "application/json",
        },
        params={
            "fields": "summary,description,status,comment",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    fields = data["fields"]

    description = _extract_adf_text(
        fields.get("description")
    )

    comments = []

    for comment in fields.get("comment", {}).get("comments", []):
        comments.append(
            {
                "author": comment.get("author", {}).get(
                    "displayName"
                ),
                "body": _extract_adf_text(
                    comment.get("body")
                ),
                "created": comment.get("created"),
            }
        )

    return {
        "key": ticket_key,
        "summary": fields.get("summary"),
        "description": description,
        "status": fields.get("status", {}).get("name"),
        "comments": comments,
    }