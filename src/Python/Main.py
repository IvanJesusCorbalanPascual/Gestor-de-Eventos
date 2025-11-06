import sys
import os
from PyQt5 import QtWidgets, uic

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "PantallaPrincipal.ui")
        uic.loadUi(ui_path, self)
        self.boxTema.currentTextChanged.connect(self.cambiar_tema)
    def cambiar_tema(self, tema):
        if tema == "Oscuro":
            self.setStyleSheet("""
                QMainWindow{background-color:#2d2d2d;}
                QWidget{background-color:#2d2d2d;color:#ffffff;}
                QTableWidget{background-color:#3c3c3c;color:#ffffff;}
                QHeaderView::section{background-color:#404040;color:#ffffff;}
                QPushButton{background-color:#555555;color:#ffffff;}
                QComboBox{background-color:#404040;color:#ffffff;}
                QLineEdit{background-color:#404040;color:#ffffff;}
                QMenuBar{background-color:#404040;color:#ffffff;}
            """)
        else:
            self.setStyleSheet("""
                QMainWindow{background-color:#ffffff;}
                QWidget{background-color:#ffffff;color:#000000;}
                QTableWidget{background-color:#ffffff;color:#000000;}
                QHeaderView::section{background-color:#e0e0e0;color:#000000;}
                QPushButton{background-color:#e0e0e0;color:#000000;}
                QComboBox{background-color:#ffffff;color:#000000;}
                QLineEdit{background-color:#ffffff;color:#000000;}
                QMenuBar{background-color:#f0f0f0;color:#000000;}
            """)
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()