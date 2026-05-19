"""Unit tests for DataWriter."""

import json
from pathlib import Path

import pandas as pd
import pytest

from ingestion.pipeline.writer import DataWriter


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def writer(output_dir: Path) -> DataWriter:
    return DataWriter(output_dir=output_dir)


@pytest.fixture
def sample_raw_records() -> list[dict]:
    return [
        {"name": "Jane Doe", "age": 30},
        {"name": "John Smith", "age": 25},
    ]


@pytest.fixture
def sample_clean_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Jane Doe", "John Smith"],
            "gender": ["female", "male"],
            "city": ["Springfield", "Shelbyville"],
            "state": ["Alabama", "Alabama"],
            "country": ["United States", "United States"],
            "email": ["jane@example.com", "john@example.com"],
            "age": [30, 25],
            "registration_date": pd.to_datetime(
                ["2020-01-01T00:00:00+00:00", "2021-06-15T00:00:00+00:00"],
                utc=True,
            ),
        }
    )


class TestDataWriter:

    def test_output_directory_is_created_automatically(self, output_dir):
        assert not output_dir.exists()
        DataWriter(output_dir=output_dir)
        assert output_dir.exists()

    def test_write_raw_creates_json_file(self, writer, sample_raw_records):
        path = writer.write_raw(sample_raw_records)
        assert path.exists()
        assert path.suffix == ".json"

    def test_raw_json_content_matches_input(self, writer, sample_raw_records):
        writer.write_raw(sample_raw_records)
        with writer.raw_path.open() as fh:
            loaded = json.load(fh)
        assert loaded == sample_raw_records

    def test_write_clean_creates_parquet_file(self, writer, sample_clean_df):
        path = writer.write_clean(sample_clean_df)
        assert path.exists()
        assert path.suffix == ".parquet"

    def test_clean_parquet_content_matches_input(self, writer, sample_clean_df):
        writer.write_clean(sample_clean_df)
        reloaded = pd.read_parquet(writer.clean_path)
        assert list(reloaded.columns) == list(sample_clean_df.columns)
        assert len(reloaded) == len(sample_clean_df)

    def test_write_raw_returns_correct_path(self, writer, sample_raw_records):
        path = writer.write_raw(sample_raw_records)
        assert path == writer.raw_path

    def test_write_clean_returns_correct_path(self, writer, sample_clean_df):
        path = writer.write_clean(sample_clean_df)
        assert path == writer.clean_path

    def test_write_clean_with_empty_df_does_not_raise(self, writer):
        # Should log a warning but not raise
        path = writer.write_clean(pd.DataFrame())
        assert isinstance(path, Path)
