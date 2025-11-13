import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PopUp_evento import EliminarEvento, ActualizarEvento, CrearEvento
from EventoManager import event_manager
from Gestion_Evento import GestionEvento 
from Evento import Evento 

# Constantes que almacenan los estilos para utilizarlos mas comodamente en el resto del codigo
TEMA_PANTALLA_PRINCIPAL=("""       
/* Color de Fondo de la Ventana Principal */
QMainWindow, QWidget#centralwidget {
    background-color: #B0E0E6; /* Azul claro suave para el fondo general (como el Aqua Pale) */
}


/* 1. ESTILO DE LA TABLA (QTableWidget) */

QTableWidget {
    background-color: #A5E0FF; /* Azul Cielo mas intenso para el fondo de la tabla */
    border: none;
    color:black;
    gridline-color: #6495ED; /* Color de las lineas de la cuadricula */

}

/* Estilo de la Cabecera Horizontal (NOMBRE DEL EVENTO, ORGANIZADOR, etc.) */
QHeaderView::section {
    background-color: #4AC1FF; /* Azul Cian brillante */
    color: white;
    font-weight: bold;
    padding: 6px;
    border: 1px solid #48D1CC; /* Borde para separar secciones */
}

/* Estilo para las Filas de la Tabla (ItemView) */
QTableWidget::item {
    background-color: #A5E0FF; /* Fondo de las celdas (Azul Cielo) */
    padding: 5px;
}
/* Estilo para las Filas Seleccionadas */
QTableWidget::item:selected {
    background-color: #83D4FF; /* Azul Acero para la seleccion */
    color: white;
}


/* 2. ESTILO DEL BUSCADOR (QLineEdit) */

QLineEdit#lneBuscador { /* Usa tu objectName real */
    background-color: #E0FFFF; /* Azul Celeste muy claro */
    border: 2px solid #87CEFA; /* Borde sutil */
    border-radius: 10px; /* Bordes redondeados */
    padding: 5px;
    margin-right: 10px; /* Margen para separarlo de los botones */
}


/* 3. ESTILO DE LOS BOTONES DE ACCION */

QPushButton {
    /* Estilos base comunes */
    border: none;
    border-radius: 12px; /* Bordes Redondeados para todos los botones */
    padding: 8px 15px;
    font-weight: bold;
    color: black;
}
""")

TEMA_OSCURO=("""
                QMainWindow{background-color:#2d2d2d;}
                QWidget{background-color:#2d2d2d;color:#ffffff;}
                QTableWidget{background-color:#3c3c3c;color:#ffffff;}
                QHeaderView::section{background-color:#404040;color:#ffffff;}
                QPushButton{background-color:#e0e0e0;color:#000000;}
                QComboBox{background-color:#404040;color:#ffffff;}
                QLineEdit{background-color:#404040;color:#aaaaaa;}
                QMenuBar{background-color:#404040;color:#ffffff;}
            """)

