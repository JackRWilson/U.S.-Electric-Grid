import hashlib
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from api_calls import ExtractAPI
from utils import STATE_NAMES, AGG_RESPONDENTS

BASE_URL = "https://api.eia.gov/v2/electricity/rto"
DEMAND_URL = f"{BASE_URL}/region-data/data/"
GENERATION_URL = f"{BASE_URL}/fuel-type-data/data/"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

CACHE_DIR = Path("../../data/cache")

LOOK_BACK = timedelta(days=90)
HR_FORMAT = "%Y-%m-%dT%H"


def incremental_extract(
    cache_path,
    extract_function,
    dup_subset_keys,
    time_col,
    default_start,
    overlap=timedelta(hours=20),
    chunk=timedelta(days=7),
    refresh=False,
):
    cached_data = None
    if cache_path.exists() and not refresh:
        cached_data = pd.read_parquet(cache_path)

    if cached_data is not None and not cached_data.empty:
        start = cached_data[time_col].max() - overlap
    else:
        cached_data = None
        start = default_start
    now = datetime.now(UTC).replace(tzinfo=None)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_start = start
    while chunk_start < now:
        chunk_end = min(chunk_start + chunk, now)
        new_data = extract_function(chunk_start, chunk_end)

        if not new_data.empty:
            if cached_data is None:
                out_data = new_data
            else:
                out_data = pd.concat([cached_data, new_data], ignore_index=True)

            out_data = (
                out_data.drop_duplicates(subset=dup_subset_keys, keep="last")
                .sort_values(time_col)
                .reset_index(drop=True)
            )

            out_data.to_parquet(cache_path, index=False)

        chunk_start = chunk_end

    return out_data if out_data is not None else pd.DataFrame()


class ExtractEIA(ExtractAPI):
    def _init_params(self, start, end=None):
        params = {
            "api_key": os.environ["EIA_API_KEY"],
            "frequency": "hourly",
            "data[0]": "value",
            "start": start.strftime(HR_FORMAT),
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
        }
        if end is not None:
            params["end"] = end.strftime(HR_FORMAT)
        return params

    def _clean(self, df):
        df["period"] = pd.to_datetime(df["period"])
        df["value"] = pd.to_numeric(df["value"])
        return df

    def extract_demand(self, start=None, refresh=False):
        def extract(since, until):
            params = self._init_params(since, until)
            params["facets[type][]"] = ["D", "NG", "TI"]
            return self._clean(self.get_eia_data(DEMAND_URL, params))

        if start is None:
            default_start = datetime.now(UTC).replace(tzinfo=None) - LOOK_BACK
        else:
            default_start = start

        return incremental_extract(
            CACHE_DIR / "eia_demand.parquet",
            extract,
            dup_subset_keys=["period", "respondent", "type"],
            time_col="period",
            default_start=default_start,
            refresh=refresh,
        )

    def extract_generation(self, start=None, refresh=False):
        def extract(since, until):
            return self._clean(
                self.get_eia_data(GENERATION_URL, self._init_params(since, until))
            )

        if start is None:
            default_start = datetime.now(UTC).replace(tzinfo=None) - LOOK_BACK
        else:
            default_start = start

        return incremental_extract(
            CACHE_DIR / "eia_generation.parquet",
            extract,
            dup_subset_keys=["period", "respondent", "fueltype"],
            time_col="period",
            default_start=default_start,
            chunk=timedelta(days=3),
            refresh=refresh,
        )


class ExtractExcel:
    def extract(self, data_path, skiprows=1):
        return pd.read_excel(data_path, skiprows=skiprows)


class ExtractCSV:
    def extract(self, data_path, encoding="utf-8", delimiter=",", low_memory=True):
        return pd.read_csv(
            data_path, encoding=encoding, delimiter=delimiter, low_memory=low_memory
        )


class ExtractParquet:
    def extract(self, data_path):
        return pd.read_parquet(data_path)


