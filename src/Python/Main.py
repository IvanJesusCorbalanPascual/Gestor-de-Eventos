import sys
import os
from PyQt5 import QtWidgets
from Pantalla_Principal import MainWindow
import imagenes_rc

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()