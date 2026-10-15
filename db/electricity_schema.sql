drop schema if exists electricity cascade;
create schema electricity;
set search_path to electricity;

create table county (
    county_id serial primary key,
	fips_code char(5) unique not null,
	state_abbrev char(2) not null,
    state_name varchar(50) not null,
    county_name varchar(100) not null,
    est_population_2024 int,
    personal_income_total int,
    personal_income_per_capita int
);

create table balancing_authority (
    ba_id serial primary key,
    ba_code varchar(20) not null unique,
    ba_name varchar(200) not null
);

create table fuel_type (
    fuel_type_id serial primary key,
    fuel_type_code varchar(10) not null unique,
    fuel_type_name varchar(100) not null
);

create table electric_demand (
    electric_demand_id serial primary key,
    ba_id int not null
        references balancing_authority(ba_id),
    "period" timestamp not null,
    demand_mwh int,
    net_generation_mwh int,
    total_interchange_mwh int,
    unique (ba_id, "period")
);

create table electric_generation(
    electric_generation_id serial primary key,
    ba_id int not null
        references balancing_authority(ba_id),
    "period" timestamp not null,
    fuel_type_id int not null
        references fuel_type(fuel_type_id),
    generation_mwh int,
    unique (ba_id, "period", fuel_type_id)
);

create table ba_county (
    ba_county_id serial primary key,
    ba_id int not null
        references balancing_authority(ba_id),
    county_id int not null
        references county(county_id),
    unique (ba_id, county_id)
);

create table weather_location (
    weather_location_id serial primary key,
    latitude numeric(5,2) not null,
    longitude numeric(5,2) not null,
    unique(latitude, longitude)
);

create table weather (
    weather_id serial primary key,
    weather_location_id int not null
        references weather_location(weather_location_id),
    "period" timestamp not null,
    temp numeric(5,2),
    precipitation numeric(8,3),
    rain numeric(8,3),
    showers numeric(8,3),
    snowfall numeric(8,3),
    total_cloud_cover int,
    weather_code varchar(50),
    wind_speed_10m numeric(5,2),
    wind_speed_80m numeric(5,2),
    wind_speed_120m numeric(5,2),
    wind_speed_180m numeric(5,2),
    wind_gusts_10m numeric(5,2),
    unique (weather_location_id, "period")
);

create table ba_weather_location (
    ba_weather_location_id serial primary key,
    ba_id int not null
        references balancing_authority(ba_id),
    weather_location_id int not null
        references weather_location(weather_location_id),
    weather_weight numeric (9,8) not null
);