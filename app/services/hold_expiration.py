import asyncio
import logging
import time

from app.core.redis_client import redis_client, publish_event
from app.core.database import SessionLocal
from app.models.enums import SeatStatus
from app.models.seat import Seat

logger = logging.getLogger(__name__)


async def release_expired_seat(seat_id: int):
    db = SessionLocal()

    try:
        seat = (
            db.query(Seat)
            .filter(Seat.id == seat_id)
            .with_for_update()
            .first()
        )

        if not seat:
            return

        if seat.status != SeatStatus.HELD:
            return

        event_id = seat.event_id

        seat.status = SeatStatus.AVAILABLE
        db.commit()

        await publish_event(
            f"event:{event_id}:updates",
            {
                "seat_id": seat_id,
                "status": "available",
            },
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


async def listen_for_expired_holds():
    logger.info("Hold expiration checker started")

    try:
        while True:
            now = time.time()

            expired_seats = redis_client.zrangebyscore(
                "seat_holds",
                "-inf",
                now,
            )


            for seat_id in expired_seats:
                seat_id = int(seat_id)

                logger.info(f"Hold expired: seat_id={seat_id}")

                await release_expired_seat(seat_id)

                redis_client.zrem(
                    "seat_holds",
                    str(seat_id),
                )

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        raise