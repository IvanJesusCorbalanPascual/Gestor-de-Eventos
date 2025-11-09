import sys
import os
from PyQt5 import QtWidgets, uic
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
        self.lneBuscador.textChanged.connect(self.buscar_evento)
        self.boxTema.currentTextChanged.connect(self.cambiar_tema)
        self.btnConsultarEvento.clicked.connect(self.abrir_gestion_eventos)
        self.btnActualizarEvento.clicked.connect(self.abrir_Actualizar_Evento)
        self.btnCrearEvento.clicked.connect(self.abrir_Crear_Evento)
        self.btnEliminarEvento.clicked.connect(self.abrir_Eliminar_Evento)
        
        # Cargar eventos al iniciar la aplicacion
        self.cargar_eventos_en_tabla() 

    def cambiar_tema(self, tema):
        if tema == "Oscuro":
            self.setStyleSheet(TEMA_OSCURO)
        else:
            self.setStyleSheet(TEMA_CLARO)

    # Metodo para buscar eventos con el buscador
    def buscar_evento(self,consulta):
        tabla = self.tablaEventos
        consultaToLow = consulta.lower().strip()

        """
         Bucle for que recorre todos los Eventos (Filas) buscando un texto que coincida
         con el de la consulta realizada por el usuario, si coincide lo deja visible, sino
         lo esconde 
        """

        for fila in range(tabla.rowCount()):
            itemTarea = tabla.item(fila,0)

            if itemTarea:
                consulta = itemTarea.text().lower()
                esVisible = consultaToLow in consulta
                tabla.setRowHidden(fila, not esVisible)
            else:
                tabla.setRowHidden(fila, True)
        
    def abrir_gestion_eventos(self):
        self.gestion_window = GestionEvento()
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
        self.gestion_window = EliminarEvento()
        self.gestion_window.show()

    def cargar_eventos_en_tabla(self):
        # Lee los eventos del CSV y los muestra en la tablaEventos
        datos = event_manager.cargar_eventos()
        
        # Configurar la tabla
        self.tablaEventos.setRowCount(len(datos))
        self.tablaEventos.setColumnCount(5) 
        
        # Llenar la tabla con los datos
        for row_index, row_data in enumerate(datos):
            # Nombre
            self.tablaEventos.setItem(row_index, 0, QtWidgets.QTableWidgetItem(row_data[0]))
            # Fecha
            self.tablaEventos.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row_data[1]))
            # Organizador
            self.tablaEventos.setItem(row_index, 2, QtWidgets.QTableWidgetItem(row_data[2]))
            # Ubicacion
            self.tablaEventos.setItem(row_index, 3, QtWidgets.QTableWidgetItem(row_data[3]))
            # Mesas
            self.tablaEventos.setItem(row_index, 4, QtWidgets.QTableWidgetItem(row_data[4]))
            
        self.tablaEventos.setHorizontalHeaderLabels(['Nombre', 'Fecha', 'Organizador', 'Ubicacion', 'Mesas'])
        self.tablaEventos.resizeColumnsToContents()