"""Vertical menu widget for prompt-toolkit"""

from functools import wraps
from typing import Any, Callable, NewType, Optional, Sequence

from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text.base import OneStyleAndTextTuple, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

E = KeyPressEvent

Item = NewType("Item", tuple[str, Any])


class VertMenu:
    def __init__(
        self,
        items: Sequence[Item],
        current_item: Optional[Item] = None,
        current_handler: Optional[Callable[[Optional[Item]], None]] = None,
        accept_handler: Optional[Callable[[Item], None]] = None,
        focusable: bool = True,
    ):
        self._items: Sequence[Item] = []
        self._current_item: Optional[Item] = None
        self._current_index: Optional[int] = None
        self._text_fragments: StyleAndTextTuples = []
        self.reset(items, current_item, current_handler, accept_handler)
        self.control = FormattedTextControl(
            self._text_fragments,
            key_bindings=self._get_key_bindings(),
            focusable=focusable,
        )
        self.window = Window(self.control, width=30, style=self.get_style)
        # Setting items via the property sanitizes everything:
        self.items = items
        self.handle_current()

    def reset(
        self,
        items: Sequence[Item],
        current_item: Optional[Item] = None,
        current_handler: Optional[Callable[[Optional[Item]], None]] = None,
        accept_handler: Optional[Callable[[Item], None]] = None,
    ) -> None:
        self._items = items
        if current_item is not None:
            self._current_index = self._items.index(current_item)
            self._current_item = current_item
        else:
            self._current_index = 0
            self._current_item = self._items[0]
        self.current_handler = current_handler
        self.accept_handler = accept_handler
        self._update_text_fragments()

    def get_style(self) -> str:
        if get_app().layout.has_focus(self.window):
            return "class:vertmenu.focused"
        else:
            return "class:vertmenu.unfocused"

    def _gen_mouse_handler(self, index: int) -> Callable[[MouseEvent], None]:
        def mouse_event(e: MouseEvent) -> None:
            if e.event_type == MouseEventType.MOUSE_UP:
                prev_index = self.current_index
                self.current_index = index
                if self.current_index != prev_index:
                    self.handle_current()

        return mouse_event

    def _gen_cell(self, index: int, item: Any) -> OneStyleAndTextTuple:
        if self.current_index is not None and index == self.current_index:
            style = "[SetCursorPosition] class:vertmenu.current"
        else:
            style = "class:vertmenu.item"
        last = index == len(self.items) - 1
        suffix = "\n" if not last else ""
        return (style, item[0] + suffix, self._gen_mouse_handler(index))

    def _update_text_fragments(self) -> None:
        self._text_fragments.clear()
        for i, item in enumerate(self.items):
            self._text_fragments.append(self._gen_cell(i, item))

    @property
    def items(self) -> Sequence[Item]:
        return self._items

    @items.setter
    def items(self, items: Sequence[Item]) -> None:
        old_current_item = self.current_item
        self._items = items
        self._current_index = None
        self._current_item = None
        self._update_text_fragments()
        width = 30
        for item in self._items:
            width = max(width, *(len(line) for line in item[0].split("\n")))
        self.window.width = width
        if not items:
            return
        try:
            self.current_item = old_current_item
        except ValueError:
            pass
        if self.current_item is None:
            self.current_index = 0

    @property
    def current_item(self) -> Optional[Item]:
        if not self.items:
            return None
        return self._current_item

    @current_item.setter
    def current_item(self, item: Item) -> None:
        self._current_index = None
        self._current_item = None
        if not self.items:
            return
        index = self.items.index(item)
        self.current_index = index

    @property
    def current_index(self) -> Optional[int]:
        if not self.items:
            return None
        return self._current_index

    @current_index.setter
    def current_index(self, index: int) -> None:
        if not self.items:
            self._current_index = None
            self._current_item = None
            return
        prev_index = self._current_index
        self._current_index = index
        self._current_index = max(0, self._current_index)
        self._current_index = min(len(self.items) - 1, self._current_index)
        self._current_item = self.items[self._current_index]
        if prev_index is not None:
            prev_item = self._items[prev_index]
            self._text_fragments[prev_index] = self._gen_cell(prev_index, prev_item)
        self._text_fragments[self._current_index] = self._gen_cell(
            self._current_index, self._current_item
        )

    def handle_current(self) -> None:
        if self.current_handler is not None:
            if self._current_index is not None:
                self.current_handler(self.items[self._current_index])
            else:
                self.current_handler(None)

    def handle_accept(self) -> None:
        if self.accept_handler is not None and self._current_index is not None:
            self.accept_handler(self.items[self._current_index])

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        def wrapper(func: Callable[[E], None]) -> Callable[[E], None]:
            @wraps(func)
            def inner(event: E) -> None:
                if not self.items:
                    return
                prev_index = self.current_index
                func(event)
                if self.current_index != prev_index:
                    self.handle_current()

            return inner

        @kb.add("c-home")
        @kb.add("escape", "home")
        @wrapper
        def _first(event: E) -> None:
            self.current_index = 0

        @kb.add("c-end")
        @kb.add("escape", "end")
        @wrapper
        def _last(event: E) -> None:
            self.current_index = len(self.items) - 1

        @kb.add("up")
        @wrapper
        def _up(event: E) -> None:
            assert self.current_index is not None
            self.current_index -= 1

        @kb.add("down")
        @wrapper
        def _down(event: E) -> None:
            assert self.current_index is not None
            self.current_index += 1

        @kb.add("pageup")
        @wrapper
        def _pageup(event: E) -> None:
            assert self.current_index is not None
            w = self.window
            if w.render_info:
                self.current_index -= len(w.render_info.displayed_lines)

        @kb.add("pagedown")
        @wrapper
        def _pagedown(event: E) -> None:
            assert self.current_index is not None
            w = self.window
            if w.render_info:
                self.current_index += len(w.render_info.displayed_lines)

        @kb.add(" ")
        @kb.add("enter")
        def _enter(event: E) -> None:
            self.handle_accept()

        return kb

    def __pt_container__(self) -> Container:
        return self.window
