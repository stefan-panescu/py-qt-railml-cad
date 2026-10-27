"""Business logic for canvas elements."""

from modules.canvas.canvas_settings import CanvasSettings
from modules.canvas.element import Element


class CanvasModel:
    """Manage canvas elements and coordinate snapping independently of Qt."""

    def __init__(self, settings=None):
        self.settings = settings or CanvasSettings()
        self.elements = []

    def snapped_position(self, x: float, y: float) -> tuple[float, float]:
        """Snap a coordinate to the configured grid intersection."""
        return (
            round(x / self.settings.grid_spacing_horizontal)
            * self.settings.grid_spacing_horizontal,
            round(y / self.settings.grid_spacing_vertical)
            * self.settings.grid_spacing_vertical,
        )

    def add_element(self, x: float, y: float) -> Element:
        """Create and store an element centered at the snapped position."""
        center_x, center_y = self.snapped_position(x, y)
        element = Element(
            center_x,
            center_y,
            self.settings.element_size,
            self.settings.element_size,
        )
        self.elements.append(element)
        return element

    def element_at(self, x: float, y: float):
        """Return the topmost element at a coordinate, if any."""
        return next(
            (element for element in reversed(self.elements) if element.contains(x, y)),
            None,
        )

    def move_element(self, element: Element, x: float, y: float) -> None:
        """Move an element to the nearest configured grid intersection."""
        element.x, element.y = self.snapped_position(x, y)

    def delete_element(self, element: Element) -> bool:
        """Remove an element from the canvas model."""
        if element not in self.elements:
            return False
        self.elements.remove(element)
        return True
