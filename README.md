# NWS-data-pipeline
Data pipeline to query weather data from NWS

- FastAPI + PSQL
- Station and weather observations models
- Constraint checks


Commands

- check database 
sudo docker compose exec db psql -U postgres


Assumptions:
- a weather observation from NWS is invariable and will not be updated later
    - duplicated observations will be skipped and not updated