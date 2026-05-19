import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class DataWriter:
    """
    Persists raw and validated datasets to disk.

    raw_users.json   – the untouched API payload
    clean_users.parquet – the validated, transformed records
    """

    def __init__(self, output_dir: str | Path = ".") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def raw_path(self) -> Path:
        return self._output_dir / "raw_users.json"

    @property
    def clean_path(self) -> Path:
        return self._output_dir / "clean_users.parquet"

    def write_raw(self, records: list[dict]) -> Path:
        """Serialise the raw API records as pretty-printed JSON."""
        with self.raw_path.open("w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2, default=str)
        logger.info("Raw data written to %s (%d records).", self.raw_path, len(records))
        return self.raw_path

    def write_clean(self, df: pd.DataFrame) -> Path:
        """Persist the validated DataFrame as a Parquet file."""
        if df.empty:
            logger.warning("Clean DataFrame is empty; skipping parquet write.")
            return self.clean_path

        for col in df.select_dtypes(include=["datetimetz"]).columns:
            df[col] = df[col].dt.tz_convert("UTC")

        df.to_parquet(self.clean_path, index=False, engine="pyarrow")
        logger.info("Clean data written to %s (%d records).", self.clean_path, len(df))
        return self.clean_path
