"""Dyanmic vertical menu"""

import re
from typing import Callable, Iterable, Optional

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import to_plain_text
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl

from .vertmenu import Item, VertMenu

E = KeyPressEvent


class DynVertMenuBase:
    def __init__(
        self,
        items: Iterable[Item],
        selected_item: Optional[Item] = None,
        selected_handler: Optional[Callable[[Optional[Item], int], None]] = None,
        accept_handler: Optional[Callable[[Item], None]] = None,
        menu_max_width: Optional[int] = None,
    ):
        self._all_items = tuple(items)
        self._vertmenu = VertMenu(
            self._all_items,
            selected_item,
            selected_handler,
            accept_handler,
            focusable=False,
            max_width=menu_max_width,
        )
        self.buffer = Buffer(multiline=False, on_text_changed=self.on_change)
        self.control = BufferControl(
            buffer=self.buffer, key_bindings=self._vertmenu._init_key_bindings()
        )
        self.window = HSplit(
            [
                VSplit([Window(width=1, char=">", height=1), Window(self.control)]),
                self._vertmenu,
            ]
        )
        self._vertmenu.focus_window = self.window

    def on_change(self, buf: Buffer) -> None:
        raise NotImplementedError

    def __pt_container__(self) -> Container:
        return self.window


class RegexFilterVertMenu(DynVertMenuBase):
    def on_change(self, buf: Buffer) -> None:
        regex_str = buf.document.text
        try:
            regex = re.compile(regex_str)
        except re.error:
            return
        filtered_items = tuple(
            (item for item in self._all_items if regex.search(to_plain_text(item[0])))
        )
        self._vertmenu.control.items = filtered_items


class FuzzFilterVertMenu(DynVertMenuBase):
    def on_change(self, buf: Buffer) -> None:
        text = buf.document.text
        regex_str = ".*".join(text)
        try:
            regex = re.compile(regex_str, re.IGNORECASE)
        except re.error:
            return
        filtered_items = tuple(
            (item for item in self._all_items if regex.search(to_plain_text(item[0])))
        )
        self._vertmenu.control.items = filtered_items


class RegexSearchVertMenu(DynVertMenuBase):
    def on_change(self, buf: Buffer) -> None:
        regex_str = buf.document.text
        try:
            regex = re.compile(regex_str)
        except re.error:
            return
        item = next(
            (item for item in self._all_items if regex.search(to_plain_text(item[0])))
        )
        if item:
            self._vertmenu.control.selected_item = item


class FuzzSearchVertMenu(DynVertMenuBase):
    def on_change(self, buf: Buffer) -> None:
        text = buf.document.text
        regex_str = ".*".join(text)
        try:
            regex = re.compile(regex_str, re.IGNORECASE)
        except re.error:
            return
        item = next(
            (item for item in self._all_items if regex.search(to_plain_text(item[0])))
        )
        if item:
            self._vertmenu.control.selected_item = item
