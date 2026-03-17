"""ETnews adapter for ETnews-specific RSS parsing."""

from .default_adapter import DefaultRSSAdapter


class ETnewsAdapter(DefaultRSSAdapter):
    """ETnews RSS adapter.

    Currently inherits default behavior as ETnews follows standard RSS format.
    Can be extended with ETnews-specific logic if needed.
    """

    # ETnews-specific fields can be added here if needed
    pass
