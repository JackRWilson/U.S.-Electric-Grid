drop schema if exists electricity cascade;
create schema electricity;
set search_path to electricity;

create table state (
	state_id serial primary key,
	state_abbrev varchar(5) not null unique
);

create table city (
	city_id serial primary key,
	state_id int not null
        references state(state_id),
    city_name varchar(100) not null,
    est_population int,
    avg_household_income int,
    median_household_income int,
    unique (state_id, city_name)
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
    demand_mwh int not null,
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

create table ba_city (
    ba_city_id serial primary key,
    ba_id int not null
        references balancing_authority(ba_id),
    city_id int not null
        references city(city_id),
    "weight" numeric(8,6) not null,
    unique (ba_id, city_id)
);

create table plant (
    plant_id serial primary key,
    city_id int
        references city(city_id),
    ba_id int not null
        references balancing_authority(ba_id),
    latitude numeric(9,6),
    longitude numeric(9,6),
    plant_name varchar(100)
);

create table plant_fuel_type (
    plant_fuel_type_id serial primary key,
    fuel_type_id int not null
        references fuel_type(fuel_type_id),
    plant_id int not null
        references plant(plant_id),
    unique (plant_id, fuel_type_id)
);

create table weather (
    weather_id serial primary key,
    plant_id int not null
        references plant(plant_id),
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
    unique (plant_id, "period")
);