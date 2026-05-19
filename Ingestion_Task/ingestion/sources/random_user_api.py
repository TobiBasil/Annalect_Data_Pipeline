import requests
from ingestion.sources.base import BaseDataSource


class RandomUserAPIDataSource(BaseDataSource):
    """Fetches random user records from the randomuser.me REST API."""

    def __init__(self,
        batch_size: int = 1_000,
        api_url: str = "https://randomuser.me/api/",
        max_results_per_request: int = 5_000
    ) -> None:
        self._api_url = api_url
        self._max_limit = max_results_per_request
        self._batch_size = min(batch_size, self._max_limit)

    def fetch(self, limit: int) -> list[dict]:
        """Download *limit* users from the API in batches."""

        records: list[dict] = []

        with requests.Session() as session:
            while len(records) < limit:
                remaining = limit - len(records)
                page_size = min(self._batch_size, remaining)

                response = session.get(
                    self._api_url,
                    params={"results": page_size, "exc": "login,nat,picture"},
                    timeout=30
                )
                response.raise_for_status()

                page_records = response.json().get("results", [])
                records.extend(page_records)

        return records[:limit]