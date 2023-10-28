"""Vertical menu widget for prompt-toolkit with optional fzf-inspired search"""

import importlib.metadata


def version() -> str:
    return importlib.metadata.version("ptvertmenu")