class BALocations:
    GRID_STEP = 0.25
    TOP_N = 3

    def __init__(self, respondents_df, ba_df, coord_df, ba_county_df, plant_df, pop_df):
        self._respondents_df = respondents_df
        self._ba_df = ba_df
        self._coord_df = coord_df.rename(columns=str.strip)
        self._ba_county_df = ba_county_df
        self._plant_df = plant_df
        self._pop_df = pop_df

    def _snap(self, s):
        return (s / self.GRID_STEP).round() * self.GRID_STEP

    def get_coords(self):
        county_ba_points, county_coords = self._get_county_points()
        plant_ba_points, plant_coords = self._get_plant_points(county_ba_points)

        ba_points = pd.concat([county_ba_points, plant_ba_points], ignore_index=True)
        coordinates = (
            pd.concat([county_coords, plant_coords], ignore_index=True)
            .drop_duplicates()
            .sort_values(["latitude", "longitude"])
            .reset_index(drop=True)
        )
        return ba_points, coordinates

    def _top_n_weighted_points(self, df, lat_col, long_col):
        top_counties = (
            df.sort_values(["respondent", "population"], ascending=[True, False])
            .groupby("respondent")
            .head(self.TOP_N)
            .copy()
        )
        top_counties["county_weight"] = top_counties[
            "population"
        ] / top_counties.groupby("respondent")["population"].transform("sum")

        top_counties["latitude"] = self._snap(top_counties[lat_col])
        top_counties["longitude"] = self._snap(top_counties[long_col])

        ba_points = top_counties.groupby(
            ["respondent", "latitude", "longitude"],
            as_index=False,
        ).agg(
            county_population=("population", "sum"),
            weather_weight=("county_weight", "sum"),
            county_name=("county_name", self._join_unique_names),
            state_abbrev=("state_abbrev", self._join_unique_names),
        )
        ba_points["state_name"] = ba_points["state_abbrev"].map(
            lambda states: self._join_unique_names(
                STATE_NAMES.get(state, state) for state in states.split("; ")
            )
        )
        ba_points = ba_points.drop(columns="state_abbrev")
        coordinates = (
            ba_points[["latitude", "longitude"]]
            .drop_duplicates()
            .sort_values(["latitude", "longitude"])
            .reset_index(drop=True)
        )
        return ba_points, coordinates

    def _join_unique_names(self, names):
        return "; ".join(sorted({name for name in names if pd.notna(name)}))

    def _get_county_points(self):
        coord = self._coord_df
        bc = self._ba_county_df
        ba = self._ba_df

        lookup = (
            ba[["BA ID", "BA Code"]]
            .drop_duplicates()
            .rename(
                columns={"BA ID": "balancing_authority_id_eia", "BA Code": "respondent"}
            )
        )

        bc = bc[pd.to_datetime(bc["report_date"]).dt.year == 2025].copy()
        bc["county_id_fips"] = bc["county_id_fips"].astype(int)
        bc = bc.merge(lookup, on="balancing_authority_id_eia", how="left")
        bc = bc.groupby(
            ["respondent", "county_id_fips"],
            as_index=False,
        ).agg(population=("population", "max"))

        county_coords = (
            coord[["GEOID", "NAME", "USPS", "INTPTLAT", "INTPTLONG"]]
            .drop_duplicates("GEOID")
            .rename(
                columns={
                    "GEOID": "county_id_fips",
                    "NAME": "county_name",
                    "USPS": "state_abbrev",
                }
            )
        )
        bc = bc.merge(county_coords, on="county_id_fips", how="left")

        return self._top_n_weighted_points(bc, "INTPTLAT", "INTPTLONG")

    def _get_plant_points(self, county_ba_points):
        coord = self._coord_df
        plants = self._plant_df
        pop = self._pop_df

        all_respondents = self._respondents_df.merge(
            county_ba_points, on="respondent", how="left"
        )
        all_respondents = all_respondents[
            ["respondent", "respondent-name", "latitude", "longitude"]
        ]
        all_respondents = (
            all_respondents.groupby(["respondent", "respondent-name"], as_index=False)
            .mean()
            .reset_index(drop=True)
        )

        pop = pop[pop["SUMLEV"] == 50].copy()
        pop["GEOID"] = pop["STATE"] * 1000 + pop["COUNTY"]
        pop = pop[["GEOID", "POPESTIMATE2025"]]

        missing = all_respondents[
            ~all_respondents["respondent-name"].isin(AGG_RESPONDENTS)
            & all_respondents["latitude"].isna()
        ]

        coord_small = coord[["USPS", "NAME", "GEOID"]].drop_duplicates(["USPS", "NAME"])

        missing_plants = missing.merge(
            plants,
            left_on="respondent",
            right_on="Balancing Authority Code",
            how="left",
        )[["respondent", "Plant Name", "Latitude", "Longitude", "State", "County"]]
        missing_plants["County"] = missing_plants["County"] + " County"

        plant_county = missing_plants.merge(
            coord_small,
            left_on=["State", "County"],
            right_on=["USPS", "NAME"],
            how="left",
        ).merge(pop, on="GEOID", how="left")
        plant_county = plant_county.rename(
            columns={"NAME": "county_name", "USPS": "state_abbrev"}
        )

        county_level = (
            plant_county.dropna(
                subset=["GEOID", "POPESTIMATE2025", "Latitude", "Longitude"]
            )
            .groupby(["respondent", "GEOID"], as_index=False)
            .agg(
                population=("POPESTIMATE2025", "max"),
                plant_lat=("Latitude", "mean"),
                plant_lon=("Longitude", "mean"),
                n_plants=("Plant Name", "nunique"),
                county_name=("county_name", "first"),
                state_abbrev=("state_abbrev", "first"),
            )
        )

        return self._top_n_weighted_points(county_level, "plant_lat", "plant_lon")


