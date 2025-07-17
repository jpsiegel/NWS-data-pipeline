from typing import Tuple
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.weather_observation import WeatherObservation

router = APIRouter()

@router.get("/metrics/avg_temperature_last_week")
def avg_temp_last_week(db: Session = Depends(get_db)):
    """
    Calculate the average observed temperature (°C) for the previous week (Mon–Sun).
    """
    start_dt, end_dt = get_last_week_range()

    result = db.query(func.avg(WeatherObservation.temperature))\
        .filter(
            WeatherObservation.timestamp >= start_dt,
            WeatherObservation.timestamp < end_dt
        ).scalar()

    return {
        "last_week_monday": start_dt.isoformat(),
        "last_week_sunday": end_dt.isoformat(),
        "average_temperature": f"{round(result, 2)} °C" if result else None
    }

def get_last_week_range() -> Tuple[datetime, datetime]:
    """
    Returns the datetime range for the previous week (Monday to Sunday).

    Returns:
        Tuple[datetime, datetime]: A pair of datetimes representing the start (inclusive)
        and end (exclusive) of the previous week in UTC.
    """
    today = datetime.utcnow().date()
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)

    start_dt = datetime.combine(last_monday, datetime.min.time())
    end_dt = datetime.combine(last_sunday + timedelta(days=1), datetime.min.time())

    return start_dt, end_dt
