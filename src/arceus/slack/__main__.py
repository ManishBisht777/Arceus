from dotenv import load_dotenv
from arceus.slack.app import start


load_dotenv()


if __name__ == "__main__":
    start()