import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QDialog
from EventoManager import event_manager
from ParticipanteManager import participante_manager

# Ruta base para cargar las UI, asumiendo que 'ui' esta en el directorio padre
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
UI_DIR = os.path.join(parent_dir, "ui")

class AnyadirMesa(QtWidgets.QDialog):
    """Pop-up para aumentar el numero de mesas de un evento."""
    def __init__(self, gestion_window):
        super(AnyadirMesa, self).__init__()
        
        self.gestion_evento_window = gestion_window
        self.nombre_evento = gestion_window.nombreEvento
        self.evento_obj = gestion_window.evento_obj # Objeto Evento actual
        
        # Carga de la UI
        ui_path = os.path.join(UI_DIR, "AnyadirMesa.ui")
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        try:
             uic.loadUi(ui_path, self)
        except FileNotFoundError:
             QMessageBox.critical(self, "Error de UI", f"No se encontro el archivo de UI en: {ui_path}")
             self.close()
             return

        self.setWindowTitle(f"Anyadir Mesas a: {self.nombre_evento}")
        
        # Mapeo de botones (Ajustar nombres si tu UI tiene otros)
        self.btnConfirmar.clicked.connect(self.confirmar_adicion_mesas)
        self.btnCancelar.clicked.connect(self.close)
        
        # Mostrar el numero de mesas actual
        self.lblMesasActuales.setText(str(self.evento_obj.get_num_mesas()))
        
    def confirmar_adicion_mesas(self):
        mesas_a_anyadir_str = self.lneNumMesasAñadir.text().strip()
        
        # Validacion del input
        try:
            mesas_a_anyadir = int(mesas_a_anyadir_str)
            if mesas_a_anyadir <= 0:
                QMessageBox.warning(self, "Error de Validacion", "Debes anyadir un numero positivo de mesas.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error de Validacion", "Por favor, introduce un numero valido para las mesas.")
            return

        # Logica de actualizacion
        num_mesas_actual = self.evento_obj.get_num_mesas()
        nuevo_num_mesas = num_mesas_actual + mesas_a_anyadir
        
        self.evento_obj.num_mesas = str(nuevo_num_mesas)
        
        # Preparar los nuevos datos para el EventoManager
        nuevos_datos_evento = [
            self.evento_obj.nombre, 
            self.evento_obj.fecha, 
            self.evento_obj.ubicacion, 
            self.evento_obj.organizador, 
            self.evento_obj.num_mesas
        ]

        if event_manager.actualizar_evento(self.nombre_evento, nuevos_datos_evento):
            QMessageBox.information(self, "Mesas Añadidas", f"Se han añadido {mesas_a_anyadir} mesas. El nuevo total es: {nuevo_num_mesas}")
            self.finished.emit(QDialog.Accepted) 
            self.close()
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el numero de mesas del evento.")


class EliminarMesa(QtWidgets.QDialog):
    """Pop-up para confirmar la eliminacion de una mesa de un evento."""
    
    # MODIFICACION: Ahora recibe el numero de mesa a eliminar
    def __init__(self, gestion_window, mesa_a_eliminar_num): 
        super(EliminarMesa, self).__init__()
        
        self.gestion_evento_window = gestion_window
        self.evento_obj = gestion_window.evento_obj 
        # Variable con el numero de mesa que se va a eliminar
        self.mesa_a_eliminar_num = mesa_a_eliminar_num
        
        # Carga de la UI
        ui_path = os.path.join(UI_DIR, "EliminarMesa.ui")
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        try:
             uic.loadUi(ui_path, self)
        except FileNotFoundError:
             QMessageBox.critical(self, "Error de UI", f"No se encontro el archivo de UI en: {ui_path}")
             self.close()
             return

        self.setWindowTitle(f"Eliminar Mesa {self.mesa_a_eliminar_num} de: {self.evento_obj.nombre}")
        
        # Mapeo de botones
        self.btnBorrarMesa.clicked.connect(self.confirmar_eliminacion_mesa)
        self.btnCancelarEliminar.clicked.connect(self.close)
        
        # Personalizar el mensaje con el numero de la mesa seleccionada
        self.seguroQueQuieresBorrar.setText(
            f"¿Seguro que quieres BORRAR la Mesa {self.mesa_a_eliminar_num}?\n"
            "¡Esto desasignara a sus participantes y renumerara el resto de mesas!"
        )
        
    def confirmar_eliminacion_mesa(self):
        mesa_a_eliminar = self.mesa_a_eliminar_num
        nombre_evento = self.evento_obj.nombre
        
        # 1. Validar que la mesa existe
        num_mesas_actual = self.evento_obj.get_num_mesas()
        if mesa_a_eliminar < 1 or mesa_a_eliminar > num_mesas_actual:
            QMessageBox.critical(self, "Error", f"La mesa {mesa_a_eliminar} no es valida para el evento.")
            self.close()
            return
        
        # 2. Renumerar PARTICIPANTES: Desasignar participantes de la mesa eliminada y decrementar 1 a los de mesas superiores
        # Esta logica se ha delegado en ParticipanteManager.py para mantener la consistencia del CSV
        participante_manager.renumerar_mesas_tras_eliminacion(nombre_evento, mesa_a_eliminar)
        
        # 3. Actualizar el objeto Evento con el nuevo numero de mesas
        nuevo_num_mesas = num_mesas_actual - 1
        self.evento_obj.num_mesas = str(nuevo_num_mesas)
        
        # 4. Preparar los nuevos datos para el EventoManager
        nuevos_datos_evento = [
            self.evento_obj.nombre, 
            self.evento_obj.fecha, 
            self.evento_obj.ubicacion, 
            self.evento_obj.organizador, 
            self.evento_obj.num_mesas
        ]

        # 5. Guardar la actualizacion del evento en el CSV
        if event_manager.actualizar_evento(nombre_evento, nuevos_datos_evento):
            QMessageBox.information(
                self, 
                "Mesa Eliminada", 
                f"Se ha eliminado la Mesa {mesa_a_eliminar} (Nuevo total: {nuevo_num_mesas}).\n"
                f"Los participantes se han desasignado y el resto de mesas se han renumerado."
            )
            
            # Emitir la senal para que la ventana de gestion recargue todos los datos
            self.finished.emit(QDialog.Accepted) 
            self.close()
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el numero de mesas del evento.")