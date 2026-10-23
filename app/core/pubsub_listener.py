import asyncio
import json
import logging

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.connection_manager import manager

logger = logging.getLogger(__name__)


async def listen_for_events():
    while True:
        pubsub = None

        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )

            pubsub = client.pubsub()

            await pubsub.psubscribe("event:*:updates")

            logger.info("Redis Pub/Sub listener started...")

            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    channel = message["channel"]

                    event_id = int(
                        channel.split(":")[1]
                    )

                    data = json.loads(message["data"])

                    logger.info(
                        f"Received from {channel}: {data}"
                    )

                    await manager.broadcast(
                        event_id,
                        data,
                    )

        except asyncio.CancelledError:
            raise

        except Exception as e:
            logger.error(
                f"Redis Pub/Sub listener error: {e}"
            )

            await asyncio.sleep(2)

        finally:
            if pubsub:
                await pubsub.aclose()

            if "client" in locals():
                await client.aclose()