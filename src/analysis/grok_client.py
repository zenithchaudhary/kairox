import os
from dotenv import load_dotenv
from openai import OpenAI

# Load XAI_API_KEY from .env. Called here so this module works
# standalone, even if nothing else has loaded the .env file yet.
load_dotenv()

# xAI's API is OpenAI-compatible, so we reuse the OpenAI SDK pointed
# at xAI's base_url instead of a separate xAI-specific library.
GROK_MODEL = "grok-4.3"

_client = None


def get_client() -> OpenAI:
    """
    Singleton pattern, same approach as the embeddings model in
    src/ingestion/embeddings.py. Avoids re-creating the HTTP client
    on every call.
    """
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
    return _client