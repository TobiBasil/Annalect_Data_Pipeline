"""Integration tests for the full IngestionPipeline with mocked API."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ingestion.pipeline.ingestion_pipeline import IngestionPipeline, PipelineResult
from ingestion.pipeline.transformer import DataTransformer
from ingestion.pipeline.validator import DataValidator
from ingestion.pipeline.writer import DataWriter
from ingestion.sources.random_user_api import RandomUserAPIDataSource


# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

def make_api_user(
    first="Alice",
    last="Walker",
    gender="female",
    city="Denver",
    state="Colorado",
    country="United States",
    email="alice@example.com",
    age=28,
    registered="2019-03-12T08:00:00.000Z",
) -> dict:
    return {
        "name": {"first": first, "last": last},
        "gender": gender,
        "location": {"city": city, "state": state, "country": country},
        "email": email,
        "dob": {"age": age},
        "registered": {"date": registered},
    }


MOCK_API_USERS = [make_api_user(first=f"User{i}", last="Test", email=f"user{i}@example.com")
                  for i in range(5)]

MOCK_API_RESPONSE = {"results": MOCK_API_USERS}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def pipeline(output_dir: Path) -> IngestionPipeline:
    return IngestionPipeline(
        source=RandomUserAPIDataSource(),
        transformer=DataTransformer(),
        validator=DataValidator(),
        writer=DataWriter(output_dir=output_dir),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIngestionPipelineWithMockedAPI:

    @patch("requests.get")
    def test_pipeline_run_returns_pipeline_result(self, mock_get, pipeline):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: MOCK_API_RESPONSE,
            raise_for_status=lambda: None,
        )
        result = pipeline.run(limit=5)
        assert isinstance(result, PipelineResult)

    @patch("requests.get")
    def test_pipeline_fetches_correct_number_of_records(self, mock_get, pipeline):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: MOCK_API_RESPONSE,
            raise_for_status=lambda: None,
        )
        result = pipeline.run(limit=5)
        assert result.total_fetched == 5

    @patch("requests.get")
    def test_pipeline_writes_raw_json_file(self, mock_get, pipeline, output_dir):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: MOCK_API_RESPONSE,
            raise_for_status=lambda: None,
        )
        result = pipeline.run(limit=5)
        assert result.raw_path.exists()

    @patch("requests.get")
    def test_pipeline_writes_clean_parquet_file(self, mock_get, pipeline, output_dir):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: MOCK_API_RESPONSE,
            raise_for_status=lambda: None,
        )
        result = pipeline.run(limit=5)
        assert result.clean_path.exists()

    @patch("requests.get")
    def test_pipeline_valid_and_invalid_counts_sum_to_fetched(self, mock_get, pipeline):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: MOCK_API_RESPONSE,
            raise_for_status=lambda: None,
        )
        result = pipeline.run(limit=5)
        assert result.total_valid + result.total_invalid == result.total_fetched

    @patch("ingestion.sources.random_user_api.requests.Session.get")
    def test_api_is_called_with_results_param(self, mock_get, pipeline):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: MOCK_API_RESPONSE,
            raise_for_status=lambda: None,
        )
        pipeline.run(limit=5)

        assert mock_get.called

        # Extract arguments safely from the last call
        args, kwargs = mock_get.call_args

        # Validate the contents of the 'params' dictionary
        assert "params" in kwargs
        assert kwargs["params"]["results"] == 5


class TestRandomUserAPIDataSource:

    @patch("requests.get")
    def test_fetch_returns_list_of_dicts(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"results": MOCK_API_USERS},
            raise_for_status=lambda: None,
        )
        source = RandomUserAPIDataSource()
        records = source.fetch(limit=5)
        assert isinstance(records, list)
        assert all(isinstance(r, dict) for r in records)

    @patch("requests.get")
    def test_fetch_respects_limit(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"results": MOCK_API_USERS},
            raise_for_status=lambda: None,
        )
        source = RandomUserAPIDataSource()
        records = source.fetch(limit=3)
        assert len(records) <= 3
