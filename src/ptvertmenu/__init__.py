"""Vertical menu widget for prompt-toolkit with optional fzf-inspired search"""

import importlib.metadata

from .filteredmenu import FuzzFilterVertMenu, RegexFilterVertMenu
from .vertmenu import Item, VertMenu


def version() -> str:
    return importlib.metadata.version("ptvertmenu")


__all__ = [
    "version",
    "VertMenu",
    "FuzzFilterVertMenu",
    "RegexFilterVertMenu",
    "Item",
]
