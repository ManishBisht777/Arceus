from langgraph.graph import StateGraph, START, END

from arceus.graph.state import AgentState
from arceus.tools.jira import get_jira_ticket


def fetch_ticket(state: AgentState):
    ticket = get_jira_ticket.invoke(
        {
            "ticket_key": state["ticket_key"]
        }
    )

    return {
        "ticket": ticket
    }


builder = StateGraph(AgentState)

builder.add_node(
    "fetch_ticket",
    fetch_ticket,
)

builder.add_edge(
    START,
    "fetch_ticket",
)

builder.add_edge(
    "fetch_ticket",
    END,
)

app = builder.compile()