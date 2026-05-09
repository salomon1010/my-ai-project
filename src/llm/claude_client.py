import os
import anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

FALLBACK_MESSAGE = (
    "[Report generation unavailable. "
    "Please check that ANTHROPIC_API_KEY is set in your .env file or Streamlit secrets and try again.]"
)


def _get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets (cloud) or environment variables (local)."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


def generate_report(prompt: str) -> str:
    api_key = _get_secret("ANTHROPIC_API_KEY")
    model = _get_secret("MODEL_ID") or "claude-haiku-4-5"

    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — returning fallback message")
        return FALLBACK_MESSAGE

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return FALLBACK_MESSAGE
