"""Configurable numeric settings for the canvas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CanvasSettings:
    """Numeric canvas settings loaded from the application configuration."""

    grid_spacing_horizontal: int = 200
    grid_spacing_vertical: int = 400
    minimum_grid_zoom: float = 0.2
    element_size: int = 800
    element_pen_width: float = 5.0
    connection_point_size: int = 24
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
            connection_point_size=int(config.get(
                "Canvas", "connection_point_size",
                str(defaults.connection_point_size),
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
            or settings.connection_point_size <= 0
            or settings.zoom_factor <= 1
            or settings.minimum_zoom <= 0
            or settings.maximum_zoom <= settings.minimum_zoom
        ):
            raise ValueError("Canvas numeric settings must be positive and valid.")
        return settings
