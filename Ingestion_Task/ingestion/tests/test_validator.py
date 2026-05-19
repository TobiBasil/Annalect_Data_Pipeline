"""Unit tests for DataValidator schema enforcement."""

import pandas as pd
import pytest

from ingestion.pipeline.validator import DataValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def valid_row(**overrides) -> dict:
    base = {
        "name": "Jane Doe",
        "gender": "female",
        "city": "Springfield",
        "state": "Alabama",
        "country": "United States",
        "email": "jane.doe@example.com",
        "age": 30,
        "registration_date": "2020-05-15T10:30:00+00:00",
    }
    base.update(overrides)
    return base


@pytest.fixture
def validator() -> DataValidator:
    return DataValidator()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDataValidator:

    def test_valid_row_passes_validation(self, validator):
        df = pd.DataFrame([valid_row()])
        valid_df, errors = validator.validate(df)
        assert len(valid_df) == 1
        assert len(errors) == 0

    def test_invalid_email_is_rejected(self, validator):
        df = pd.DataFrame([valid_row(email="not-an-email")])
        valid_df, errors = validator.validate(df)
        assert len(valid_df) == 0
        assert len(errors) == 1

    def test_invalid_gender_is_rejected(self, validator):
        df = pd.DataFrame([valid_row(gender="unknown_gender")])
        valid_df, errors = validator.validate(df)
        assert len(valid_df) == 0
        assert len(errors) == 1

    def test_age_above_120_is_rejected(self, validator):
        df = pd.DataFrame([valid_row(age=121)])
        valid_df, errors = validator.validate(df)
        assert len(errors) == 1

    def test_negative_age_is_rejected(self, validator):
        df = pd.DataFrame([valid_row(age=-1)])
        valid_df, errors = validator.validate(df)
        assert len(errors) == 1

    def test_mixed_valid_and_invalid_rows(self, validator):
        rows = [
            valid_row(),
            valid_row(email="bad-email"),
            valid_row(age=200),
            valid_row(name="Bob Builder"),
        ]
        df = pd.DataFrame(rows)
        valid_df, errors = validator.validate(df)
        assert len(valid_df) == 2
        assert len(errors) == 2

    def test_valid_df_contains_expected_columns(self, validator):
        df = pd.DataFrame([valid_row()])
        valid_df, _ = validator.validate(df)
        assert "email" in valid_df.columns
        assert "registration_date" in valid_df.columns

    def test_empty_dataframe_returns_empty(self, validator):
        df = pd.DataFrame()
        valid_df, errors = validator.validate(df)
        assert valid_df.empty
        assert errors == []
