import sys
import os
from PyQt5 import QtWidgets, uic
from EventoManager import event_manager

class GestionEvento(QtWidgets.QMainWindow):
    
    # Metodo para inciar la pantalla
    def __init__(self, nombreEvento):
        super(GestionEvento, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "GestionDeEventos.ui")
        uic.loadUi(ui_path, self)
        
        # Guarda el nombre del evento para usarlo despues
        self.nombreEvento = nombreEvento
        
        self.btnVolver.clicked.connect(self.volver_principal)
        
        # Cargar la informacion del evento al iniciar
        self.cargar_info_evento()
        print("Consultando evento...")
        
    # Metodo para cargar la informacion del evento
    def cargar_info_evento(self):
        # Buscamos el evento usando el manager
        evento = event_manager.buscar_evento_por_nombre(self.nombreEvento)
        
        if evento:
            # Asignar los valores a los labels de la UI
            self.lblTituloEvento.setText(evento[0])  # Nombre
            self.lblFecha.setText(evento[1])        # Fecha
            self.lblUbicacion.setText(evento[2])    # Ubicacion
            self.lblOrganizador.setText(evento[3])  # Organizador
            self.lblMesas.setText(evento[4])        # Num_Mesas
            print(f"Informacion del evento '{self.nombreEvento}' cargada correctamente")
        else:
            QtWidgets.QMessageBox.critical(self, "Error de Carga", "No se ha podido encontrar la informacion del evento")
            self.volver_principal()
        
    # Metodo para volver a la pantalla principal    
    def volver_principal(self):
        from Pantalla_Principal import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
        print("Volviendo a la pantalla principal...")