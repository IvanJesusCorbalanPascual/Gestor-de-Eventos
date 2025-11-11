import sys
import os
from PyQt5 import QtWidgets, uic
from EventoManager import event_manager
from PopUp_evento import ActualizarParticipante
from PopUp_participante import CrearParticipante 
from ParticipanteManager import participante_manager
from PyQt5.QtWidgets import QTableWidgetItem 
from Evento import Evento # Importamos Evento para tipado si fuera necesario

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
        # Buscamos el evento usando el manager, devuelve un objeto Evento o None
        evento_obj = event_manager.buscar_evento(self.nombreEvento)
        
        if evento_obj:
            # Asignar los valores a los labels de la UI usando los atributos del objeto
            self.lblTituloEvento.setText(evento_obj.nombre)      # Nombre
            self.lblFecha.setText(evento_obj.fecha)            # Fecha
            self.lblUbicacion.setText(evento_obj.ubicacion)      # Ubicacion
            self.lblOrganizador.setText(evento_obj.organizador)  # Organizador
            self.lblMesas.setText(evento_obj.num_mesas)          # Num_Mesas
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
        # Leemos los participantes del CSV y los muestra en la tablaParticipantes
        participantes_lista = participante_manager.cargar_participantes_por_evento(self.nombreEvento)
        
        tabla = self.tablaParticipantes
        tabla.setRowCount(len(participantes_lista))
        # Ahora hay 5 columnas (Evento, Nombre, Acompañantes, NoSentarCon, Mesa_Asignada)
        tabla.setColumnCount(5) 

        column_headers = ['Nombre', 'Acompañantes', 'No Sentar Con', 'Mesa Asignada', 'Evento (Oculto)']
        
        # Llenar la tabla con los datos
        for row_index, participante_obj in enumerate(participantes_lista):
            
            # Nombre (Columna 0)
            tabla.setItem(row_index, 0, QTableWidgetItem(participante_obj.nombre))
            # Acompañantes (Columna 1)
            tabla.setItem(row_index, 1, QTableWidgetItem(participante_obj.acompanyantes))
            # No Sentar Con (Columna 2)
            tabla.setItem(row_index, 2, QTableWidgetItem(participante_obj.no_sentar_con))
            # Mesa Asignada (Columna 3)
            mesa_str = str(participante_obj.mesa_asignada) if participante_obj.mesa_asignada else "PENDIENTE"
            tabla.setItem(row_index, 3, QTableWidgetItem(mesa_str))
            # Evento (Columna 4)
            tabla.setItem(row_index, 4, QTableWidgetItem(participante_obj.evento)) 
            
        tabla.setHorizontalHeaderLabels(column_headers)
        # Ocultar la columna de Evento si lo deseas
        tabla.setColumnHidden(4, True) 
        
        self.tablaParticipantes.resizeColumnsToContents()
        print("Lista de participantes cargada.")

    def abrir_actualizar_participante(self):
        filaSeleccionada = self.tablaParticipantes.currentRow()

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