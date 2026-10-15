# Overview
Analysis of U.S. Energy generation and demand and how weather, population, and income play a role.

# Set Up
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create .env file with API and DB credentials using format in .env.example

# Data
EIA API

Weather API

EIA 2025 Plant/Generator Data
https://www.eia.gov/electricity/data/eia860/

Population Data
https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html

Geo Data
https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html#list-tab-264479560

BA Territory Data
https://data.catalyst.coop/preview/pudl/out_eia861__yearly_balancing_authority_service_territory

Additional BA Territory Data
https://www.eia.gov/electricity/data/eia861/
