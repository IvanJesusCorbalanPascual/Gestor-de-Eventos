import sys
import os
from PyQt5 import QtWidgets, uic
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
        uic.loadUi(ui_path, self)
        
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

        # Comprobacion minima de campos requeridos: Nombre
        if not nombre:
            QtWidgets.QMessageBox.warning(self, "Error", "El nombre del participante no puede estar vacio")
            return

        # 1. Crea el objeto Participante (mesa_asignada es None por defecto)
        nuevo_participante = Participante(
            evento=self.nombreEvento, 
            nombre=nombre, 
            acompanyantes=acompanyantes, 
            no_sentar_con=no_sentar_con
        )
        
        # 2. Guardar el objeto en el CSV a través del manager
        if participante_manager.guardar_participante(nuevo_participante):

            # Mostrar mensaje y actualizar la tabla en la ventana de gestion
            QtWidgets.QMessageBox.information(self, "Participante Creado", f"Participante '{nombre}' añadido al evento '{self.nombreEvento}'")
            
            # Recargando la tabla con los participantes tras cada operacion
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
            self.gestion_evento_window.cargar_participantes_en_tabla()
            self.gestion_evento_window.refrescar_listas_mesas_tab()
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Actualización", "No se pudo actualizar el participante.")


class EliminarParticipante(QtWidgets.QDialog):
    def __init__(self, gestion_window, nombre_evento, nombre_participante):
        super(EliminarParticipante, self).__init__()

        self.gestion_evento_window = gestion_window
        self.nombre_participante = nombre_participante
        self.nombre_evento = nombre_evento

        # Carga la UI de EliminarParticipante
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        dir_padre = os.path.dirname(dir_actual)
        ui_path = os.path.join(dir_padre, "ui", "EliminarParticipante.ui")
        uic.loadUi(ui_path, self)

        self.seguroQueQuieresBorrar.setText(f"¿Seguro que quieres BORRAR a: {self.nombre_participante}?")
        self.setWindowTitle("Confirmar Eliminación")
        
        # Conexión de los botones
        self.btnCancelarEliminar.clicked.connect(self.volver_gestion) 
        self.btnBorrarParticipante.clicked.connect(self.confirmar_eliminacion)

    def volver_gestion(self):
        self.close()

    def confirmar_eliminacion(self):
        if participante_manager.eliminar_participante(self.nombre_evento, self.nombre_participante):
            
            QtWidgets.QMessageBox.information(self, "Participante Eliminado", f"Ha sido eliminado el participante: '{self.nombre_participante}' exitosamente.")
            
            # 6. Actualizar la tabla en la ventana de gestión
            self.gestion_evento_window.cargar_participantes_en_tabla()
            # 7. Refrescar también las listas de Drag&Drop
            self.gestion_evento_window.refrescar_listas_mesas_tab()
            
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se ha podido borrar al participante.")

    


    

