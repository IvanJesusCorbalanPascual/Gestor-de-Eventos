import sys
import os
import csv
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QFileDialog
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
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        ui_path = os.path.join(parent_dir, "ui", "ActualizarEvento.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Actualizar Evento")

        # Conecta el boton 'Actualizar' a la funcion 'confirmar_actualizacion'
        self.btnPopupActualizarEvento.clicked.connect(self.confirmar_actualizacion)

        # Se usa try-except para manejar nombres de botones ligeramente diferentes si el UI se renombra
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
            self.lblNombreEvento.setText(self.nombre_evento_original)
            # Usamos los atributos del objeto Evento
            self.lneNuevoNombreEvento.setText(evento_obj.nombre)
            self.lneActualizarUbicacionEvento.setText(evento_obj.ubicacion)
            self.lneActualizarOrganizador.setText(evento_obj.organizador)
            self.lneActualizarMesas.setText(evento_obj.num_mesas) 

            # Convierte la fecha de un String a formato QDateTime
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
        nuevoNumMesas_str = self.lneActualizarMesas.text().strip()

        # Validacion de numero de mesas
        try:
            nuevoNumMesas = int(nuevoNumMesas_str)
            if nuevoNumMesas <= 0:
                 QtWidgets.QMessageBox.warning(self, "Error de validacion", "El numero de mesas debe ser positivo")
                 return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error de validacion", "Por favor, introduce un numero de mesas valido")
            return

        # Comprueba que los campos no estan vacios
        if not all([nuevoNombre, nuevaUbicacion, nuevoOrganizador]):
            QtWidgets.QMessageBox.warning(self, "Error", "Debes completar todos los campos, intentalo de nuevo")
            return
        
        # Almacena los nuevos datos en una lista para el manager
        nuevos_datos_evento = [nuevoNombre, nuevaFecha, nuevaUbicacion, nuevoOrganizador, str(nuevoNumMesas)]

        # Llama al manager para intentar actualizar el CSV
        if event_manager.actualizar_evento(self.nombre_evento_original, nuevos_datos_evento):

            # Si main_window existe, actualiza su tabla (esto es solo para la Pantalla Principal)
            if self.main_window:
                self.main_window.cargar_eventos_en_tabla()

            QtWidgets.QMessageBox.information(self, "Evento Actualizado", f"El evento '{nuevoNombre}' ha sido actualizado")
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No ha sido posible actualizar el evento")


class CrearEvento(QtWidgets.QMainWindow):
    def __init__(self, main_window):
        super(CrearEvento, self).__init__()

        # Guarda main_window para usarlo en otras funciones
        self.main_window = main_window

        # Guarda la ruta del CSV en una variable
        self.csv_path_adjuntado = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "CrearEvento.ui")
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Creacion Evento")

        self.btnCrearEvento.clicked.connect(self.crear_nuevo_evento)
        self.btnCancelar.clicked.connect(self.volver_principal)
        self.btnAdjuntarCSV.clicked.connect(self.abrir_dialogo_csv)

    def volver_principal(self):
        self.close()

    def abrir_dialogo_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV de Participantes", "", "Archivos CSV (*.csv);;Todos los archivos (*)")

        if file_path:
            self.csv_path_adjuntado = file_path
            file_name = os.path.basename(file_path)
            self.btnAdjuntarCSV.setText(f"Adjuntado: {file_name}")

    def importar_participantes_csv(self, file_path, nombre_evento):
        contador = 0
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)

                next(reader, None)

                for row in reader:
                    if not row: 
                        continue

                    nombre = row[0].strip()
                    if not nombre:
                        continue

                    acompanyantes = row[1].strip() if len(row) > 1 else ""
                    no_sentar_con = row[2].strip() if len(row) > 2 else ""

                    # Creación del objeto participante
                    nuevo_participante = Participante(evento=nombre_evento, nombre=nombre, acompanyantes=acompanyantes, no_sentar_con=no_sentar_con)

                    if participante_manager.guardar_participante(nuevo_participante):
                        contador += 1
                    else:
                        print(f"Error al intentar guardar el participante: {nombre}")

        except FileNotFoundError:
            print(f"Error, no se ha podido encontrar el archivo CSV en {file_path}")
            return f"Error, no se ha podido encontrar el archivo {os.path.basename(file_path)}]"
        except Exception as e:
            print(f"Error de procesamiento en el CSV: {e}")
            return f"Error de procesamiento en el CSV: {e}"
        return contador

    def crear_nuevo_evento(self):
        # Obtener los datos del UI
        nombre = self.lneNombreEvento.text()
        # Usamos la constante de la clase Evento
        fecha_obj = self.dateFechaEvento.dateTime().toString(Evento.DATE_FORMAT) 
        ubicacion = self.lneUbicacion.text()
        organizador = self.lneOrganizador.text()
        num_mesas_str = self.lneNumMesas.text().strip()
        
        # Validacion de mesas
        try:
            # Intentamos convertir el texto a un numero entero
            num_mesas = int(num_mesas_str)
 
            if num_mesas <= 0:
                raise ValueError("El numero debe ser positivo")

        except ValueError:

            QtWidgets.QMessageBox.warning(self, "Error de validacion", 
                                          "Por favor, introduce un numero de mesas valido")
            return

        # Error si no estan los datos
        if not all([nombre, ubicacion, organizador]):
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, complete todos los campos")
            return

        # Creamos el objeto Evento
        nuevo_evento = Evento(nombre, fecha_obj, ubicacion, organizador, str(num_mesas))
        
        # Guardar el objeto en el CSV a traves del manager
        if event_manager.guardar_evento(nuevo_evento):

            mensaje_csv = ""
            if self.csv_path_adjuntado:
                num_importados = self.importar_participantes_csv(self.csv_path_adjuntado, nombre)
                mensaje_csv = f"\n{num_importados} participantes han sido importados del CSV."

            # Actualizar la tabla de la ventana principal
            self.main_window.cargar_eventos_en_tabla()

            # Cerrar la ventana despues de crear el evento
            QtWidgets.QMessageBox.information(self, "Evento Creado", f"Evento '{nombre}' creado y guardado." + mensaje_csv)
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Guardado", "No se pudo guardar el evento en la base de datos")

class EliminarEvento(QtWidgets.QMainWindow):
    def __init__(self, nombreEvento, mainWindow):
        super(EliminarEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "EliminarEvento.ui")
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # Guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path))  # Estableciendo el icono de la ventana
        uic.loadUi(ui_path, self)
        self.setWindowTitle(f"Eliminar Evento {nombreEvento}")

        self.nombreEvento = nombreEvento
        self.mainWindow = mainWindow

        # Personalizamos el QLabel con el mensaje de confirmacion
        self.seguroQueQuieresBorrar.setText(f"¿Seguro que quieres BORRAR '{self.nombreEvento}' ?")

        self.btnCancelarEliminar.clicked.connect(self.volver_principal)
        self.btnBorrar.clicked.connect(self.confirmar_eliminacion)

    def volver_principal(self):
        self.close()

    def confirmar_eliminacion(self):
        # Eliminados el evento del CSV llamando al manager
        if event_manager.eliminar_evento(self.nombreEvento):

            QtWidgets.QMessageBox.information(self, "Evento Eliminado", f"Se ha eliminado el evento '{self.nombreEvento}' exitosamente")

            # Actualiza la tabla en la ventana principal
            self.mainWindow.cargar_eventos_en_tabla()

            self.close()

        else:
            QtWidgets.QMessageBox.critical(self, "Error al eliminar", f"No se ha podido borrar el evento")