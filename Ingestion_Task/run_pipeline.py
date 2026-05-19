

"""
Entry point for Part 1: Ingest 1000 users from the randomuser.me API.

Usage
-----
    python run_pipeline.py

Outputs (written to ./output/)
-------------------------------
    raw_users.json       - raw API payload
    clean_users.parquet  - validated, transformed records
"""

import logging
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')


from ingestion.sources import RandomUserAPIDataSource
from ingestion.pipeline.transformer import DataTransformer
from ingestion.pipeline.validator import DataValidator
from ingestion.pipeline.writer import DataWriter
from ingestion.pipeline.ingestion_pipeline import IngestionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

OUTPUT_DIR   = Path("output")
RECORD_LIMIT = 1_000


def build_pipeline(output_dir: Path = OUTPUT_DIR) -> IngestionPipeline:
    return IngestionPipeline(
        source=RandomUserAPIDataSource(batch_size=1_000),
        transformer=DataTransformer(),
        validator=DataValidator(),
        writer=DataWriter(output_dir=output_dir),
    )


if __name__ == "__main__":
    pipeline = build_pipeline()
    result = pipeline.run(limit=RECORD_LIMIT)

    print("\n── Pipeline Summary ──────────────────────────")
    print(f"  Records fetched : {result.total_fetched}")
    print(f"  Records valid   : {result.total_valid}")
    print(f"  Records invalid : {result.total_invalid}")
    print(f"  Raw output      : {result.raw_path}")
    print(f"  Clean output    : {result.clean_path}")
    print("──────────────────────────────────────────────\n")