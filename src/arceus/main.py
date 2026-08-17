import sys

from dotenv import load_dotenv

from arceus.workflow import run_arceus


load_dotenv()


def main():

    if len(sys.argv) < 2:
        raise RuntimeError(
            "Usage: uv run python -m arceus.main DTP-3861"
        )

    ticket_key = sys.argv[1]

    result = run_arceus(ticket_key)

    print("\n")
    print("=" * 80)
    print("ARCEUS COMPLETE")
    print("=" * 80)

    print(f"Ticket: {result['ticket_key']}")
    print(f"Branch: {result['branch_name']}")
    print(f"PR: {result['pr_url']}")


if __name__ == "__main__":
    main()