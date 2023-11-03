"""Vertical menu widget for prompt-toolkit"""

from typing import TYPE_CHECKING, Any, Dict, Iterable, Iterator, NewType, Optional, cast

from prompt_toolkit.data_structures import Point
from prompt_toolkit.filters import FilterOrBool, to_filter
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding.key_bindings import KeyBindingsBase
from prompt_toolkit.layout.controls import GetLinePrefixCallable, UIContent, UIControl
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

if TYPE_CHECKING:
    from prompt_toolkit.key_binding.key_bindings import NotImplementedOrNone

Item = tuple[str, Any]
Index = NewType("Index", int)


class VertMenuUIControl(UIControl):
    """UIControl optimized for VertMenu"""

    def __init__(
        self,
        items: Iterable[Item],
        focusable: FilterOrBool = True,
        key_bindings: Optional[KeyBindingsBase] = None,
    ):
        self._items = tuple(items)
        self._selected: Index = Index(0)
        self.focusable = to_filter(focusable)
        self.key_bindings = key_bindings
        self._width = 30
        # Mark if the last movement we did was down:
        self._moved_down = False
        # ^ We use this to show the complete label of the item at the
        # bottom of the screen when it's the selected one.
        self._lineno_to_index: Dict[int, Index] = {}
        self._index_to_lineno: Dict[Index, int] = {}
        self._gen_lineno_mappings()

    def _items_enumerate(self) -> Iterator[tuple[Index, Item]]:
        for index, item in enumerate(self._items):
            yield Index(index), item

    def _gen_lineno_mappings(self) -> None:
        # Create the lineno <-> item mappings:
        self._lineno_to_index.clear()
        self._index_to_lineno.clear()
        lineno = 0
        self._width = 30
        for index, item in self._items_enumerate():
            self._index_to_lineno[Index(index)] = lineno
            for line in item[0].split("\n"):
                self._lineno_to_index[lineno] = index
                lineno += 1
                self._width = max(self._width, len(line))

    @property
    def items(self) -> tuple[Item, ...]:
        return self._items

    @items.setter
    def items(self, items: Iterable[Item]) -> None:
        previous = None
        if self._items:
            previous = self._items[self._selected]
        self._items = tuple(items)
        self._selected = Index(0)
        self._moved_down = False
        self._gen_lineno_mappings()
        if previous is None:
            return
        # We keep the same selected item, if possible:
        try:
            self.selected_item = previous
        except IndexError:
            pass

    @property
    def selected(self) -> int:
        return cast(int, self._selected)

    @selected.setter
    def selected(self, selected: int) -> None:
        previous = self._selected
        selected = max(0, selected)
        selected = min(selected, len(self._items) - 1)
        self._selected = Index(selected)
        self._moved_down = self._selected > previous

    @property
    def selected_item(self) -> Optional[Item]:
        if not self._items:
            return None
        return self._items[self._selected]

    @selected_item.setter
    def selected_item(self, item: Item) -> None:
        for index, current in self._items_enumerate():
            if current == item:
                self._selected = index
                return
        raise IndexError

    def preferred_width(self, max_available_width: int) -> Optional[int]:
        return self._width

    def preferred_height(
        self,
        width: int,
        max_available_height: int,
        wrap_lines: bool,
        get_line_prefix: Optional[GetLinePrefixCallable],
    ) -> Optional[int]:
        return len(self._lineno_to_index)

    def is_focusable(self) -> bool:
        return self.focusable()

    def _get_line(self, lineno: int) -> StyleAndTextTuples:
        index = self._lineno_to_index[lineno]
        item = self._items[index]
        itemlines = item[0].split("\n")
        line = itemlines[lineno - self._index_to_lineno[index]]
        if self.selected_item == item:
            return [("class:vertmenu.selected", line)]
        else:
            return [("class:vertmenu.item", line)]

    def _cursor_position(self) -> Point:
        item = self.selected_item
        if item is None:
            return Point(x=0, y=0)
        lineno = self._index_to_lineno[self._selected]
        if self._moved_down:
            # Put the cursor in the last line of a multi-line item if
            # we have moved down to show the full label if it is at
            # the bottom of the screen:
            while self._lineno_to_index.get(lineno + 1) == self.selected:
                lineno += 1
        return Point(x=0, y=lineno)

    def create_content(self, width: int, height: int) -> UIContent:
        return UIContent(
            get_line=self._get_line,
            line_count=len(self._lineno_to_index),
            show_cursor=False,
            cursor_position=self._cursor_position(),
        )

    def mouse_handler(self, mouse_event: MouseEvent) -> "NotImplementedOrNone":
        if mouse_event.event_type != MouseEventType.MOUSE_DOWN:
            return NotImplemented
        index = self._lineno_to_index.get(mouse_event.position.y)
        if index is not None:
            self.selected = index
        return None

    def move_cursor_down(self) -> None:
        self.selected += 1
        # Unmark _moved_down because this is only called when the
        # cursor is at the top:
        self._moved_down = False

    def move_cursor_up(self) -> None:
        self.selected -= 1
        # Mark _moved_down because this called when the cursor is at
        # the bottom:
        self._moved_down = True

    def get_key_bindings(self) -> Optional[KeyBindingsBase]:
        return self.key_bindings