TEMA_GREENTONIC=("""
/* Color de Fondo de la Ventana Principal */
QMainWindow, QWidget#centralwidget {
    background-color: #E0FFE0; /* Verde muy palido/Menta para el fondo general */
    color: #1E1E1E; /* Texto oscuro */
}


/* 1. ESTILO DE LA TABLA (QTableWidget) */

QTableWidget {
     background-color: #F0FFF0; /* Blanco mas puro para el fondo de la tabla */
    border: 1px solid #90EE90; /* Borde verde claro */
    color: black;
    gridline-color: #ADFF2F; /* Verde Lima (Acento refrescante para las lineas) */
}

/* Estilo de la Cabecera Horizontal (Headers) */
QHeaderView::section {
    background-color: #3CB371; /* Verde Medio Mar (Un verde mas profundo para el contraste) */
    color: white;
    font-weight: bold;
    padding: 6px;
    border: 1px solid #2E8B57; /* Borde verde oscuro */
}

/* Estilo para las Filas de la Tabla (ItemView) */
QTableWidget::item {
    background-color: #F0FFF0; /* Fondo de las celdas (Blanco) */
    padding: 5px;
}
/* Estilo para las Filas Seleccionadas */
QTableWidget::item:selected {
    background-color: #98FB98; /* Verde Menta Claro para la seleccion */
    color: black; /* Texto oscuro sobre seleccion clara */
}


/* 2. ESTILO DEL BUSCADOR (QLineEdit) */

QLineEdit#lneBuscador { /* Usa tu objectName real */
    background-color: #FFFFFF; /* Blanco limpio */
    border: 2px solid #66CDAA; /* Borde suave de color Aguamarina */
    border-radius: 10px; /* Bordes redondeados */
    padding: 5px;
    margin-right: 10px;
    color: #1E1E1E;
}


/* 3. ESTILO DE LOS BOTONES DE ACCION */

QPushButton {
    /* Estilos base comunes */
    background-color: #6B8E23; /* Verde Oliva Oscuro como color primario */
    color: black; /* Texto blanco para alto contraste */
    border: none;
    border-radius: 12px;
    padding: 8px 15px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #8FBC8F; /* Verde Claro al pasar el raton */
    color: #1E1E1E; /* Texto oscuro en hover */
    border: 1px solid #3CB371;
}
""")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        icon_path = os.path.join(parent_dir,"Imagenes", "logoGT.png") # guardando la ruta del icono en la variable icon_path
        self.setWindowIcon(QIcon(icon_path)) # Icono de ventana
        ui_path = os.path.join(parent_dir, "ui", "PantallaPrincipal.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Gestor de Eventos")
        # Asignando el tema al iniciar la pantalla
        self.setStyleSheet(TEMA_PANTALLA_PRINCIPAL) 
       
        
        # Mapeo de botones
        self.lneBuscador.textChanged.connect(self.buscar_evento)
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
        # Se asume que el resto de botones de accion deben estar tambien deshabilitados si no hay seleccion
        self.btnActualizarEvento.setEnabled(esta_seleccionado)
        self.btnEliminarEvento.setEnabled(esta_seleccionado)


    def cambiar_tema(self, tema):
        if tema == "Oscuro":
            self.setStyleSheet(TEMA_OSCURO)
        elif tema == ('GreenTonic'):
            self.setStyleSheet(TEMA_GREENTONIC)
        else:
            self.setStyleSheet(TEMA_PANTALLA_PRINCIPAL)

    def obtener_evento_seleccionado(self):
        # Comprueba y obtiene la fila seleccionada en tablaEventos
        filaSeleccionada = self.tablaEventos.currentRow()

        # Verifica si ha seleccionado un evento
        if filaSeleccionada == -1:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "Seleccione un evento de la tabla")
            return None
        
        # Obtiene el nombre del evento (columna 0)
        try:
            nombreEvento = self.tablaEventos.item(filaSeleccionada, 0).text()
            return nombreEvento
        except AttributeError:
            QtWidgets.QMessageBox.critical(self, "Error", "No se ha podido encontrar el nombre del evento seleccionado")
            return None

    # Metodo para buscar eventos con el buscador
    def buscar_evento(self,consulta):
        tabla = self.tablaEventos
        consultaToLow = consulta.lower().strip()

        # Bucle que recorre todos los Eventos (Filas) buscando un texto que coincida
        # con el de la consulta realizada por el usuario, si coincide lo deja visible, sino
        # lo esconde 
        for fila in range(tabla.rowCount()):
            itemTarea = tabla.item(fila,0)

            if itemTarea:
                texto_item = itemTarea.text().lower()
                esVisible = consultaToLow in texto_item
                tabla.setRowHidden(fila, not esVisible)
            else:
                tabla.setRowHidden(fila, True)
        
    def abrir_gestion_eventos(self):
        # Obtenemos el nombre del evento
        nombreEvento = self.obtener_evento_seleccionado()

        if nombreEvento:
            # Abrimos la ventana de gestion y le pasamos el nombre del evento
            self.gestion_window = GestionEvento(nombreEvento=nombreEvento)
            self.gestion_window.show()
            self.gestion_window.setStyleSheet(TEMA_PANTALLA_PRINCIPAL)
            self.close()

    def abrir_Actualizar_Evento(self):
        nombreEvento = self.obtener_evento_seleccionado()

        if nombreEvento is None:
            return
        
        self.gestion_window = ActualizarEvento(main_window=self, nombreEvento=nombreEvento) 
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
        # Lee los eventos del CSV y los muestra en la tablaEventos. Devuelve lista de objetos Evento
        eventos_lista = event_manager.cargar_eventos()
        
        # Configurar la tabla
        self.tablaEventos.setRowCount(len(eventos_lista))
        self.tablaEventos.setColumnCount(5) 
        
        # Llenar la tabla con los datos
        for row_index, evento_obj in enumerate(eventos_lista):
            # Usamos los atributos del objeto Evento 
            self.tablaEventos.setItem(row_index, 0, QtWidgets.QTableWidgetItem(evento_obj.nombre))
            # Fecha
            self.tablaEventos.setItem(row_index, 1, QtWidgets.QTableWidgetItem(evento_obj.fecha))
            # Organizador
            self.tablaEventos.setItem(row_index, 2, QtWidgets.QTableWidgetItem(evento_obj.organizador))
            # Ubicacion
            self.tablaEventos.setItem(row_index, 3, QtWidgets.QTableWidgetItem(evento_obj.ubicacion))
            # Mesas
            self.tablaEventos.setItem(row_index, 4, QtWidgets.QTableWidgetItem(evento_obj.num_mesas))
              
        self.tablaEventos.setHorizontalHeaderLabels(['Nombre', 'Fecha', 'Organizador', 'Ubicacion', 'Mesas'])
        # Ocultando el indice vertical (los numeros de fila)
        self.tablaEventos.verticalHeader().setVisible(False)
        self.tablaEventos.resizeColumnsToContents()