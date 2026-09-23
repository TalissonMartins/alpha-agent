import os

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://alphaagent:alphaagent@localhost:5432/alphaagent",
    )


def should_persist_database() -> bool:
    return os.getenv("PERSIST_DATABASE", "false").lower() in {"1", "true", "yes"}
