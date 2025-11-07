import sys
import os
from PyQt5 import QtWidgets, uic

class ActualizarEvento(QtWidgets.QMainWindow):
    def __init__(self):
        super(ActualizarEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "ActualizarEvento.ui")
        uic.loadUi(ui_path, self)
        self.btnCancelarActualizacion.clicked.connect(self.volver_principal)

    def volver_principal(self):
        self.close()

class CrearEvento(QtWidgets.QMainWindow):
    def __init__(self):
        super(CrearEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "CrearEvento.ui")
        uic.loadUi(ui_path, self)
        print("Creando evento...")

class EliminarEvento(QtWidgets.QMainWindow):
    def __init__(self):
        super(EliminarEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "EliminarEvento.ui")
        uic.loadUi(ui_path, self)
        self.btnCancelarEliminar.clicked.connect(self.volver_principal)

    def volver_principal(self):
        self.close()