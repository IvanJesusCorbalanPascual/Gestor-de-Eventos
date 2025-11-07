import sys
import os
from PyQt5 import QtWidgets
from Pantalla_Principal import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    print("Abriendo el progama...")

if __name__ == "__main__":
    main()