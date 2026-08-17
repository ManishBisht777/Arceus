from arceus.config import ARCEUS_PROD_BRANCH


def resolve_branch(state):
    branch = (
        state["requested_branch"]
        or ARCEUS_PROD_BRANCH
    )

    return {
        "base_branch": branch,
    }