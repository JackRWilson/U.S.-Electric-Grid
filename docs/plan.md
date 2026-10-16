# Overview
This project analyses U.S. Energy generation and demand and how weather, population, and income play a role.


# Data / Links
U.S. Energy Information Administration
https://www.eia.gov/opendata/
- Various paths
    - Hourly generation by source
        - Electricity > Electric Power Operations > Hourly Generation by Source
        - period, name, fuel type, value, units
    - Annual Emissions by State
        - Electricity > State Specific Data > Emissions from Energy Consumptions at... > CO2 Emissions Rate per MWh
        - year, state, fuel type, rate
    - Annual Consumption by State
        - Electricity > State Specific Data > Supply and disposition of electricity > Net Generation from Electric Power Sector ; Estimated Losses Incurred in Transmission and Distribution ; Net Interstate Imports ; Retail Sales of Electricity, Total Electric Industry ; Net Generation from All Sectors
    - Hourly Demand, Forecast, Generation, Interchange
        - Electricity > Electric Power Operations > Hourly Demand, Demand Forecast, Generation...
        - Might be better for mapping company areas
        - Filter by Demand (D) instead of forecast
- Open API
    - Could get API key or scrape from output
- Has lots of different energy stuff and locations
    - Could use Google Map API to get coordinates that can be easily mapped to more deterministic locations (join other tables)
- Data updated so could use Airflow orchestration
- Has hourly data options
- Probably also contains data on renewable energy

Open Source Weather API
https://open-meteo.com/en/docs
- Has forecast and past data
- Based on coordinates
- Temp, rain, humidity, wind, etc. hourly
- Less than 10,000 calls per day

EIA 2025 Plant Data
https://www.eia.gov/electricity/data/eia860/

Population Data
https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html

FIPS Data
https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html#list-tab-264479560

BA Data
https://data.catalyst.coop/preview/pudl/out_eia861__yearly_balancing_authority_service_territory

EIA Industry Report Data
https://www.eia.gov/electricity/data/eia861/

County Population Data
https://apps.bea.gov/regional/downloadzip.htm

Flow: EIA call > filter so only need respondent-codes from Plant that are in EIA > get lat/long from the remaining cords > Weather call with cords 


# Thoughts
Look at over energy and not just electricity?

Weather definitely affects solar and wind so would need to be supplemented by nuclear, hydro, or fossil fuels.


# Questions
1. How does weather affect electricity demand and renewable energy generation?
    Hypothesis: Electricity usage would go up when its warm (AC) and natural gas usage would go when its cold (furnace)
2. If we can (somewhat) accurately predict weather can that be mapped to electricity/energy usage?
3. How does energy demand and generation vary by area?
4. How does population of an area impact its electricity generation and consumption?
5. Do areas with higher income use more electricity? How much more?


# Deliverables
- PowerPoint
- Dashboard (DASH app)
- Airflow, DAGs


# Process
Project process is as follows (subject to change)

## Plan
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Explore data, practice extraction | 2 hr | 1:30 hrs|
| Collect all data sources | 1 hr | 1:30 hrs |
| Create questions | 30 min | 10 min |
| Create project plan | 1 hr | 30 min |
| Total | 3:30 hrs | 3:40 hrs |

## ETL Prep
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Create ERD | 1 hr | 1:30 hrs |
| Create schema | 1 hr | 45 min |
| Set up Airflow | 15 min | |
| Set up DB engine | 10 min | 1 hr |
| Total | 2:25 hrs | |

## Extract
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Extract data from sites | 1 hr | 12:40 hrs |
| Total | 1:30 hrs | 12:40 hrs |

## Transform
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Transform county data | 2 hrs | 6:20 hrs |
| Transform ba data | 30 min | 40 min |
| Transform fuel data | 30 min | 15 min |
| Transform demand data | 2 hrs | 1 hr |
| Transform generation data | 2 hrs | 10 min |
| Transform ba county data | 30 min | 40 min |
| Transform weather location data | 1 hr | 20 min |
| Transform weather data | 30 min | 2:15 hrs |
| Transform ba location data | 30 min | 15 min |
| Total | 9:30 hrs | 11:55 hrs |

## Load
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Load transformed data into DB | 3 hrs | |
| Total | 3 hrs | |

## App
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Sketch up possible app view | 1 hr | |
| Load data tables in | 3 hrs | |
| Create electricity generation section | 2 hrs | |
| Create electricty demand section | 2 hr | |
| Create weather section | 2 hr | |
| Create population section | 1 hr | |
| Create income section | 1 hr | |
| App final touches | 2 hr | |
| Total | 14 hrs | |

## Machine Learning (if time)

## Report (MD)
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Overview section | 1:30 hrs | |
| Questions / hypothesis section | 15 min | |
| Data description section | 30 min | |
| Tools used section | 15 min | |
| EDA / Analysis section | 2 hr | |
| App section | 30 min | |
| ETL diagram / Process section | 30 min | |
| Conclusion section | 30 min | |
| Sources section | 15 min | |
| Polish GitHub README | 1 hr | |
| Total | 7:15 hrs | |

## PowerPoint
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Overview section | 10 min | |
| Questions / hypothesis section | 30 min | |
| Data description section | 30 min | |
| App / EDA section | 10 min | |
| Technical challenges section | 30 min | |
| Conclusion section | 30 min | |
| Final touches | 30 min | |
| Total | 2:50 hrs | |

## Presentation
| Task | Est. Time | Act. Time |
| ---- | --------- | --------- |
| Practice | 3 hrs | |
| Total | 3 hrs | |