import logging
from dataclasses import dataclass
from pathlib import Path

from ingestion.sources import BaseDataSource
from ingestion.pipeline.transformer import DataTransformer
from ingestion.pipeline.validator import DataValidator
from ingestion.pipeline.writer import DataWriter

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Immutable summary returned after a pipeline run."""
    raw_path: Path
    clean_path: Path
    total_fetched: int
    total_valid: int
    total_invalid: int


class IngestionPipeline:
    """
    Orchestrates the end-to-end ingestion flow.

    Flow
    ----
    source.fetch() → transformer.transform() → validator.validate()
        → writer.write_raw() + writer.write_clean()
    """

    def __init__(
        self,
        source: BaseDataSource,
        transformer: DataTransformer,
        validator: DataValidator,
        writer: DataWriter,
    ) -> None:
        self._source = source
        self._transformer = transformer
        self._validator = validator
        self._writer = writer

    def run(self, limit: int = 1_000) -> PipelineResult:
        """
        Execute the full ingestion pipeline and return a summary.

        Parameters
        ----------
        limit : int
            Number of user records to fetch from the data source.
        """
        logger.info("Pipeline started — fetching %d records.", limit)

        raw_records = self._source.fetch(limit)
        logger.info("Fetched %d raw records.", len(raw_records))

        raw_path = self._writer.write_raw(raw_records)

        transformed_df = self._transformer.transform(raw_records)
        logger.info("Transformation complete — %d rows produced.", len(transformed_df))

        valid_df, errors = self._validator.validate(transformed_df)
        logger.info(
            "Validation complete — %d valid, %d invalid.",
            len(valid_df),
            len(errors),
        )

        clean_path = self._writer.write_clean(valid_df)

        result = PipelineResult(
            raw_path=raw_path,
            clean_path=clean_path,
            total_fetched=len(raw_records),
            total_valid=len(valid_df),
            total_invalid=len(errors),
        )
        logger.info(
            "Pipeline complete. Valid: %d | Invalid: %d",
            result.total_valid,
            result.total_invalid,
        )
        return result
