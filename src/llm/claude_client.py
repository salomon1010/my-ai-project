import os
import anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets (cloud) or environment variables (local)."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


def generate_report(prompt: str) -> str:
    api_key = _get_secret("ANTHROPIC_API_KEY")
    model = _get_secret("MODEL_ID") or "claude-haiku-4-5"

    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set")
        return "[ERROR: ANTHROPIC_API_KEY is missing. Go to Streamlit Cloud → App Settings → Secrets and add your key.]"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    except anthropic.AuthenticationError:
        return "[ERROR: Invalid API key. Check ANTHROPIC_API_KEY in Streamlit Secrets.]"

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return f"[ERROR: Claude API call failed — {e}]"
