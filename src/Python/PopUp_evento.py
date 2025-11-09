import sys
import os
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QDateTime
from EventoManager import event_manager

class ActualizarEvento(QtWidgets.QMainWindow):
    # Permite modificar un evento existente
    def __init__(self, main_window, nombreEvento):
        super(ActualizarEvento, self).__init__()

        self.main_window = main_window
        self.nombre_evento_original = nombreEvento

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "ActualizarEvento.ui")
        uic.loadUi(ui_path, self)
        self.btnPopupCancelarActualizacionEvento.clicked.connect(self.volver_principal)
        self.setWindowTitle("Actualizar evento")

        self.lblNombreEvento.setText(self.nombre_evento_original)
        
        # Conecta el botón 'Actualizar' a la función 'confirmar_actualizacion'
        self.btnPopupActualizarEvento.clicked.connect(self.confirmar_actualizacion)

        try:
            self.btnPopupCancelarActualizacionEvento.clicked.connect(self.volver_principal)
        except AttributeError:
            self.btnCancelarActualizacion.clicked.connect(self.volver_principal)
        
        self.cargar_datos_actuales()

    # Rellena con los datos actuales los campos
    def cargar_datos_actuales(self):
        datos = event_manager.buscar_evento(self.nombre_evento_original)

        if datos:
            self.lneNuevoNombreEvento.setText(datos[0])
            self.lneActualizarUbicacionEvento.setText(datos[2])
            self.lneActualizarOrganizador.setText(datos[3])
            self.lneActualizarMesas.setText(datos[4]) 

            # Convierte la fecha de un String a formato QDateTime
            fechaDt = QDateTime.fromString(datos[1], "yyyy-MM-dd hh:mm:ss")
            self.dateTimeEventoActualizar.setDateTime(fechaDt)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No se han podido cargar los datos del evento")
            self.close()

    def volver_principal(self):
        self.close()

    def confirmar_actualizacion(self):
        # Obtiene los nuevos datos del UI
        nuevoNombre = self.lneNuevoNombreEvento.text()
        nuevaFecha = self.dateTimeEventoActualizar.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        nuevaUbicacion = self.lneActualizarUbicacionEvento.text()
        nuevoOrganizador = self.lneActualizarOrganizador.text()
        nuevoNumMesas = self.lneActualizarMesas.text()

        # Comprueba que los campos no estan vacios
        if not all([nuevoNombre, nuevaUbicacion, nuevoOrganizador]):
            # Si falta un campo. muestra una advertencia y detiene la ejecucion
            QtWidgets.QMessageBox.warning(self, "Error", "Debes completar todos los campos, intentalo de nuevo.")
            return
        
        # Almacena los nuevos datos
        nuevos_datos_evento = [nuevoNombre, nuevaFecha, nuevaUbicacion, nuevoOrganizador, nuevoNumMesas]

        # Llama al manager para intentar actualizar el CSV
        if event_manager.actualizar_evento(self.nombre_evento_original, nuevos_datos_evento):

            self.main_window.cargar_eventos_en_tabla()

            QtWidgets.QMessageBox.information(self, "Evento Actualizado", f"El evento '{nuevoNombre}' ha sido actualizado.")
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No ha sido posible actualizar el evento.")

class CrearEvento(QtWidgets.QMainWindow):
    def __init__(self, main_window):
        super(CrearEvento, self).__init__()

        #  Guarda main_window para usarlo en otras funciones
        self.main_window = main_window

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "CrearEvento.ui")
        uic.loadUi(ui_path, self)
        print("Creando evento...")

        self.btnCrearEvento.clicked.connect(self.crear_nuevo_evento)
        self.btnCancelar.clicked.connect(self.volver_principal)

    def volver_principal(self):
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

class ActualizarParticipante(QtWidgets.QMainWindow):
    def __init__(self, gestion_window, nombre_participante):
        super(ActualizarParticipante, self).__init__()

        self.gestion_window = gestion_window
        self.nombre_participante_original = nombre_participante

        # Carga la UI de ActualizarParticipante
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        dir_padre = os.path.dirname(dir_actual)
        ui_path = os.path.join(dir_padre, "ui", "ActualizarParticipante.ui")
        uic.loadUi(ui_path, self)

        # Conexión de los botones
        self.btnPopupCancelarActualizacionParticipante.clicked.connect(self.volver_gestion)
        self.btnPopupActualizarParticipante.clicked.connect(self.confirmar_actualizacion)

    def volver_gestion(self):
            self.close()

    def confirmar_actualizacion(self):
        QtWidgets.QMessageBox.information(self, "Pendiente", "Lógica para actualizar participante aún no implementada.")
        self.close()
