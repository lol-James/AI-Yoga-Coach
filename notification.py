from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer

class NotificationLabel(QLabel):
    def __init__(self, parent, message, success=True, duration=1000):
        super().__init__(parent)

        self.setText(message)
        self.setStyleSheet(
            f"""
            background-color: {'#28a745' if success else '#dc3545'}; 
            color: white;
            border-radius: 10px;
            padding: 8px 16px;
            font-weight: bold;
            font-family: Arial;
            font-size: 18px;
            """
        )
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(450, 50)
        self.move(20, 60)
        self.show()

        QTimer.singleShot(duration, self.hide)
