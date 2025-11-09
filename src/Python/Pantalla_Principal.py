import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PopUp_evento import EliminarEvento, ActualizarEvento, CrearEvento
from EventoManager import event_manager
from Gestion_Evento import GestionEvento 

# Constantes que almacenan los estilos para utilizarlos mas comodamente en el resto del codigo
TEMA_OSCURO=("""
                QMainWindow{background-color:#2d2d2d;}
                QWidget{background-color:#2d2d2d;color:#ffffff;}
                QTableWidget{background-color:#3c3c3c;color:#ffffff;}
                QHeaderView::section{background-color:#404040;color:#ffffff;}
                QPushButton{background-color:#e0e0e0;color:#000000;}
                QComboBox{background-color:#404040;color:#ffffff;}
                QLineEdit{background-color:#404040;color:#ffffff;}
                QMenuBar{background-color:#404040;color:#ffffff;}
            """)

TEMA_CLARO=("""
                QMainWindow{background-color:#ffffff;}
                QWidget{background-color:#ffffff;color:#000000;}
                QTableWidget{background-color:#ffffff;color:#000000;}
                QHeaderView::section{background-color:#e0e0e0;color:#000000;}
                QPushButton{background-color:#e0e0e0;color:#000000;}
                QComboBox{background-color:#ffffff;color:#000000;}
                QLineEdit{background-color:#ffffff;color:#000000;}
                QMenuBar{background-color:#f0f0f0;color:#000000;}
            """)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "PantallaPrincipal.ui")
        uic.loadUi(ui_path, self)
        
        # Asignando el tema claro al iniciar la pantalla
        self.setStyleSheet(TEMA_CLARO)
        
        # Mapeo de botones
        self.boxTema.currentTextChanged.connect(self.cambiar_tema)
        
        # Conectamos la tabla para que verifique la seleccion y active o desactive el boton
        self.tablaEventos.itemSelectionChanged.connect(self.actualizar_estado_botones)
        
        self.btnConsultarEvento.clicked.connect(self.abrir_gestion_eventos)
        self.btnActualizarEvento.clicked.connect(self.abrir_Actualizar_Evento)
        self.btnCrearEvento.clicked.connect(self.abrir_Crear_Evento)
        self.btnEliminarEvento.clicked.connect(self.abrir_Eliminar_Evento)
        
        # Inicialmente el boton consultar estara deshabilitado
        self.btnConsultarEvento.setEnabled(False)
        
        # Cargar eventos al iniciar la aplicacion
        self.cargar_eventos_en_tabla() 
        
    # Metodo para actualizar el estado de los botones
    def actualizar_estado_botones(self):
        # Habilita el boton si hay al menos una celda seleccionada en la tabla
        esta_seleccionado = len(self.tablaEventos.selectedIndexes()) > 0
        self.btnConsultarEvento.setEnabled(esta_seleccionado)


    def cambiar_tema(self, tema):
        if tema == "Oscuro":
            self.setStyleSheet(TEMA_OSCURO)
        else:
            self.setStyleSheet(TEMA_CLARO)

    def obtener_evento_seleccionado(self):
        # Comprueba y obtiene la fila seleccionada en tablaEventos
        filaSeleccionada = self.tablaEventos.currentRow()

        # Verifica si ha seleccionado un evento
        if filaSeleccionada == -1:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "Seleccione un evento de la tabla")
            return None
        
        # Obtiene el nombre del evento
        try:
            nombreEvento = self.tablaEventos.item(filaSeleccionada, 0).text()
            return nombreEvento
        except AttributeError:
            QtWidgets.QMessageBox.critical(self, "Error", "No se ha podido encontrar el nombre del evento seleccionado")
            return None

    def abrir_gestion_eventos(self):
        # Obtenemos el nombre del evento
        nombreEvento = self.obtener_evento_seleccionado()

        if nombreEvento:
            # Abrimos la ventana de gestion y le pasamos el nombre del evento
            self.gestion_window = GestionEvento(nombreEvento=nombreEvento)
            self.gestion_window.show()
            self.close()

    def abrir_Actualizar_Evento(self):
        self.gestion_window = ActualizarEvento(main_window=self) 
        self.gestion_window.show()

    def abrir_Crear_Evento(self):
        # Pasa la referencia de la ventana principal para que el pop-up pueda actualizar la tabla
        self.gestion_window = CrearEvento(main_window=self) 
        self.gestion_window.show()

    def abrir_Eliminar_Evento(self):
        # Obtenemos el nombre del evento
        nombreEvento = self.obtener_evento_seleccionado()

        if nombreEvento:
            self.gestion_window = EliminarEvento(nombreEvento=nombreEvento, mainWindow=self)
            self.gestion_window.show()

    def cargar_eventos_en_tabla(self):
        # Lee los eventos del CSV y los muestra en la tablaEventos
        datos = event_manager.cargar_eventos()
        
        # Configurar la tabla
        self.tablaEventos.setRowCount(len(datos))
        self.tablaEventos.setColumnCount(4) 
        
        # Llenar la tabla con los datos
        for row_index, row_data in enumerate(datos):
            # Nombre
            self.tablaEventos.setItem(row_index, 0, QtWidgets.QTableWidgetItem(row_data[0]))
            # Fecha
            self.tablaEventos.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row_data[1]))
            # Organizador
            self.tablaEventos.setItem(row_index, 2, QtWidgets.QTableWidgetItem(row_data[3]))
            # Ubicacion
            self.tablaEventos.setItem(row_index, 3, QtWidgets.QTableWidgetItem(row_data[2]))
            # Mesas
            self.tablaEventos.setItem(row_index, 3, QtWidgets.QTableWidgetItem("Sin Asignar"))
            
        self.tablaEventos.setHorizontalHeaderLabels(['Nombre', 'Fecha', 'Organizador', 'Ubicacion'])
        self.tablaEventos.resizeColumnsToContents()