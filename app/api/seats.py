from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.event import Event
from app.models.seat import Seat
from app.schemas.seat import SeatOut

router = APIRouter(prefix="/events", tags=["Seats"])

@router.get("/{event_id}/seats", response_model=list[SeatOut])
def list_event_seats(event_id: int, db: Session = Depends(get_db)):
    if db.query(Event).filter(Event.id == event_id).first() is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db.query(Seat).filter(Seat.event_id == event_id).order_by(Seat.row_label, Seat.seat_number).all()
