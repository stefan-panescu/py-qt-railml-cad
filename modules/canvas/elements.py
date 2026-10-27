"""Canvas element model."""

from dataclasses import dataclass


@dataclass(eq=False)
class Element:
    """A rectangular element positioned by its center in canvas coordinates."""

    x: float
    y: float
    width: float
    height: float

    def contains(self, x: float, y: float) -> bool:
        """Return whether a canvas-coordinate point lies inside the element."""
        return (
            self.x - self.width / 2 <= x <= self.x + self.width / 2
            and self.y - self.height / 2 <= y <= self.y + self.height / 2
        )
