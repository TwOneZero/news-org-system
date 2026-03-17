"""Maeil Business News adapter for Maeil-specific RSS parsing."""

from .default_adapter import DefaultRSSAdapter


class MaeliAdapter(DefaultRSSAdapter):
    """Maeil Business News RSS adapter.

    Currently inherits default behavior as Maeil follows standard RSS format.
    Can be extended with Maeil-specific logic if needed.
    """

    # Maeil-specific fields can be added here if needed
    pass
