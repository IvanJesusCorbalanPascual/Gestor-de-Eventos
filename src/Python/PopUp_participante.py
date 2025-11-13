import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from ParticipanteManager import participante_manager
from Participante import Participante # Importando la clase Participante

class CrearParticipante(QtWidgets.QDialog):
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
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # Guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Crear Participante")
        
        # Mapeo de botones
        self.btnCrear.clicked.connect(self.crear_nuevo_participante)
        self.btnCancelar.clicked.connect(self.volver_gestion_evento)

    def volver_gestion_evento(self):
        # Cierra la ventana del pop-up
        self.close()

    def crear_nuevo_participante(self):
        # Obtener los datos pasados por el usuario
        nombre = self.lneNombreParticipante.text().strip()
        acompanyantes = self.lneAcompanyantes.text().strip()
        no_sentar_con = self.lneNoSentarCon.text().strip()

        # La comprobación minima de campos requeridos es ek binvre
        if not nombre:
            QtWidgets.QMessageBox.warning(self, "Error", "El nombre del participante no puede estar vacio")
            return

        # Crea el objeto Participante, siendo mesa_asignada None por defecto
        nuevo_participante = Participante(
            evento=self.nombreEvento, 
            nombre=nombre, 
            acompanyantes=acompanyantes, 
            no_sentar_con=no_sentar_con
        )
        
        # Guarda el objeto en el CSV a traves del manager
        if participante_manager.guardar_participante(nuevo_participante):

            # Muestra el mensaje y actualiza la tabla en la ventana de gestion
            QtWidgets.QMessageBox.information(self, "Participante Creado", f"Participante '{nombre}' añadido al evento '{self.nombreEvento}'")
            
            # Recarga la tabla con los participantes tras cada operacion
            self.gestion_evento_window.cargar_participantes_en_tabla()
            self.gestion_evento_window.refrescar_listas_mesas_tab()  
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Guardado", "No se pudo guardar el participante en la base de datos")


class ActualizarParticipante(QtWidgets.QDialog):
    def __init__(self, gestion_window, nombre_participante):
        super(ActualizarParticipante, self).__init__()

        self.gestion_evento_window = gestion_window
        self.nombre_participante_original = nombre_participante
        # Obtenemos el nombre del evento desde la ventana de gestion
        self.nombre_evento = gestion_window.nombreEvento

        # Carga la UI de ActualizarParticipante
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        dir_padre = os.path.dirname(dir_actual)
        icon_path = os.path.join(dir_padre,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        ui_path = os.path.join(dir_padre, "ui", "ActualizarParticipante.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle(f"Actualizar Participante: {nombre_participante}")

        # Carga los datos actuales al iniciar
        self.cargar_datos_actuales()
        
        # Conexion de los botones
        self.btnPopupCancelarActualizacionParticipante.clicked.connect(self.volver_gestion)
        self.btnPopupActualizarParticipante.clicked.connect(self.confirmar_actualizacion)

    def cargar_datos_actuales(self):
        participante_obj = participante_manager.buscar_participante(
            self.nombre_evento, 
            self.nombre_participante_original
        )
        
        if participante_obj:
            self.lneActualizarNombreParticipante.setText(participante_obj.nombre) 
            self.lneActualizarAcompanyantes.setText(participante_obj.acompanyantes)
            self.lneActualizarNoSentarCon.setText(participante_obj.no_sentar_con)
            
            # Guardamos el objeto para referencia futura
            self.participante_actual = participante_obj 
            
            self.setWindowTitle(f"Actualizar: {self.nombre_participante_original}")
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Carga", "No se encontro el participante para actualizar")
            self.close()

    def volver_gestion(self):
            self.close()

    def confirmar_actualizacion(self):
        # Obtiene los nuevos datos del UI
        nuevoNombre = self.lneActualizarNombreParticipante.text().strip()
        nuevosAcompanyantes = self.lneActualizarAcompanyantes.text().strip()
        nuevosNoSentarCon = self.lneActualizarNoSentarCon.text().strip()
        
        # Validacion minima
        if not nuevoNombre:
            QtWidgets.QMessageBox.warning(self, "Error", "El nombre del participante no puede estar vacio")
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
            
            QtWidgets.QMessageBox.information(self, "Actualizacion Exitosa", f"Participante '{self.nombre_participante_original}' actualizado a '{nuevoNombre}'")
            
            # Recargar la tabla en la ventana de gestion de eventos
            self.gestion_evento_window.cargar_participantes_en_tabla()
            self.gestion_evento_window.refrescar_listas_mesas_tab()
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Actualizacion", "No se pudo actualizar el participante")


class EliminarParticipante(QtWidgets.QDialog):
    def __init__(self, gestion_window, nombre_evento, nombre_participante):
        super(EliminarParticipante, self).__init__()

        self.gestion_evento_window = gestion_window
        self.nombre_participante = nombre_participante
        self.nombre_evento = nombre_evento

        # Carga la UI de EliminarParticipante
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        dir_padre = os.path.dirname(dir_actual)
        icon_path = os.path.join(dir_padre,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        ui_path = os.path.join(dir_padre, "ui", "EliminarParticipante.ui")
        uic.loadUi(ui_path, self)

        self.seguroQueQuieresBorrar.setText(f"¿Seguro que quieres BORRAR a: {self.nombre_participante}?")
        self.setWindowTitle("Confirmar Eliminacion")
        
        # Conexion de los botones
        self.btnCancelarEliminar.clicked.connect(self.volver_gestion) 
        self.btnBorrarParticipante.clicked.connect(self.confirmar_eliminacion)

    def volver_gestion(self):
        self.close()

    def confirmar_eliminacion(self):
        if participante_manager.eliminar_participante(self.nombre_evento, self.nombre_participante):
            
            QtWidgets.QMessageBox.information(self, "Participante Eliminado", f"Ha sido eliminado el participante: '{self.nombre_participante}' exitosamente")
            
            # Actualizar la tabla en la ventana de gestion
            self.gestion_evento_window.cargar_participantes_en_tabla()
            # Refrescar tambien las listas de Drag&Drop
            self.gestion_evento_window.refrescar_listas_mesas_tab()
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se ha podido borrar al participante")