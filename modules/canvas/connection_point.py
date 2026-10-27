"""Connection point model for canvas elements."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectionPoint:
    """A named connection location in canvas coordinates."""

    side: str
    x: float
    y: float
