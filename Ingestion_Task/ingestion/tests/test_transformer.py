"""Unit tests for DataTransformer."""

import pandas as pd
import pytest

from ingestion.pipeline.transformer import DataTransformer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_raw_record(
    first="Jane",
    last="Doe",
    gender="female",
    city="Springfield",
    state="Oregon",
    country="United States",
    email="jane.doe@example.com",
    age=30,
    registered="2020-05-15T10:30:00.000Z",
) -> dict:
    """Build a minimal raw API record dict."""
    return {
        "name": {"first": first, "last": last},
        "gender": gender,
        "location": {"city": city, "state": state, "country": country},
        "email": email,
        "dob": {"age": age},
        "registered": {"date": registered},
    }


@pytest.fixture
def transformer() -> DataTransformer:
    return DataTransformer()


@pytest.fixture
def sample_records() -> list[dict]:
    return [
        make_raw_record(first="Jane", last="Doe", state="Oregon"),
        make_raw_record(first="John", last="Smith", state="Texas", gender="male"),
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDataTransformer:

    def test_output_has_all_required_columns(self, transformer, sample_records):
        df = transformer.transform(sample_records)
        expected_columns = {"name", "gender", "city", "state", "country", "email", "age", "registration_date"}
        assert expected_columns.issubset(set(df.columns))

    def test_name_is_concatenated_first_last(self, transformer):
        records = [make_raw_record(first="Alice", last="Wonder")]
        df = transformer.transform(records)
        assert df["name"].iloc[0] == "Alice Wonder"

    def test_email_is_lowercased(self, transformer):
        records = [make_raw_record(email="UPPER@EXAMPLE.COM")]
        df = transformer.transform(records)
        assert df["email"].iloc[0] == "upper@example.com"

    def test_gender_is_lowercased(self, transformer):
        records = [make_raw_record(gender="FEMALE")]
        df = transformer.transform(records)
        assert df["gender"].iloc[0] == "female"

    def test_city_is_title_cased(self, transformer):
        records = [make_raw_record(city="new york")]
        df = transformer.transform(records)
        assert df["city"].iloc[0] == "New York"

    def test_registration_date_is_parsed_as_datetime(self, transformer, sample_records):
        df = transformer.transform(sample_records)
        assert pd.api.types.is_datetime64_any_dtype(df["registration_date"])

    def test_row_count_matches_input(self, transformer, sample_records):
        df = transformer.transform(sample_records)
        assert len(df) == len(sample_records)

    def test_transform_returns_dataframe(self, transformer, sample_records):
        result = transformer.transform(sample_records)
        assert isinstance(result, pd.DataFrame)
