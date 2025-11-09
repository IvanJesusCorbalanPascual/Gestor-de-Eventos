import sys
import os
from PyQt5 import QtWidgets, uic
from ParticipanteManager import participante_manager

class CrearParticipante(QtWidgets.QMainWindow):
    # Pop-up para añadir un nuevo participante a un evento
    def __init__(self, gestion_evento_window, nombreEvento):
        super(CrearParticipante, self).__init__()

        # Guarda la referencia a la ventana de gestion del evento para actualizar la tabla
        self.gestion_evento_window = gestion_evento_window
        # Guarda el nombre del evento actual
        self.nombreEvento = nombreEvento

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "AñadirParticipante.ui")
        uic.loadUi(ui_path, self)
        
        # Conexiones de botones
        self.btnCrear.clicked.connect(self.crear_nuevo_participante)
        self.btnCancelar.clicked.connect(self.volver_gestion_evento)

    def volver_gestion_evento(self):
        # Cierra la ventana del pop-up
        self.close()

    def crear_nuevo_participante(self):
        # Obtener los datos del UI
        nombre = self.lneNombreParticipante.text().strip()
        acompanyantes = self.lneAcompanyantes.text().strip()
        no_sentar_con = self.lneNoSentarCon.text().strip()

        # Comprobacion minima de campos requeridos Nombre
        if not nombre:
            QtWidgets.QMessageBox.warning(self, "Error", "El nombre del participante no puede estar vacio")
            return

        # Guardar los datos en el CSV
        if participante_manager.guardar_participante(self.nombreEvento, nombre, acompanyantes, no_sentar_con):

            # Mostrar mensaje y actualizar la tabla en la ventana de gestion
            QtWidgets.QMessageBox.information(self, "Participante Creado", f"Participante '{nombre}' añadido al evento '{self.nombreEvento}'")
            
            # Llama al metodo de recarga de la ventana de gestion
            self.gestion_evento_window.cargar_participantes_en_tabla()
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Guardado", "No se pudo guardar el participante en la base de datos")