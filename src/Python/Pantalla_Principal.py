import sys
import os
from PyQt5 import QtWidgets, uic
from PopUp_evento import EliminarEvento, ActualizarEvento, CrearEvento

TEMA_OSCURO=("""
                QMainWindow{background-color:#2d2d2d;}
                QWidget{background-color:#2d2d2d;color:#ffffff;}
                QTableWidget{background-color:#3c3c3c;color:#ffffff;}
                QHeaderView::section{background-color:#404040;color:#ffffff;}
                QPushButton{background-color:#555555;color:#ffffff;}
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
        self.btnConsultarEvento.clicked.connect(self.abrir_gestion_eventos)
        self.btnActualizarEvento.clicked.connect(self.abrir_Actualizar_Evento)
        self.btnCrearEvento.clicked.connect(self.abrir_Crear_Evento)
        self.btnEliminarEvento.clicked.connect(self.abrir_Eliminar_Evento)

    def cambiar_tema(self, tema):
        if tema == "Oscuro":
            self.setStyleSheet(TEMA_OSCURO)
        else:
            self.setStyleSheet(TEMA_CLARO)

    def abrir_gestion_eventos(self):
        from Gestion_Evento import GestionEvento
        self.gestion_window = GestionEvento()
        self.gestion_window.show()
        self.close()

    def abrir_Actualizar_Evento(self):
        self.gestion_window = ActualizarEvento()
        self.gestion_window.show()

    def abrir_Crear_Evento(self):
        self.gestion_window = CrearEvento()
        self.gestion_window.show()

    def abrir_Eliminar_Evento(self):
        self.gestion_window = EliminarEvento()
        self.gestion_window.show()