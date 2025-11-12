# Gestion_Evento.py

import sys
import os
from PyQt5 import QtWidgets, uic, QtCore
from EventoManager import event_manager
from PopUp_participante import CrearParticipante, ActualizarParticipante, EliminarParticipante
from ParticipanteManager import participante_manager
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem, QMessageBox
from PyQt5.QtCore import QDataStream, QIODevice
from Evento import Evento
from mesas import Mesa
from PopUp_evento import ActualizarEvento 


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
        self.mesas_del_evento = []

        # Mapeo de botones
        self.btnVolver.clicked.connect(self.volver_principal)
        self.btnActualizarParticipante.clicked.connect(self.abrir_actualizar_participante)
        self.btnAnyadirParticipante.clicked.connect(self.abrir_crear_participante)
        self.btnEliminarParticipante.clicked.connect(self.abrir_eliminar_participante)
        
        # Correccion del error: Usar el nombre de boton existente en el UI (btnAnyadirMesa)
        # para la funcionalidad de Actualizar Mesas.
        self.btnAnyadirMesa.clicked.connect(self.abrir_actualizar_evento_para_mesas)
        self.btnEliminarMesa.clicked.connect(self.eliminar_mesa)

        # Conexiones de las listas
        self.listWidgetMesas.currentItemChanged.connect(self._manejar_cambio_mesa_seleccionada)

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

        # CARGA INICIAL DE DATOS
        self.cargar_info_evento()
        self.cargar_mesas_en_listwidget()
        self.cargar_participantes_en_tabla()
        self.refrescar_listas_mesas_tab()

        print("Consultando evento")

    # --- Funcionalidad de Mesas ---
    
    def abrir_actualizar_evento_para_mesas(self):
        # Reusa el pop-up de ActualizarEvento para modificar la cantidad de mesas
        # No se pasa main_window ya que GestionEvento se encarga de recargar la informacion
        self.popup_actualizar_evento = ActualizarEvento(main_window=None, nombreEvento=self.nombreEvento)
        
        # Conecta la senal finished para recargar las mesas y participantes
        self.popup_actualizar_evento.finished.connect(self.recargar_datos_tras_actualizacion)
        self.popup_actualizar_evento.show()
        
    def recargar_datos_tras_actualizacion(self):
        # Vuelve a buscar el evento actualizado y recarga las vistas
        self.evento_obj = event_manager.buscar_evento(self.nombreEvento)
        self.cargar_info_evento()
        self.cargar_mesas_en_listwidget()
        self.refrescar_listas_mesas_tab()
        self.cargar_participantes_en_tabla()
        
    def eliminar_mesa(self):
        item_seleccionado = self.listWidgetMesas.currentItem()
        
        if not item_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Selecciona una mesa para eliminar")
            return
            
        nombre_mesa_str = item_seleccionado.text().strip()

        if nombre_mesa_str.upper() == "TODOS LOS PARTICIPANTES":
            QMessageBox.warning(self, "Advertencia", "No puedes eliminar 'TODOS LOS PARTICIPANTES'")
            return
            
        try:
            # Obtener el numero de mesa
            numero_mesa_a_eliminar = int(nombre_mesa_str.split(' ')[1])
            
            # Buscar el objeto mesa
            mesa_obj = next(m for m in self.mesas_del_evento if m.numero == numero_mesa_a_eliminar)
        except (ValueError, IndexError, StopIteration):
            QMessageBox.critical(self, "Error", f"No se pudo identificar la mesa: {nombre_mesa_str}")
            return

        # 1. Chequeo de participantes
        participantes_en_mesa = participante_manager.cargar_participantes_por_mesa(self.nombreEvento, numero_mesa_a_eliminar)
        if participantes_en_mesa:
            respuesta = QMessageBox.question(self, "Confirmacion", 
                                             f"La {nombre_mesa_str} tiene {len(participantes_en_mesa)} participantes asignados. \n\n¿Deseas moverlos a 'Sin Mesa' y reducir el numero total de mesas?", 
                                             QMessageBox.Yes | QMessageBox.No)
            if respuesta == QMessageBox.No:
                return

            # Mover participantes a "Sin Mesa"
            for p in participantes_en_mesa:
                self.desasignar_participante_de_mesa(p.nombre)

        # 2. Actualizar el numero de mesas del Evento
        self.evento_obj.num_mesas = str(self.evento_obj.get_num_mesas() - 1)
        
        nuevos_datos_evento = [
            self.evento_obj.nombre, 
            self.evento_obj.fecha, 
            self.evento_obj.ubicacion, 
            self.evento_obj.organizador, 
            self.evento_obj.num_mesas
        ]

        if event_manager.actualizar_evento(self.nombreEvento, nuevos_datos_evento):
            QMessageBox.information(self, "Mesa Eliminada", f"{nombre_mesa_str} ha sido eliminada. El numero total de mesas ha sido reducido")
            # Recargar despues de modificar el manager para que se actualice el UI de gestion
            self.recargar_datos_tras_actualizacion() 
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el numero de mesas del evento")
            
    # --- FIN Funcionalidad de Mesas ---


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
        """
        if deteccion_incompatibilidades:
            print("Se ha detectado una incompatibilidad")
        """
        


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
            mesa_obj = next(m for m in self.mesas_del_evento if getattr(m, 'numero', None) == numero_mesa)
            
            # Chequeo de capacidad
            participantes_actuales = participante_manager.cargar_participantes_por_mesa(self.nombreEvento, numero_mesa)
            if len(participantes_actuales) >= 10: 
                QMessageBox.warning(self, "Advertencia", f"La {nombre_mesa} ya esta llena (Capacidad: 10). No se puede asignar a {nombre_participante}")
                return
                
        except (ValueError, IndexError, StopIteration):
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
        column_headers = [f'{header}', 'Acompañantes', 'No Sentar Con', 'Mesa']
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
        participantes_lista = participante_manager.cargar_participantes_por_evento(self.nombreEvento)
        self.cargar_tabla_con_participantes(participantes_lista)
        print("Lista de participantes cargada")

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