import sys
import os
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QDateTime
from EventoManager import event_manager
from Evento import Evento 
from ParticipanteManager import participante_manager 
from Participante import Participante


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
        # El manager devuelve un objeto Evento o None
        evento_obj = event_manager.buscar_evento(self.nombre_evento_original) 

        if evento_obj:
            # Usamos los atributos del objeto Evento
            self.lneNuevoNombreEvento.setText(evento_obj.nombre)
            self.lneActualizarUbicacionEvento.setText(evento_obj.ubicacion)
            self.lneActualizarOrganizador.setText(evento_obj.organizador)
            self.lneActualizarMesas.setText(evento_obj.num_mesas) 

            # Convierte la fecha de un String a formato QDateTime usando la constante de la clase Evento
            fechaDt = QDateTime.fromString(evento_obj.fecha, Evento.DATE_FORMAT) 
            self.dateTimeEventoActualizar.setDateTime(fechaDt)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No se han podido cargar los datos del evento")
            self.close()

    def volver_principal(self):
        self.close()

    def confirmar_actualizacion(self):
        # Obtiene los nuevos datos del UI
        nuevoNombre = self.lneNuevoNombreEvento.text()
        # Usa la constante de la clase Evento
        nuevaFecha = self.dateTimeEventoActualizar.dateTime().toString(Evento.DATE_FORMAT) 
        nuevaUbicacion = self.lneActualizarUbicacionEvento.text()
        nuevoOrganizador = self.lneActualizarOrganizador.text()
        nuevoNumMesas = self.lneActualizarMesas.text()

        # Comprueba que los campos no estan vacios
        if not all([nuevoNombre, nuevaUbicacion, nuevoOrganizador]):
            QtWidgets.QMessageBox.warning(self, "Error", "Debes completar todos los campos, intentalo de nuevo.")
            return
        
        # Almacena los nuevos datos en una lista para el manager
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
        # Usamos la constante de la clase Evento
        fecha_obj = self.dateFechaEvento.dateTime().toString(Evento.DATE_FORMAT) 
        ubicacion = self.lneUbicacion.text()
        organizador = self.lneOrganizador.text()
        num_mesas_str = self.lneNumMesas.text().strip()
        try:
            # Intentamos convertir el texto a un número entero
            num_mesas = int(num_mesas_str)
 
            if num_mesas <= 0:
                raise ValueError("El número debe ser positivo")
            print(f"Número de mesas válido: {num_mesas}")

        except ValueError:

            QtWidgets.QMessageBox.warning(self, "Error de validación", 
                                          "Por favor, introduce un número de mesas válido")
            return

        # Error si no estan los datos
        if not all([nombre, ubicacion, organizador]):
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, complete todos los campos")
            return

        # 1. Creamos el objeto Evento
        nuevo_evento = Evento(nombre, fecha_obj, ubicacion, organizador, num_mesas)
        
        # 2. Guardar el objeto en el CSV a través del manager
        if event_manager.guardar_evento(nuevo_evento):

            # Actualizar la tabla de la ventana principal
            self.main_window.cargar_eventos_en_tabla()

            # Cerrar la ventana después de crear el evento
            QtWidgets.QMessageBox.information(self, "Evento Creado", f"Evento '{nombre}' creado y guardado.")
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Guardado", "No se pudo guardar el evento en la base de datos.")


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
