"""Graphics scene for the canvas."""

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtWidgets import QGraphicsScene


class Scene(QGraphicsScene):
    """Scene containing the default 10-by-10 canvas square."""

    def __init__(self, parent=None):
        """Initialize the scene and add its default square."""
        super().__init__(parent)
        self.square = QRectF(0, 0, 10, 10)
        self.addRect(
            self.square,
            QPen(Qt.GlobalColor.black),
            QBrush(Qt.GlobalColor.white),
        )
        self.setSceneRect(-1, -1, 12, 12)
