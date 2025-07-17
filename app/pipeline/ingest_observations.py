from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.station import Station
from ..models.weather_observation import WeatherObservation
from ..pipeline.nws_api_functions import validate_station, fetch_observations, parse_observation
from sqlalchemy.dialects.postgresql import insert
from app.utils.logging import get_logger

logger = get_logger()

def run_pipeline(db: Session, station_id: str, start: datetime = None, end: datetime = None) -> int:
    """
    Run the ingestion pipeline for a station. Will fetch and store weather observations
    for the past 7 days by default, or a custom time range.

    Args:
        db (Session): Active SQLAlchemy DB session.
        station_id (str): NWS station identifier.
        start (datetime): Optional start datetime (UTC).
        end (datetime): Optional end datetime (UTC).

    Returns:
        int: Number of inserted records.
    """
    # Use default 7-day range if not specified
    end = end or datetime.utcnow()
    start = start or (end - timedelta(days=7))

    # Ensure station exists in DB
    station = db.query(Station).filter_by(nws_id=station_id).first()
    if not station:
        metadata = validate_station(station_id)
        if not metadata:
            logger.error(f"Station {station_id} not valid, please check that the station ID is correct.")
            return 0
        station = Station(
            nws_id=station_id,
            name=metadata.get("name"),
            timezone=metadata.get("timeZone"),
            latitude=metadata.get("latitude"),
            longitude=metadata.get("latitude"),
        )
        db.add(station)
        db.commit()
        db.refresh(station)

    # Fetch observations
    raw_obs = fetch_observations(station_id, start, end)
    if not raw_obs:
        logger.warning(f"No observations found for {station_id} between {start} and {end}")
        return 0

    # Parse observations
    to_insert = []
    for obs in raw_obs:
        parsed = parse_observation(obs)
        if not parsed.get("timestamp"):
            continue # ignore records without timestamp
        parsed["station_id"] = station.id
        to_insert.append(parsed)

    if to_insert:
        stmt = (
            insert(WeatherObservation)
            .values(to_insert)
            .on_conflict_do_nothing(index_elements=["station_id", "timestamp"])
            .returning(WeatherObservation.id)  # count insertions
        )

        result = db.execute(stmt)
        inserted_ids = result.scalars().all()
        inserted_count = len(inserted_ids)
        skipped_count = len(to_insert) - inserted_count

        logger.info(f"Inserted {inserted_count} new observations, skipped {skipped_count} duplicates or invalid records")
        db.commit()
        return inserted_count
    

