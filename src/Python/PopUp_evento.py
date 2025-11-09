import sys
import os
from PyQt5 import QtWidgets, uic
from EventoManager import event_manager

class ActualizarEvento(QtWidgets.QMainWindow):
    def __init__(self, main_window=None):
        super(ActualizarEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "ActualizarEvento.ui")
        uic.loadUi(ui_path, self)
        self.btnPopupCancelarActualizacionEvento.clicked.connect(self.volver_principal)

    def volver_principal(self):
        self.close()

class CrearEvento(QtWidgets.QMainWindow):
    def __init__(self, main_window): 
        super(CrearEvento, self).__init__()
        self.main_window = main_window
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "CrearEvento.ui") 
        uic.loadUi(ui_path, self)
        self.btnCrearEvento.clicked.connect(self.crear_nuevo_evento)
        self.btnCancelar.clicked.connect(self.volver_principal)

    def volver_principal(self):
        # Cierra la ventana pop-up de creacion de evento
        self.close()

    def crear_nuevo_evento(self):
        # Obtener los datos del UI
        nombre = self.lneNombreEvento.text()
        fecha_obj = self.dateFechaEvento.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        ubicacion = self.lneUbicacion.text()
        organizador = self.lneOrganizador.text()
        num_mesas = self.lneNumMesas.text()
        
        # Error si no estan los datos
        if not all([nombre, ubicacion, organizador]):
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, complete todos los campos")
            return

        # Guardar los datos en el CSV
        datos_evento = [nombre, fecha_obj, ubicacion, organizador, num_mesas]
        if event_manager.guardar_evento(datos_evento):
            
            # Actualizar la tabla de la ventana principal
            self.main_window.cargar_eventos_en_tabla()
            
            # Cerrar la ventana después de crear el evento
            QtWidgets.QMessageBox.information(self, "Evento Creado", f"Evento '{nombre}' creado y guardado.")
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Guardado")

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