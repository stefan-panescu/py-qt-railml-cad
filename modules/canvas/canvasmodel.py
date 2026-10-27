"""Canvas settings and element business logic."""

from dataclasses import dataclass

from modules.canvas.elements import Element


@dataclass(frozen=True)
class CanvasSettings:
    """Numeric canvas settings loaded from the application configuration."""

    grid_spacing_horizontal: int = 200
    grid_spacing_vertical: int = 400
    minimum_grid_zoom: float = 0.2
    element_size: int = 800
    element_pen_width: float = 5.0
    zoom_factor: float = 1.15
    minimum_zoom: float = 0.01
    maximum_zoom: float = 20.0

    @classmethod
    def from_config(cls, config):
        """Load and validate canvas settings from a Config-like object."""
        defaults = cls()
        settings = cls(
            grid_spacing_horizontal=int(config.get(
                "Canvas", "grid_spacing_horizontal",
                str(defaults.grid_spacing_horizontal),
            )),
            grid_spacing_vertical=int(config.get(
                "Canvas", "grid_spacing_vertical",
                str(defaults.grid_spacing_vertical),
            )),
            minimum_grid_zoom=float(config.get(
                "Canvas", "minimum_grid_zoom",
                str(defaults.minimum_grid_zoom),
            )),
            element_size=int(config.get(
                "Canvas", "element_size", str(defaults.element_size),
            )),
            element_pen_width=float(config.get(
                "Canvas", "element_pen_width",
                str(defaults.element_pen_width),
            )),
            zoom_factor=float(config.get(
                "Canvas", "zoom_factor", str(defaults.zoom_factor),
            )),
            minimum_zoom=float(config.get(
                "Canvas", "minimum_zoom", str(defaults.minimum_zoom),
            )),
            maximum_zoom=float(config.get(
                "Canvas", "maximum_zoom", str(defaults.maximum_zoom),
            )),
        )
        if (
            settings.grid_spacing_horizontal <= 0
            or settings.grid_spacing_vertical <= 0
            or settings.minimum_grid_zoom <= 0
            or settings.element_size <= 0
            or settings.element_pen_width <= 0
            or settings.zoom_factor <= 1
            or settings.minimum_zoom <= 0
            or settings.maximum_zoom <= settings.minimum_zoom
        ):
            raise ValueError("Canvas numeric settings must be positive and valid.")
        return settings


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

    def geometry_at(self, x: float, y: float, element=None):
        """Return the snapped top-left and size for a new or moved element."""
        center_x, center_y = self.snapped_position(x, y)
        width = element.width if element is not None else self.settings.element_size
        height = element.height if element is not None else self.settings.element_size
        return (
            center_x - width / 2,
            center_y - height / 2,
            width,
            height,
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
