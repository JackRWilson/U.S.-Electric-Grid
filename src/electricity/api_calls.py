import requests
import pandas as pd
from utils import print_progress_bar
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def _build_session():
    retry = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


SESSION = _build_session()


class ExtractAPI:
    def _request(self, url, params):
        response = SESSION.get(url, params=params, timeout=(10, 120))
        if not response.ok:
            raise RuntimeError(
                f"API request failed with status code {response.status_code} for endpoint {url}"
            )
        return response

    def get_eia_data(self, url, params, page_size=5000):
        params = {**params, "length": page_size, "offset": 0}
        all_rows = []

        while True:
            data = self._request(url, params).json()["response"]

            total = int(data["total"])
            rows = data["data"]
            if not rows:
                break

            all_rows.extend(rows)
            print_progress_bar(len(all_rows), total)

            if len(all_rows) >= total:
                print()
                break
            params["offset"] += len(rows)

        return pd.DataFrame(all_rows)

    def get_weather_data(self, url, params):
        return self._request(url, params).json()
