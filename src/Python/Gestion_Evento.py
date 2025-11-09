import sys
import os
from PyQt5 import QtWidgets, uic
from EventoManager import event_manager
from PopUp_evento import ActualizarParticipante
from PopUp_participante import CrearParticipante 

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

        self.btnActualizarParticipante.clicked.connect(self.abrir_actualizar_participante)

        
        # Conexiones para gestion de participantes (boton Añadir)
        self.btnAnyadirParticipante.clicked.connect(self.abrir_crear_participante)
        
        # Cargar la informacion del evento al iniciar
        self.cargar_info_evento()
        self.cargar_participantes_en_tabla()
        print("Consultando evento...")
        
    # Metodo para cargar la informacion del evento
    def cargar_info_evento(self):
        # Buscamos el evento usando el manager
        evento = event_manager.buscar_evento(self.nombreEvento)
        
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
            
    # Metodo para abrir la ventana de creacion de participantes
    def abrir_crear_participante(self):
        # Abre la ventana emergente para crear un participante
        self.crear_participante_window = CrearParticipante(gestion_evento_window=self, nombreEvento=self.nombreEvento)
        self.crear_participante_window.show()
        
    # Metodo para volver a la pantalla principal    
    def volver_principal(self):
        from Pantalla_Principal import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
        print("Volviendo a la pantalla principal...")


    def cargar_participantes_en_tabla(self):
        # Falta añadir la logica para leer el CSV con los participantes
        print("Cargando la lista de los participantes..")
        self.tablaParticipantes.resizeColumnsToContents()

    def abrir_actualizar_participante(self):
        filaSeleccionada = self.tablaParticipantes.currentRow()

        # Comprueba si se ha seleccionado una fila, si no, manda una advertencia al usuario
        if filaSeleccionada == -1:
            QtWidgets.QMessageBox.warning(self, "Selección de fila requerida", "Debes seleccionar un participante de la tabla que desee actualizar.")
            return
        
        try:
            nombreParticipante = self.tablaParticipantes.item(filaSeleccionada, 0).text()
        except AttributeError:
            QtWidgets.QMessageBox.critical(self, "Error", "No ha sido posible obtener el nombre del participante.")
            return
        
        self.popup_actualizar = ActualizarParticipante(gestion_window=self, nombre_participante=nombreParticipante)
        self.popup_actualizar.show()

    