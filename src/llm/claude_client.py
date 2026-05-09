import os
import anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

FALLBACK_MESSAGE = (
    "[Report generation unavailable. "
    "Please check that ANTHROPIC_API_KEY is set in your .env file and try again.]"
)


def generate_report(prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("MODEL_ID", "claude-haiku-4-5")

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
