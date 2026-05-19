import logging
import pandas as pd
from pydantic import ValidationError, TypeAdapter
from ingestion.models.user_record import UserRecord

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validate *df* by leveraging TypeAdapter for list validation.

    Invalid rows are logged and dropped; the method returns only the
    subset of records that satisfy the schema so the writer always
    receives clean data.
    """

    def __init__(self) -> None:
        # Initialize a TypeAdapter once for the entire lifecycle to save overhead
        self._adapter = TypeAdapter(list[UserRecord])

    def validate(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
        """
        Validate *df* row by row against UserRecord.

        Returns
        -------
        valid_df   : DataFrame containing only schema-conformant rows.
        errors     : List of dicts describing each rejected row.
        """
        if df.empty:
            return pd.DataFrame(), []

        raw_records = df.to_dict(orient="records")
        errors: list[dict] = []

        try:
            # Attempt to validate the entire batch at once
            validated_records = self._adapter.validate_python(raw_records)

            # If everything passes, serialize models back to dicts immediately
            valid_rows = [record.model_dump() for record in validated_records]
            valid_df = pd.DataFrame(valid_rows)
            logger.info("All %d rows passed validation.", len(df))
            return valid_df, errors

        except ValidationError as exc:
            # If any row fails, find the bad rows using their error metadata
            logger.warning("Validation errors detected in batch. Isolating bad rows...")

            # Map index out of the ValidationError list
            invalid_indices = set()
            for err in exc.errors():
                # Extract the top-level list index that failed
                batch_idx = err["loc"][0]
                invalid_indices.add(batch_idx)

                # Map it back to the original Pandas DataFrame index for accurate logs
                original_df_idx = df.index[batch_idx]
                errors.append({"row_index": original_df_idx, "errors": [err]})
                logger.warning("Row %s failed validation: %s", original_df_idx, err["msg"])

            # Filter the dictionaries using the isolated invalid list indices
            valid_rows = [
                raw_records[i] for i in range(len(raw_records))
                if i not in invalid_indices
            ]

            # Re-verify the sanitised subset to compile into valid model dictionaries
            if valid_rows:
                validated_subset = self._adapter.validate_python(valid_rows)
                valid_df = pd.DataFrame([r.model_dump() for r in validated_subset])
            else:
                valid_df = pd.DataFrame()

            logger.warning(
                "%d/%d rows failed validation and were dropped.",
                len(invalid_indices),
                len(df),
            )

            return valid_df, errors