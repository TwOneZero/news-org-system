"""RSS adapter classes for site-specific parsing."""

from .base import BaseRSSAdapter
from .default_adapter import DefaultRSSAdapter

__all__ = ["BaseRSSAdapter", "DefaultRSSAdapter"]
