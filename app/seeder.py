import argparse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.pipeline.ingest_observations import run_pipeline
from app.utils.logging import get_logger

logger = get_logger()

# Predefined fallback stations
test_stations = [
    "000PG",  # Southside Road
    "000SE",  # SCE South Hills Park
    "011HI",  # Lyon Honolulu
    "024CE",  # 39 Chocolate Springs
]

def main():
    # Parse optional --station argument
    parser = argparse.ArgumentParser(description="Run data pipeline for a weather station.")
    parser.add_argument("--station", type=str, help="Station ID to run the pipeline for.")
    args = parser.parse_args()

    # Decide station to use
    station_id = args.station if args.station else test_stations[0]

    logger.info(f"Running pipeline for station: {station_id}")

    # Connect to DB and run pipeline
    db: Session = SessionLocal()
    run_pipeline(db, station_id=station_id)
    db.close()

if __name__ == "__main__":
    main()
