# 🌤 NWS Data Pipeline

A weather data ingestion pipeline using the [National Weather Service API](https://www.weather.gov/documentation/services-web-api), created with Docker, FastAPI and PostgreSQL.


## 🚀 Features

- Containerization using **Docker** and Docker Compose
- **FastAPI + PostgreSQL** backend
- Models for **Stations** and **Weather Observations**
- Migrations with Alembic
- **Validation & constraint checks** to prevent duplicates
- Custom **logger** for visibility into the pipeline
- Efficient **batch inserts** of only new records
- SQL **window functions** for analytical queries (e.g., max wind delta)
- Query access via **RESTful endpoints**
- Basic auto-generated documentation via Swagger (see `/docs`)
- Clear **docstrings** and type annotations for maintainability


## 🧪 Usage

### 0. Make sure Docker is installed
- Check [Docker](https://docs.docker.com/engine/install/) for information
- Tested using Docker version 28.3.2

### 1. Run migrations
`docker compose run app alembic upgrade head`
- Now database schema is set up

### 2. Run pipeline
- Use seeder to populate database

`docker compose run app python -m app.seeder --station 011HI`

- Note that parameter `--station` is optional, if not provided default station 000PG will be used (default can be edited in seeder.py)
- This can be done several times, for the same or new stations.

### 3. Spin up the app and check metrics
`docker compose up`
- Then open your browser and go to:
- http://localhost:8000/metrics/avg_temperature_last_week - Average temperature
- http://localhost:8000/metrics/max_wind_speed_delta - Maximum wind speed change
- http://localhost:8000/docs - auto-generated Swagger docs
- Note that metrics endpoints run queries for the first added station in the database.

### 4. Optionally check database
`docker compose exec db psql -U postgres`
- Use psql statements to view stored data eg `select * from stations`;

---

## Assumptions

- A weather observation from NWS is **immutable**, eg once recorded, it will not change.
  - Therefore, **duplicate observations are skipped** and will not be updated. There is no "outdated" observation
- NWS API does not support **pagination** for the `/observations` endpoint.
