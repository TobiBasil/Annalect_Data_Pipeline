import pandas as pd

class DataTransformer:
    """
    Extracts and normalises raw API records using vectorised pandas operations.
    """

    # Columns produced by pd.json_normalize that map to our output schema
    NORMALIZED_FIELD_MAP: dict[str, str] = {
        "name.first": "_name_first",
        "name.last": "_name_last",
        "gender": "gender",
        "location.city": "city",
        "location.state": "state",
        "location.country": "country",
        "email": "email",
        "dob.age": "age",
        "registered.date": "registration_date",
    }

    # Defining specific cleaning groups
    TITLE_CASE_COLUMNS = ["name", "city", "state", "country"]
    LOWER_CASE_COLUMNS = ["email", "gender"]
    CATEGORY_COLUMNS = ["gender"]

    def transform(self, raw_records: list[dict]) -> pd.DataFrame:
        """
        Flatten nested JSON records and apply all cleaning rules.

        Steps
        -----
        1. Normalise nested dicts into a flat DataFrame.
        2. Select and rename only the required columns.
        3. Combine first + last name into a single 'name' column.
        4. Normalise text fields (strip, title-case where appropriate).
        5. Parse registration_date to UTC-aware datetime.
        """

        # Handle empty data gracefully with an early exit
        if not raw_records:
            # Return an empty DataFrame with the expected columns
            return pd.DataFrame(columns=[
                "name", "gender", "city", "state", "country",
                "email", "age", "registration_date"
            ])

        df = pd.json_normalize(raw_records)

        df = self._select_and_rename_columns(df)
        df = self._build_full_name(df)
        df = self._clean_text_columns(df)
        df = self._parse_registration_date(df)
        df = self._change_to_category(df)

        return df

    # ------------------------------------------------------------------
    # Private helpers – each owns exactly one transformation concern
    # ------------------------------------------------------------------

    def _select_and_rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {src: dst for src, dst in self.NORMALIZED_FIELD_MAP.items() if src in df.columns}
        return df[list(rename_map.keys())].rename(columns=rename_map)

    def _build_full_name(self, df: pd.DataFrame) -> pd.DataFrame:
        """Concatenate first + last name columns into a single 'name' column."""
        df["name"] = df["_name_first"].str.strip() + " " + df["_name_last"].str.strip()
        df = df.drop(columns=["_name_first", "_name_last"])
        return df

    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.TITLE_CASE_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

        for col in self.LOWER_CASE_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
        return df

    def _change_to_category(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.CATEGORY_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype("category")
        return df

    def _parse_registration_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df["registration_date"] = pd.to_datetime(
            df["registration_date"], utc=True, errors="coerce"
        )
        return df

