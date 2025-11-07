import sys
import os
from PyQt5 import QtWidgets, uic

class GestionEvento(QtWidgets.QMainWindow):
    
    # Metodo para inciar la pantalla
    def __init__(self):
        super(GestionEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "GestionDeEventos.ui")
        uic.loadUi(ui_path, self)
        self.btnVolver.clicked.connect(self.volver_principal)
        print("Consultando evento...")
        
    # Metodo para volver a la pantalla principal    
    def volver_principal(self):
        from Pantalla_Principal import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
        print("Volviendo a la pantalla principal...")