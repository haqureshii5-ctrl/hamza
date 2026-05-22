import asyncio
from typing import List

import openai

from .config import settings
from .logger import logger
from .models import TrendItem, GeneratedPost
from .utils import safe_truncate, format_hashtags

openai.api_key = settings.openai_api_key

PROMPT_TEMPLATE = """
You are a crypto social media writer. Create a concise, hype-but-realistic social media post for a trending crypto topic.
Rules:
- Keep the Twitter message under 280 characters.
- Use natural emojis and occasional CTA.
- Avoid financial advice, talk in general market tone.
- Include 3-5 relevant hashtags.
- Provide a strong hook.

Trend title: {title}
Trend source: {source}
Sentiment: {sentiment}
Extra context: {context}
"""

IMAGE_PROMPT_TEMPLATE = """
Generate a short image prompt for a dynamic crypto social media visual. Use words like digital chart, bull, bear, momentum, neon, altcoin, blockchain, trading desk.
Trend: {title}
Tone: {sentiment}
"""

class OpenAIGenerator:
    def __init__(self) -> None:
        self.model = settings.openai_model

    async def _create_completion(self, messages: List[dict[str, str]]) -> str:
        try:
            if hasattr(openai.ChatCompletion, "acreate"):
                response = await openai.ChatCompletion.acreate(model=self.model, messages=messages, max_tokens=180)
            else:
                response = await asyncio.to_thread(openai.ChatCompletion.create, model=self.model, messages=messages, max_tokens=180)
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.error("OpenAI generation failed: %s", exc)
            raise

    async def generate_post(self, trend: TrendItem) -> GeneratedPost:
        context = f"URL: {trend.url}" if trend.url else "No direct link provided."
        prompt = PROMPT_TEMPLATE.format(
            title=trend.title,
            source=trend.source,
            sentiment=trend.sentiment,
            context=context,
        )
        messages = [
            {"role": "system", "content": "You are a high-quality crypto social media copywriter."},
            {"role": "user", "content": prompt},
        ]

        result = await self._create_completion(messages)
        if "#" not in result:
            hashtag_text = format_hashtags([trend.topic, trend.source, "Crypto"])
            result = f"{result}\n\n{hashtag_text}"

        twitter_text = safe_truncate(result, 280)
        telegram_text = f"{result}\n\nSource: {trend.source.capitalize()}"
        hashtags = [tag for tag in result.split() if tag.startswith("#")]
        image_prompt = IMAGE_PROMPT_TEMPLATE.format(title=trend.title, sentiment=trend.sentiment)

        return GeneratedPost(
            trend=trend,
            twitter_text=twitter_text,
            telegram_text=telegram_text,
            hashtags=hashtags,
            image_prompt=image_prompt,
        )