class ExtractWeather(ExtractAPI):
    VARS = (
        "temperature_2m",
        "weather_code",
        "precipitation",
        "rain",
        "snowfall",
        "showers",
        "cloud_cover",
        "wind_speed_10m",
        "wind_gusts_10m",
        "wind_speed_80m",
        "wind_speed_180m",
        "wind_speed_120m",
    )
    LOCATION_BATCH = 50
    TIME_CHUNK = timedelta(days=14)
    SLEEP = 6

    def _fetch_batch(self, batch, since, until):
        params = {
            "latitude": ",".join(str(lat) for lat, _ in batch),
            "longitude": ",".join(str(lon) for _, lon in batch),
            "hourly": ",".join(self.VARS),
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "timezone": "GMT",
            "start_date": since.strftime("%Y-%m-%d"),
            "end_date": until.strftime("%Y-%m-%d"),
        }
        payload = self.get_weather_data(WEATHER_URL, params)
        if isinstance(payload, dict):
            payload = [payload]

        frames = []
        for result, (lat, lon) in zip(payload, batch):
            df = pd.DataFrame(result["hourly"])
            df["latitude"] = lat
            df["longitude"] = lon
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    def _clean(self, df):
        df["time"] = pd.to_datetime(df["time"])
        now = datetime.now(UTC).replace(tzinfo=None)
        return df[df["time"] <= now]

    def extract_weather(self, coordinates_df, start=None, refresh=False):
        coords = list(
            coordinates_df[["latitude", "longitude"]].itertuples(index=False, name=None)
        )

        key = hashlib.md5(str(sorted(coords)).encode()).hexdigest()[:8]

        def extract(since, until):
            frames = []
            for i in range(0, len(coords), self.LOCATION_BATCH):
                batch = coords[i : i + self.LOCATION_BATCH]
                frames.append(self._fetch_batch(batch, since, until))
                time.sleep(self.SLEEP)

            return self._clean(pd.concat(frames, ignore_index=True))

        if start is None:
            default_start = datetime.now(UTC).replace(tzinfo=None) - LOOK_BACK
        else:
            default_start = start

        return incremental_extract(
            CACHE_DIR / f"weather_{key}.parquet",
            extract,
            dup_subset_keys=["latitude", "longitude", "time"],
            time_col="time",
            default_start=default_start,
            chunk=self.TIME_CHUNK,
            refresh=refresh,
        )
