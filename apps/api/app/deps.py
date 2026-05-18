from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Protocol

from anthropic import AsyncAnthropic

from app.config import get_settings


class AnthropicClient(Protocol):
    @property
    def messages(self) -> object:  # narrowed at use site
        ...


@lru_cache
def _real_client() -> AsyncAnthropic:
    return AsyncAnthropic(api_key=get_settings().anthropic_api_key)


async def get_anthropic_client() -> AsyncIterator[AnthropicClient]:
    yield _real_client()
