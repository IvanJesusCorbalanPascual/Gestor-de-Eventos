import sys
import os
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QDateTime
from EventoManager import event_manager
from Evento import Evento 
from ParticipanteManager import participante_manager 
from Participante import Participante

# La clase ActualizarEvento sigue usando Evento.DATE_FORMAT
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
            # Si falta un campo. muestra una advertencia y detiene la ejecucion
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
        num_mesas = self.lneNumMesas.text()

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

class ActualizarParticipante(QtWidgets.QMainWindow):
    def __init__(self, gestion_window, nombre_participante):
        super(ActualizarParticipante, self).__init__()

        self.gestion_window = gestion_window
        self.nombre_participante_original = nombre_participante
        # Obtenemos el nombre del evento desde la ventana de gestión
        self.nombre_evento = gestion_window.nombreEvento

        # Carga la UI de ActualizarParticipante
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        dir_padre = os.path.dirname(dir_actual)
        ui_path = os.path.join(dir_padre, "ui", "ActualizarParticipante.ui")
        uic.loadUi(ui_path, self)

        # 1. Cargamos los datos actuales al iniciar
        self.cargar_datos_actuales()
        
        # Conexión de los botones
        self.btnPopupCancelarActualizacionParticipante.clicked.connect(self.volver_gestion)
        self.btnPopupActualizarParticipante.clicked.connect(self.confirmar_actualizacion)

    # Nuevo método para cargar los datos del participante
    def cargar_datos_actuales(self):
        participante_obj = participante_manager.buscar_participante(
            self.nombre_evento, 
            self.nombre_participante_original
        )
        
        if participante_obj:
            # Asumiendo que tu UI tiene lneNombreParticipante, lneAcompanyantes, lneNoSentarCon
            self.lneNombreParticipante.setText(participante_obj.nombre)
            self.lneAcompanyantes.setText(participante_obj.acompanyantes)
            self.lneNoSentarCon.setText(participante_obj.no_sentar_con)
            # Guardamos el objeto para referencia futura si fuera necesario
            self.participante_actual = participante_obj 
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Carga", "No se encontró el participante para actualizar.")
            self.close()

    def volver_gestion(self):
            self.close()

    # Lógica de actualización implementada
class ActualizarParticipante(QtWidgets.QMainWindow):
    def __init__(self, gestion_window, nombre_participante):
        super(ActualizarParticipante, self).__init__()

        self.gestion_window = gestion_window
        self.nombre_participante_original = nombre_participante
        # Obtenemos el nombre del evento desde la ventana de gestión
        self.nombre_evento = gestion_window.nombreEvento

        # Carga la UI de ActualizarParticipante
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        dir_padre = os.path.dirname(dir_actual)
        ui_path = os.path.join(dir_padre, "ui", "ActualizarParticipante.ui")
        uic.loadUi(ui_path, self)

        # 1. Cargamos los datos actuales al iniciar
        self.cargar_datos_actuales()
        
        # Conexión de los botones
        self.btnPopupCancelarActualizacionParticipante.clicked.connect(self.volver_gestion)
        self.btnPopupActualizarParticipante.clicked.connect(self.confirmar_actualizacion)

    def cargar_datos_actuales(self):
        participante_obj = participante_manager.buscar_participante(
            self.nombre_evento, 
            self.nombre_participante_original
        )
        
        if participante_obj:
            # CORRECCIÓN: Usar los nombres de widgets del UI: lneActualizarNombreParticipante, etc.
            self.lneActualizarNombreParticipante.setText(participante_obj.nombre) 
            self.lneActualizarAcompanyantes.setText(participante_obj.acompanyantes)
            self.lneActualizarNoSentarCon.setText(participante_obj.no_sentar_con)
            
            # Guardamos el objeto para referencia futura (p.ej., para obtener la mesa asignada)
            self.participante_actual = participante_obj 
            
            # Opcional: Mostrar el nombre original en el título
            self.setWindowTitle(f"Actualizar: {self.nombre_participante_original}")
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Carga", "No se encontró el participante para actualizar.")
            self.close()

    def volver_gestion(self):
            self.close()

    def confirmar_actualizacion(self):
        # Obtener los nuevos datos del UI, usando los nombres corregidos
        nuevoNombre = self.lneActualizarNombreParticipante.text().strip()
        nuevosAcompanyantes = self.lneActualizarAcompanyantes.text().strip()
        nuevosNoSentarCon = self.lneActualizarNoSentarCon.text().strip()
        
        # Validación mínima
        if not nuevoNombre:
            QtWidgets.QMessageBox.warning(self, "Error", "El nombre del participante no puede estar vacío.")
            return

        # Preparamos la lista de datos para el manager
        # Usamos el objeto existente para obtener el evento y la mesa asignada
        mesa_asignada_str = str(self.participante_actual.mesa_asignada) if self.participante_actual.mesa_asignada else ''
        
        nuevos_datos_list = [
            self.nombre_evento,            
            nuevoNombre,                  
            nuevosAcompanyantes,          
            nuevosNoSentarCon,            
            mesa_asignada_str              
        ]
        
        # Llamar al manager para actualizar en el CSV
        if participante_manager.actualizar_participante(self.nombre_evento, self.nombre_participante_original, nuevos_datos_list):
            
            QtWidgets.QMessageBox.information(self, "Actualización Exitosa", f"Participante '{self.nombre_participante_original}' actualizado a '{nuevoNombre}'.")
            
            # Recargar la tabla en la ventana de gestión de eventos
            self.gestion_window.cargar_participantes_en_tabla()
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Actualización", "No se pudo actualizar el participante.")