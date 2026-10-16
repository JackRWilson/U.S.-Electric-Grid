# Overview
Analysis of U.S. Energy generation and demand and how weather, population, and income play a role.

# Set Up
Download static data and insert into the data folder.
| File | Status | Link | Notes |
| ----- | ----- | ----- | -----: |
| `2___Plant_Y2025.xlsx`| Required | [link](https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip) | Only pull "2___Plant_Y2025.xlsx" |
| `CAINC1_ALL_AREAS_1969_2024.csv` | Required | [link](https://apps.bea.gov/regional/zip/CAINC1.zip) | Only pull "CAINC1_ALL_AREAS_1969_2024.csv" |
| `sub-est2025.csv` | Required | [link](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/cities/totals/sub-est2025.csv)| |
| `2020_Gaz_counties_national.txt` | Only if missing | [link](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/2020_Gaz_counties_national.zip) | |
| `Balancing_Authority_2025.xlsx` | Only if missing | [link](https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip) | Only pull "Balancing_Authority_2025.xlsx" |
| `out_eia861__yearly_balancing_authority_service_territory.parquet` | Only if missing | [link](https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/out_eia861__yearly_balancing_authority_service_territory.parquet) | |

Create a .env file with API and DB credentials using the format in .env.example.
```yaml
EIA_API_KEY=eia_api_key # Required 
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username # Required 
DB_PASSWORD=your_password # Required 
DB_DATABASE=your_db # Required 
DB_SCHEMA=electricity 
DB_ENGINE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_DATABASE}?options=-c%20search_path=${DB_SCHEMA}
EIA_INITIAL_START=2026-07-17 # Optional (delete)
WEATHER_INITIAL_START=2026-07-17 # Optional (delete)
```

| Variable | Status | Default | Notes |
| ----- | :-----: | :-----: | -----: |
| `EIA_API_KEY` | Required | | Request EIA key [here](https://www.eia.gov/opendata/) |
| `DB_USER` | Required | | Database username |
| `DB_PASSWORD` | Required | | Database password |
| `DB_DATABASE` | Required | | Database name (postgres) |
| `EIA_INITIAL_START` | Optional | 90 days | Controls initial EIA backfill window in in `YYYY-MM-DD` format. |
| `WEATHER_INITIAL_START` | Optional | 90 days | Controls initial weather backfill window in in `YYYY-MM-DD` format. |
Delete to use defaults.

## Airflow
Open Docker and navigate to the project directory.
Build the container.
```powershell
docker compose up -d --build
```
Copy Airflow username and password. {user, password}
```powershell
docker exec -it airflow /bin/bash
```
```powershell
cat simple_auth_manager_passwords.json.generated
```

Open http://localhost:8080/ and enter credentials.
Enable `electricity_etl_dag` or trigger manually. The first run will take a while.

### Manual
Open a terminal and navigate to the project directory.
Create a virtual environment and activate it, and install requirements.
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Install requirements.
```powershell
pip install -r requirements.txt
```
Open DBeaver and run schema.
```
./db/electricity_schema.sql
```
Run pipeline in main.py.
```
./src/electricity/main.py
```


# Data
### Sources
EIA API
https://www.eia.gov/opendata/

Weather API
https://open-meteo.com/en/docs/historical-forecast-api

EIA 2025 Plant Data
https://www.eia.gov/electricity/data/eia860/

Population Data
https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html

Geo Data
https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html#list-tab-264479560

BA Territory Data
https://data.catalyst.coop/preview/pudl/out_eia861__yearly_balancing_authority_service_territory

Additional BA Territory Data
https://www.eia.gov/electricity/data/eia861/


# Research Questions
1\. How does weather affect electricity demand and renewable energy generation?

2\. If we can (somewhat) accurately predict weather can that be mapped to electricity/energy usage?

3\. How does energy demand and generation vary by area?

4\. How does population of an area impact its electricity generation and consumption?

5\. Do areas with higher income use more electricity? How much more?