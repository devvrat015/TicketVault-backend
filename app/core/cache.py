import json
from typing import Any

from app.core.redis_client import redis_client


def get_cache(key: str):
    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def set_cache(key: str, value: Any, ttl: int = 60):
    redis_client.setex(
        key,
        ttl,
        json.dumps(value),
    )


def delete_cache(key: str):
    redis_client.delete(key)


def get_events_list_version() -> str:
    return redis_client.get("events:list:version") or "0"


def bump_events_list_version() -> None:
    redis_client.incr("events:list:version")