"""Canvas element model."""

from dataclasses import dataclass

from modules.canvas.connection_point import ConnectionPoint


@dataclass(eq=False)
class Element:
    """A rectangular element positioned by its center in canvas coordinates."""

    x: float
    y: float
    width: float
    height: float
    selected: bool = False

    @property
    def connection_points(self) -> tuple[ConnectionPoint, ...]:
        """Return connection points centered on each side of the element."""
        half_width = self.width / 2
        half_height = self.height / 2
        return (
            ConnectionPoint("top", self.x, self.y - half_height),
            ConnectionPoint("right", self.x + half_width, self.y),
            ConnectionPoint("bottom", self.x, self.y + half_height),
            ConnectionPoint("left", self.x - half_width, self.y),
        )

    def contains(self, x: float, y: float) -> bool:
        """Return whether a canvas-coordinate point lies inside the element."""
        return (
            self.x - self.width / 2 <= x <= self.x + self.width / 2
            and self.y - self.height / 2 <= y <= self.y + self.height / 2
        )
