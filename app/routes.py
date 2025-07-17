from typing import Tuple
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text, select

from app.db.session import get_db
from app.models.weather_observation import WeatherObservation
from app.models.station import Station

router = APIRouter()


def get_first_station(db: Session) -> Station:
    """
    Fetch the first-added weather station from the database.
    """
    station = db.query(Station).order_by(Station.id.asc()).first()
    if not station:
        raise HTTPException(status_code=404, detail="No stations found in the database.")
    return station


def get_last_week_range() -> Tuple[datetime, datetime]:
    """
    Returns the datetime range for the previous week (Monday to Sunday).
    """
    today = datetime.utcnow().date()
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    start_dt = datetime.combine(last_monday, datetime.min.time())
    end_dt = datetime.combine(last_sunday + timedelta(days=1), datetime.min.time())
    return start_dt, end_dt


@router.get("/metrics/avg_temperature_last_week")
def avg_temp_last_week(db: Session = Depends(get_db)):
    """
    Calculate the average observed temperature (°C) for the previous week (Mon–Sun)
    for the first-added station only.
    """
    station = get_first_station(db)
    start_dt, end_dt = get_last_week_range()

    result = db.query(func.avg(WeatherObservation.temperature))\
        .filter(
            WeatherObservation.station_id == station.id,
            WeatherObservation.timestamp >= start_dt,
            WeatherObservation.timestamp < end_dt
        ).scalar()

    return {
        "station_id": station.nws_id,
        "last_week_monday": start_dt.isoformat(),
        "last_week_sunday": end_dt.isoformat(),
        "average_temperature": f"{round(result, 2)} °C" if result else None
    }


@router.get("/metrics/max_wind_speed_delta")
def max_wind_speed_delta(db: Session = Depends(get_db)):
    """
    Find the maximum wind speed change (delta) between consecutive observations
    for the first-added station in the last 7 days.
    """
    station = get_first_station(db)
    station_id = station.id

    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(days=7)

    sql = text("""
        SELECT MAX(ABS(wind_speed - prev_wind_speed)) AS max_delta
        FROM (
            SELECT
                wind_speed,
                LAG(wind_speed) OVER (ORDER BY timestamp) AS prev_wind_speed
            FROM weather_observations
            WHERE station_id = :station_id
              AND timestamp BETWEEN :start AND :end
        ) AS deltas
        WHERE prev_wind_speed IS NOT NULL
    """)

    result = db.execute(sql, {
        "station_id": station_id,
        "start": start_dt,
        "end": end_dt
    }).scalar()

    return {
        "station_id": station.nws_id,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "max_wind_speed_delta_kmh": f"{round(result, 2)} km/h" if result else None
    }
