import os
import re
import threading

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from arceus.workflow import run_arceus


TICKET_PATTERN = re.compile(
    r"\b[A-Z][A-Z0-9]+-\d+\b"
)


app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


def extract_ticket_key(text: str) -> str | None:
    match = TICKET_PATTERN.search(text)

    if not match:
        return None

    return match.group(0)


def run_ticket(
    ticket_key: str,
    channel_id: str,
    thread_ts: str,
):
    try:
        result = run_arceus(ticket_key)

        app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=(
                f"✅ Arceus completed `{ticket_key}`\n\n"
                f"🌿 Branch: `{result['branch_name']}`\n"
                f"🔀 PR: {result['pr_url']}"
            ),
        )

    except Exception as error:

        app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=(
                f"❌ Arceus failed for `{ticket_key}`\n\n"
                f"```{error}```"
            ),
        )


@app.event("app_mention")
def handle_mention(event, say):

    text = event.get("text", "")

    ticket_key = extract_ticket_key(text)

    if not ticket_key:
        say(
            "I couldn't find a Jira ticket key. "
            "Try something like `DTP-3861`."
        )
        return

    thread_ts = event.get(
        "thread_ts",
        event["ts"],
    )

    say(
        f"🔍 Starting Arceus for `{ticket_key}`...\n"
        f"I'll investigate, implement, test and raise the PR."
    )

    thread = threading.Thread(
        target=run_ticket,
        args=(
            ticket_key,
            event["channel"],
            thread_ts,
        ),
        daemon=True,
    )

    thread.start()


def start():
    handler = SocketModeHandler(
        app,
        os.environ["SLACK_APP_TOKEN"],
    )

    handler.start()