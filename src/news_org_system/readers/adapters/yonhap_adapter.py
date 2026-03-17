"""Yonhap News adapter for Yonhap-specific RSS parsing."""

from .default_adapter import DefaultRSSAdapter


class YonhapAdapter(DefaultRSSAdapter):
    """Yonhap News RSS adapter.

    Currently inherits default behavior as Yonhap follows standard RSS format.
    Can be extended with Yonhap-specific logic if needed.
    """

    # Yonhap-specific fields can be added here if needed
    pass
