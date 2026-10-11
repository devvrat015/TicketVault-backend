from app.models.enums import SeatStatus
from pydantic import BaseModel, ConfigDict

class SeatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    row_label: str
    seat_number: int
    price: int
    status: SeatStatus
    event_id: int
    booking_id: int | None
