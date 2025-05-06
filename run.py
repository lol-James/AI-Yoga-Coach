from main import AIYogaCoachApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIYogaCoachApp()
    window.show()
    sys.exit(app.exec_())