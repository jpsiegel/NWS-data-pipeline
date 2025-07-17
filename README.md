# NWS-data-pipeline
Data pipeline to query weather data from NWS

- FastAPI + PSQL
- Station and weather observations models
- Constraint checks
- Seeder to populate database
- Logger for reporting and error visibility
- Pipeline inserts only new records in batches for performance
- Endpoint documentation and docstrings


Usage

- check database 
sudo docker compose exec db psql -U postgres
- Run pipeline
sudo docker compose run app python -m app.seeder --station 011HI
parameter --station is optional, if not provided default station 000PG will be used.
- Check queries
sudo docker compose up
and go to http://localhost:8000/quueries
queries are executed for the first station that was added to the database
- A basic endpoint documentation is  


Assumptions:
- a weather observation from NWS is invariable and cannot be updated later, eg it is never "outdated"
    - duplicated observations will be skipped and not updated
- Pagination is not supported for /observations