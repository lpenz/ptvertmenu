"""Vertical menu widget for prompt-toolkit"""

from functools import wraps
from typing import Callable, Iterable, Optional

from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, Window

from .vertmenuuicontrol import Item, VertMenuUIControl

E = KeyPressEvent


class VertMenu:
    def __init__(
        self,
        items: Iterable[Item],
        selected_item: Optional[Item] = None,
        selected_handler: Optional[Callable[[Optional[Item]], None]] = None,
        accept_handler: Optional[Callable[[Item], None]] = None,
        focusable: bool = True,
    ):
        self.selected_handler = selected_handler
        self.accept_handler = accept_handler
        self.control = VertMenuUIControl(
            items, focusable=focusable, key_bindings=self._init_key_bindings()
        )
        self.window = Window(self.control, width=30, style=self.get_style)
        if selected_item is not None:
            self.control.selected_item = selected_item
        self.handle_selected()

    def _init_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        def wrapper(func: Callable[[E], None]) -> Callable[[E], None]:
            @wraps(func)
            def inner(event: E) -> None:
                if not self.control.items:
                    return
                previous = self.control.selected_item
                func(event)
                if self.control.selected_item != previous:
                    self.handle_selected()

            return inner

        @kb.add("c-home")
        @kb.add("escape", "home")
        @kb.add("c-pageup")
        @wrapper
        def _first(event: E) -> None:
            self.control.selected = 0

        @kb.add("c-end")
        @kb.add("escape", "end")
        @kb.add("c-pagedown")
        @wrapper
        def _last(event: E) -> None:
            self.control.selected = len(self.control.items) - 1

        @kb.add("up")
        @wrapper
        def _up(event: E) -> None:
            self.control.selected -= 1

        @kb.add("down")
        @wrapper
        def _down(event: E) -> None:
            self.control.selected += 1

        @kb.add("pageup")
        @wrapper
        def _pageup(event: E) -> None:
            w = self.window
            if w.render_info:
                self.control.selected -= len(w.render_info.displayed_lines)

        @kb.add("pagedown")
        @wrapper
        def _pagedown(event: E) -> None:
            w = self.window
            if w.render_info:
                self.control.selected += len(w.render_info.displayed_lines)

        @kb.add(" ")
        @kb.add("enter")
        def _enter(event: E) -> None:
            self.handle_accept()

        return kb

    def get_style(self) -> str:
        if get_app().layout.has_focus(self.window):
            return "class:vertmenu.focused"
        else:
            return "class:vertmenu.unfocused"

    def handle_selected(self) -> None:
        if self.selected_handler is not None:
            self.selected_handler(self.control.selected_item)

    def handle_accept(self) -> None:
        if self.accept_handler is not None and self.control.selected_item is not None:
            self.accept_handler(self.control.selected_item)

    def __pt_container__(self) -> Container:
        return self.window


__all__ = [
    "VertMenu",
    "Item",
]