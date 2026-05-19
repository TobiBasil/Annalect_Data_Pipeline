from abc import ABC, abstractmethod


class BaseDataSource(ABC):
    """Abstract contract that every data source must satisfy."""

    @abstractmethod
    def fetch(self, limit: int) -> list[dict]:
        """Return up to *limit* raw records as plain dicts."""
        ...
