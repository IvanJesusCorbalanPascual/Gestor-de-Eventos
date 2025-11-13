# Gestion_Evento.py

import sys
import os
import csv
from PyQt5 import QtWidgets, uic, QtCore
from EventoManager import event_manager
from PopUp_participante import CrearParticipante, ActualizarParticipante, EliminarParticipante
from ParticipanteManager import participante_manager
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtCore import QDataStream, QIODevice
from Evento import Evento
from Mesas import Mesa
from PopUp_evento import ActualizarEvento
from PopUp_Mesa import AnyadirMesa, EliminarMesa


class GestionEvento(QtWidgets.QMainWindow):

    def __init__(self, nombreEvento):
        super(GestionEvento, self).__init__()

        # Cargando la interfaz
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ui_path = os.path.join(parent_dir, "ui", "GestionDeEventos.ui")
        uic.loadUi(ui_path, self)

        # Creando la Variables principales
        self.nombreEvento = nombreEvento
        self.evento_obj = event_manager.buscar_evento(self.nombreEvento)
        # Nota: self.nombreParticipante no esta definido en el constructor
        self.participante_obj = participante_manager.buscar_participante(self.nombreEvento, self.nombreParticipante) if hasattr(self, 'nombreParticipante') else None
        self.mesas_del_evento = []

        # Mapeo de botones
        self.btnVolver.clicked.connect(self.volver_principal)
        self.btnActualizarParticipante.clicked.connect(self.abrir_actualizar_participante)
        self.btnAnyadirParticipante.clicked.connect(self.abrir_crear_participante)
        self.btnEliminarParticipante.clicked.connect(self.abrir_eliminar_participante)
        
        # para la funcionalidad de Actualizar Mesas.
        self.btnAnyadirMesa.clicked.connect(self.abrir_anyadir_mesas)
        self.btnEliminarMesa.clicked.connect(self.abrir_eliminar_mesa)

        # Conexion boton generar informe
        self.btnGenerarInforme.clicked.connect(self.generar_informe_csv)
        
        # Conexión para el LineEdit del buscador
        # CORRECCIÓN: Usar el objectName correcto 'lneBuscadorParticipante' del .ui
        self.lneBuscadorParticipante.textChanged.connect(self.filtrar_participantes) 
            
        # Conexiones de las listas
        self.listWidgetMesas.currentItemChanged.connect(self._manejar_cambio_mesa_seleccionada)
        
        # Conecta la senal de cambio de seleccion de mesas para actualizar la UI
        self.listWidgetMesas.currentItemChanged.connect(self.actualizar_estado_boton_eliminar_mesa)

        # CONFIGURACION DE DRAG & DROP
        # Lista derecha: Participantes sin mesa
        self.listWidgetParticipantesSinMesas.setDragEnabled(True) 
        self.listWidgetParticipantesSinMesas.setAcceptDrops(True)
        self.listWidgetParticipantesSinMesas.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listWidgetParticipantesSinMesas.viewport().installEventFilter(self)

        # Lista medio: Participantes en mesa
        self.listWidgetParticipantes.setDragEnabled(True)
        self.listWidgetParticipantes.setAcceptDrops(True)
        self.listWidgetParticipantes.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listWidgetParticipantes.viewport().installEventFilter(self)

        # La lista de mesas no acepta drops
        self.listWidgetMesas.setAcceptDrops(False)
        
        # Deshabilitar el boton de eliminar mesa al inicio
        self.btnEliminarMesa.setEnabled(False)

        # CARGA INICIAL DE DATOS
        self.cargar_info_evento()
        self.cargar_mesas_en_listwidget()
        self.cargar_participantes_en_tabla()
        self.refrescar_listas_mesas_tab()

        print("Consultando evento")

    # --- Metodo para la gestion de UI de Mesas ---
    
    def actualizar_estado_boton_eliminar_mesa(self):
        #Habilita/Deshabilita el boton Eliminar Mesa si una mesa especifica esta seleccionada
        current_item = self.listWidgetMesas.currentItem()
        
        # Comprobar si hay un item seleccionado
        if current_item is None:
            self.btnEliminarMesa.setEnabled(False)
            self.btnEliminarMesa.setText("Eliminar Mesa")
            return
            
        nombre_mesa_seleccionada = current_item.text().strip().upper()
        
        # Comprobar si es una mesa valida
        if nombre_mesa_seleccionada.startswith("MESA ") and nombre_mesa_seleccionada != "TODOS LOS PARTICIPANTES":
            try:
                # Extraer el numero de mesa
                numero_mesa_sel = int(nombre_mesa_seleccionada.split(' ')[1])
                # La mesa seleccionada debe existir
                if numero_mesa_sel <= self.evento_obj.get_num_mesas():
                    self.btnEliminarMesa.setEnabled(True)
                    self.btnEliminarMesa.setText(f"Eliminar Mesa {numero_mesa_sel}")
                else:
                    self.btnEliminarMesa.setEnabled(False)
                    self.btnEliminarMesa.setText("Eliminar Mesa")
            except (ValueError, IndexError):
                self.btnEliminarMesa.setEnabled(False)
                self.btnEliminarMesa.setText("Eliminar Mesa")
        else:
            self.btnEliminarMesa.setEnabled(False)
            self.btnEliminarMesa.setText("Eliminar Mesa")
            
    # --- Funcionalidad de Mesas ---
    
    def abrir_anyadir_mesas(self):
        # Usamos el nuevo pop-up AnyadirMesa
        self.popup_anyadir_mesa = AnyadirMesa(gestion_window=self)
        
        # Conecta la senal finished para recargar las mesas y participantes
        self.popup_anyadir_mesa.finished.connect(self.recargar_datos_tras_actualizacion)
        self.popup_anyadir_mesa.show()

    # abrir el pop-up de Eliminar Mesa
    def abrir_eliminar_mesa(self):
        # Obtener la mesa seleccionada, como se hace para actualizar participante
        item_seleccionado = self.listWidgetMesas.currentItem()
        
        if not item_seleccionado or item_seleccionado.text().strip().upper() == "TODOS LOS PARTICIPANTES":
            QMessageBox.warning(self, "Seleccion Requerida", "Por favor, selecciona una mesa especifica para eliminar.")
            return

        nombre_mesa_seleccionada = item_seleccionado.text().strip()
        
        try:
            mesa_a_eliminar_num = int(nombre_mesa_seleccionada.split(' ')[1])
            
            # 1. Comprobar que el numero de mesa es valido
            if mesa_a_eliminar_num <= 0 or mesa_a_eliminar_num > self.evento_obj.get_num_mesas():
                QMessageBox.critical(self, "Error", f"Mesa {mesa_a_eliminar_num} no valida o no existente.")
                return
            
        except (ValueError, IndexError):
            QMessageBox.critical(self, "Error", "Error al obtener el numero de mesa seleccionado.")
            return
            
        # Pasar el numero de mesa seleccionado al pop-up
        # MODIFICACION: Se pasa el numero de mesa seleccionado al pop-up
        self.popup_eliminar_mesa = EliminarMesa(gestion_window=self, mesa_a_eliminar_num=mesa_a_eliminar_num)
        
        # Conecta la senal finished para recargar las mesas y participantes
        self.popup_eliminar_mesa.finished.connect(self.recargar_datos_tras_actualizacion)
        self.popup_eliminar_mesa.show()
        
    
    def recargar_datos_tras_actualizacion(self):
        # Vuelve a buscar el evento actualizado y recarga las vistas
        self.evento_obj = event_manager.buscar_evento(self.nombreEvento)
        self.cargar_info_evento()
        self.cargar_mesas_en_listwidget()
        self.refrescar_listas_mesas_tab()
        self.cargar_participantes_en_tabla()
        self.actualizar_estado_boton_eliminar_mesa() # Actualizar estado del boton
        


    # EVENT FILTER - Metodo que gestiona tanto la funcion de arrastrar como la de soltar
    def eventFilter(self, source, event):
        # Drop sobre la lista de participantes EN MESA (medio)
        if source == self.listWidgetParticipantes.viewport(): #viewport es el area real donde se dibujan los items de la lista
            if event.type() == QtCore.QEvent.DragEnter:
                event.acceptProposedAction()
                
            elif event.type() == QtCore.QEvent.Drop:
                event.acceptProposedAction()
                self.handle_drop_on_participantes_list(event)
                return True

        # Drop sobre la lista de participantes SIN MESA (derecha)
        if source == self.listWidgetParticipantesSinMesas.viewport():
            if event.type() == QtCore.QEvent.DragEnter:
                event.acceptProposedAction()
                
            elif event.type() == QtCore.QEvent.Drop:
                event.acceptProposedAction()
                self.handle_drop_on_sin_mesa_list(event)
                return True

        return super(GestionEvento, self).eventFilter(source, event)

    # Logica de drop: ASIGNAR participante a mesa (drop en la lista MEDIA)
    def handle_drop_on_participantes_list(self, event):
        # Logica que se ejecuta cuando soltamos un item en la lista de PARTICIPANTES (medio)
        try:
            nombre_participante = event.source().currentItem().text()
        except Exception as e:
            print(f"[ERROR] No se pudo obtener el nombre del participante arrastrado: {e}")
            return

        current_mesa_item = self.listWidgetMesas.currentItem()
        
        # Manejo de errores
        if not current_mesa_item:
            QMessageBox.warning(self, "Accion Invalida", "Por favor, selecciona una mesa de la lista 'Mesas' primero")
            return

        nombre_mesa = current_mesa_item.text().strip().upper()

        # Manejo de errores: No se puede asignar un participante al elemento "TODOS LOS PARTICIPANTES"
        if nombre_mesa == "TODOS LOS PARTICIPANTES":
            QMessageBox.warning(self, "Accion Invalida", "No puedes asignar un participante a 'TODOS LOS PARTICIPANTES'. Selecciona una mesa especifica")
            return

        # Finalmente asignando el participante a la mesa con el metodo asignar_participante_a_mesa
        print(f"[ACTION] Asignar: '{nombre_participante}' -> '{nombre_mesa}'")
        self.asignar_participante_a_mesa(nombre_participante, nombre_mesa)

    def handle_drop_on_sin_mesa_list(self, event):
        # Logica que se ejecuta cuando soltamos un item en la lista SIN MESA (derecha)
        # Desasignando la mesa del participante
        # Obteniendo el nombre
        try:
            nombre_participante = event.source().currentItem().text()
        except Exception as e:
            print(f"[ERROR] No se pudo obtener el nombre del participante arrastrado: {e}")
            return
            
        print(f"[ACTION] Desasignar: '{nombre_participante}' -> sin mesa")
        
        # Desasignando la mesa del participante
        self.desasignar_participante_de_mesa(nombre_participante)

    # Asignar mesa a un participante
    def asignar_participante_a_mesa(self, nombre_participante, nombre_mesa):
        try:
            numero_mesa = int(nombre_mesa.split(' ')[1])
            # Se busca el objeto Mesa para comprobar capacidad (la capacidad es 10 por defecto para todas las mesas)
            # Esta linea puede fallar si self.mesas_del_evento esta vacio o si el objeto mesa no tiene atributo 'numero'
            mesa_obj = next(m for m in self.mesas_del_evento if getattr(m, 'numero', None) == numero_mesa)
            
            # Chequeo de capacidad
            participantes_actuales = participante_manager.cargar_participantes_por_mesa(self.nombreEvento, numero_mesa)
            if len(participantes_actuales) >= 10: 
                QMessageBox.warning(self, "Advertencia", f"La {nombre_mesa} ya esta llena (Capacidad: 10). No se puede asignar a {nombre_participante}")
                return
                
        except (ValueError, IndexError, StopIteration):
            # En caso de StopIteration, significa que no se encontro la mesa_obj en self.mesas_del_evento.
            # Podria intentar buscar el objeto mesa de otra manera o asumir que existe ya que se pasa en nombre_mesa.
            QMessageBox.critical(self, "Error", f"'{nombre_mesa}' no es un objeto de mesa valido")
            return

        # Obtener participante y actualizar
        participante_obj = participante_manager.buscar_participante(self.nombreEvento, nombre_participante)
        if not participante_obj:
            QMessageBox.critical(self, "Error", f"No se pudo encontrar al participante '{nombre_participante}'")
            return
        
        # Si no hay chequeo de incompatibilidad, se asigna directamente

        participante_obj.mesa_asignada = numero_mesa
        nuevos_datos_list = [
            participante_obj.evento,
            participante_obj.nombre,
            participante_obj.acompanyantes,
            participante_obj.no_sentar_con,
            str(participante_obj.mesa_asignada)
        ]

        if participante_manager.actualizar_participante(self.nombreEvento, nombre_participante, nuevos_datos_list):
            print(f"[Exito] {nombre_participante} guardado en Mesa {numero_mesa}")
            self.refrescar_listas_mesas_tab()
            self.cargar_participantes_en_tabla()
        else:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo actualizar al participante '{nombre_participante}'")

    # Desasignar la mesa a un participante (volver a "sin mesa")
    def desasignar_participante_de_mesa(self, nombre_participante):
        # Quita la asignacion de mesa de un participante (la pone a None)
        participante_obj = participante_manager.buscar_participante(self.nombreEvento, nombre_participante)
        if not participante_obj:
            QMessageBox.critical(self, "Error", f"No se pudo encontrar al participante '{nombre_participante}'")
            return
            
        # Manejo de errores: Si ya esta sin mesa, no hacemos nada
        if participante_obj.mesa_asignada is None:
            print(f"[DEBUG] {nombre_participante} ya estaba sin mesa")
            return

        # Actualizando el objeto y creando la lista para el manager
        participante_obj.mesa_asignada = None
        
        nuevos_datos_list = [
            participante_obj.evento,
            participante_obj.nombre,
            participante_obj.acompanyantes,
            participante_obj.no_sentar_con,
            '' # Cadena vacia para indicar que no tiene mesa en el CSV
        ]

        # Guardar en el CSV
        if participante_manager.actualizar_participante(self.nombreEvento, nombre_participante, nuevos_datos_list):
            print(f"[Exito] {nombre_participante} desasignado correctamente (sin mesa)")
            
            # Refrescar TODAS las listas para mostrar el cambio
            self.refrescar_listas_mesas_tab() 
            self.cargar_participantes_en_tabla()
        else:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo actualizar al participante '{nombre_participante}'")

    # Actualizar listas
    def _manejar_cambio_mesa_seleccionada(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        if current_item:
            self.refrescar_listas_mesas_tab()

    def refrescar_listas_mesas_tab(self):
        todos_participantes = participante_manager.cargar_participantes_por_evento(self.nombreEvento)

        # DERECHA: sin mesa
        self.listWidgetParticipantesSinMesas.clear()
        # Filtrar solo participantes sin mesa asignada
        participantes_sin_mesa = [p for p in todos_participantes if p.mesa_asignada is None or str(p.mesa_asignada).strip() == ""]
        for p in participantes_sin_mesa:
            self.listWidgetParticipantesSinMesas.addItem(p.nombre)

        # MEDIO: participantes en la mesa seleccionada
        self.listWidgetParticipantes.clear()
        item_seleccionado = self.listWidgetMesas.currentItem()

        if item_seleccionado and item_seleccionado.text().strip().upper() != "TODOS LOS PARTICIPANTES":
            try:
                numero_mesa_sel = int(item_seleccionado.text().split(' ')[1])
                participantes_filtrados = participante_manager.cargar_participantes_por_mesa(self.nombreEvento, numero_mesa_sel)
                for p in participantes_filtrados:
                    self.listWidgetParticipantes.addItem(p.nombre)
            except (ValueError, IndexError):
                pass

    # Cargar informacion del evento 
    def cargar_info_evento(self):
        evento_obj = self.evento_obj
        if evento_obj:
            self.lblTituloEvento.setText(str(evento_obj.nombre))
            self.lblFecha.setText(str(evento_obj.fecha))
            self.lblUbicacion.setText(str(evento_obj.ubicacion))
            self.lblOrganizador.setText(str(evento_obj.organizador))
            self.lblMesas.setText(str(evento_obj.num_mesas))
            print(f"Informacion del evento '{self.nombreEvento}' cargada correctamente")
        else:
            QMessageBox.critical(self, "Error de Carga", "No se encontro la informacion del evento")
            self.volver_principal()

    # Cargar Mesas 
    # En este metodo se puede modificar la capacidad de participantes por mesa
    def cargar_mesas_en_listwidget(self):
        self.listWidgetMesas.clear()
        self.mesas_del_evento = []
        self.listWidgetMesas.addItem("TODOS LOS PARTICIPANTES")

        num_mesas = self.evento_obj.get_num_mesas() if self.evento_obj else 0
        for i in range(1, num_mesas + 1):
            mesa_obj = Mesa(i, 10) # Capacidad fija de 10
            self.mesas_del_evento.append(mesa_obj)
            self.listWidgetMesas.addItem(f"Mesa {i}")

        print(f"Cargadas {num_mesas} mesas")
        self.listWidgetMesas.setCurrentRow(0)


        # Cargando la tabla de participantes desde el CSV

    def cargar_tabla_con_participantes(self, participantes_lista, header="Nombre"):
        tabla = self.tablaParticipantes
        tabla.setRowCount(len(participantes_lista))
        tabla.setColumnCount(4)
        column_headers = [f'{header}', 'Acompanantes', 'No Sentar Con', 'Mesa']
        tabla.setHorizontalHeaderLabels(column_headers)

        # Bucle que por cada lista y objeto de la lista de participantes, rellena la tabla con los datos
        for fila, participante_obj in enumerate(participantes_lista):
            tabla.setItem(fila, 0, QTableWidgetItem(participante_obj.nombre))
            tabla.setItem(fila, 1, QTableWidgetItem(participante_obj.acompanyantes))
            tabla.setItem(fila, 2, QTableWidgetItem(participante_obj.no_sentar_con))
            # si la mesa tiene un numero, lo coge, sino le asigna por default "PENDIENTE"
            mesa_str = str(participante_obj.mesa_asignada) if participante_obj.mesa_asignada else "PENDIENTE" 
            tabla.setItem(fila, 3, QTableWidgetItem(mesa_str))

        tabla.resizeColumnsToContents()

    def cargar_participantes_en_tabla(self):
        # Este metodo carga todos los participantes sin filtro
        participantes_lista = participante_manager.cargar_participantes_por_evento(self.nombreEvento)
        self.cargar_tabla_con_participantes(participantes_lista)
        print("Lista de participantes cargada")

    # NUEVO METODO: Filtrar participantes basado en el texto del buscador
    def filtrar_participantes(self):
        # El widget existe debido a la corrección del objectName
        texto_busqueda = self.lneBuscadorParticipante.text().lower().strip()
        
        # Cargar todos los participantes del evento
        todos_participantes = participante_manager.cargar_participantes_por_evento(self.nombreEvento)
        
        # Si el campo de busqueda esta vacio, muestra todos
        if not texto_busqueda:
            participantes_filtrados = todos_participantes
        else:
            # Filtrar los participantes cuyo nombre contiene el texto de busqueda
            participantes_filtrados = [
                p for p in todos_participantes 
                if texto_busqueda in p.nombre.lower()
            ]
            
        # Recargar la tabla con la lista filtrada
        self.cargar_tabla_con_participantes(participantes_filtrados)
        print(f"Lista de participantes filtrada por: '{texto_busqueda}'")

    # Pop Up's
    def abrir_crear_participante(self):
        self.crear_participante_window = CrearParticipante(gestion_evento_window=self,
                                                           nombreEvento=self.nombreEvento)
        self.crear_participante_window.finished.connect(self.refrescar_listas_mesas_tab)
        self.crear_participante_window.show()

    def volver_principal(self):
        from Pantalla_Principal import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
        print("Volviendo a la pantalla principal")

    def abrir_actualizar_participante(self):
        filaSeleccionada = self.tablaParticipantes.currentRow()
        if filaSeleccionada == -1:
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un participante de la tabla")
            return

        try:
            nombreParticipante = self.tablaParticipantes.item(filaSeleccionada, 0).text()
        except AttributeError:
            QMessageBox.critical(self, "Error", "No se pudo obtener el nombre del participante")
            return

        self.popup_actualizar = ActualizarParticipante(gestion_window=self, nombre_participante=nombreParticipante)
        self.popup_actualizar.finished.connect(self.refrescar_listas_mesas_tab)
        self.popup_actualizar.show()

    def abrir_eliminar_participante(self):
        filaSeleccionada = self.tablaParticipantes.currentRow()
        if filaSeleccionada == -1:
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un participante de la tabla")
            return
        
        try:
            nombreParticipante = self.tablaParticipantes.item(filaSeleccionada, 0).text()
        except AttributeError:
            QMessageBox.critical(self, "Error", "No se ha podido obtener el nombre del participante")
            return
        
        self.popup_eliminar = EliminarParticipante(
            gestion_window=self, 
            nombre_evento=self.nombreEvento, 
            nombre_participante=nombreParticipante
        )

        self.popup_eliminar.finished.connect(self.refrescar_listas_mesas_tab)
        self.popup_eliminar.show()

    def generar_informe_csv(self):
        print("Iniciando a generar el informe de CSV")

        # Comprueba que el objeto evento esta cargado
        evento = self.evento_obj
        if not evento:
            QMessageBox.critical(self, "Error", "No se ha podido cargar la informacion del evento")
            return
        
        # Carga lista de todos los participantes de este evento
        todosParticipantes = participante_manager.cargar_participantes_por_evento(self.nombreEvento)

        # Sugiere automaticamente un nombre de archivo facil y descriptivo, como "Informe_Pepe.csv"
        nombreArchivoPorDefecto = f"Informe__{evento.nombre.replace(' ', '_')}.csv"

        options = QFileDialog.Options()
        # Permite al usuario elegir donde guardar abriendo dialogo
        filePath, _ = QFileDialog.getSaveFileName(self, "Guardar Informe CSV", nombreArchivoPorDefecto, "Archivos CSV (*.csv);;Todos los Archivos (*)", options=options)
            
        # Si el usuario cancela el dialogo
        if not filePath:
            print("La generacion del informe ha sido cancelada")
            return
            
        # Escribe el archivo CSV
        try:
            with open(filePath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                writer.writerow(['INFORME DEL EVENTO'])
                writer.writerow(['Nombre del Evento', evento.nombre]) 
                writer.writerow(['Organizador', evento.organizador]) 
                writer.writerow(['Fecha', evento.fecha])
                writer.writerow(['Ubicacion', evento.ubicacion])
                writer.writerow(['Total Mesas', evento.num_mesas])
                writer.writerow([])

                writer.writerow(['MESAS ASIGNADAS'])
                writer.writerow(['Nombre Mesa', 'Participantes Asignados'])

                num_mesas = evento.get_num_mesas()
                for i in range(1, num_mesas + 1):
                    # Encuentra los participantes para la mesa
                    participantes_en_mesa = [p for p in todosParticipantes if p.mesa_asignada == i]
                    nombres = ", ".join([p.nombre for p in participantes_en_mesa])
                    writer.writerow([f"Mesa {i}", nombres])    

                # Añade los participantes sin mesa asignada
                participantes_sin_mesa = [p for p in todosParticipantes if p.mesa_asignada is None or str(p.mesa_asignada).strip() == ""]
                nombres_sin_mesa = ", ".join([p.nombre for p in participantes_sin_mesa])
                writer.writerow(['Pendientes (Sin Asignar)', nombres_sin_mesa])
                writer.writerow([])

                # Preferencias y conflictos
                writer.writerow(['LISTA DE LAS PREFERENCIAS DE LOS PARTICIPANTES'])
                writer.writerow(['Participante', 'Preferencias (Acompañantes)', 'Incompatibilidades (No Sentar Con)'])

                for p in todosParticipantes:
                    writer.writerow([p.nombre, p.acompanyantes, p.no_sentar_con])

            QMessageBox.information(self, "Informe Generado", f"El informe ha sido guardado en:\n{filePath}")
            print(f"El informe guardado en {filePath}")

        # Captura algunos errores como por ejemplo si el archivo estuviera abierto
        except IOError as e:
            QMessageBox.critical(self, "Error al Escribir", f"No se pudo guardar el archivo:\n{e}")
            print(f"Error al escribir CSV: {e}")

        # Captura cualquier otro error inesperado
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", f"Ocurrio un error al generar el informe:\n{e}")
            print(f"Error inesperado: {e}")