import sys
import os
from PyQt5 import QtWidgets, uic
from EventoManager import event_manager

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
    def __init__(self, nombreEvento, mainWindow):
        super(EliminarEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "EliminarEvento.ui")
        uic.loadUi(ui_path, self)

        self.nombreEvento = nombreEvento
        self.mainWindow = mainWindow

        # Personalizamos el QLabel con el mensaje de confirmación
        self.seguroQueQuieresBorrar.setText(f"¿Seguro que quieres BORRAR '{self.nombreEvento}' ?")

        self.btnCancelarEliminar.clicked.connect(self.volver_principal)
        self.btnBorrar.clicked.connect(self.confirmar_eliminacion)

    def volver_principal(self):
        self.close()

    def confirmar_eliminacion(self):
        # Eliminados el evento del CSV llamando al manager
        if event_manager.eliminar_evento(self.nombreEvento):

            # Muestra un mensaje mostrando que ha funcionado
            QtWidgets.QMessageBox.information(self, "Evento Eliminado", f"Se ha eliminado el evento '{self.nombreEvento}' exitosamente.")

            # Actualiza la tabla en la ventana principal
            self.mainWindow.cargar_eventos_en_tabla()

            self.close()

        else:
            QtWidgets.QMessageBox.critical(self, "Error al eliminar", f"No se ha podido borrar el evento.")