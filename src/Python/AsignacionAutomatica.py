from Participante import Participante
from EventoManager import event_manager
from ParticipanteManager import participante_manager
from PyQt5.QtWidgets import QMessageBox

# --- CLASES Y LOGICA DE ASIGNACION HEURISTICA ---

class Mesa:
    """Clase interna simple para la logica de asignacion."""
    def __init__(self, numero, capacidad):
        self.numero = numero
        self.capacidad = capacidad
        self.participantes = []
        self.nombres_participantes = set()

    def puede_aceptar(self, nuevo_participante: Participante, participante_map: dict) -> tuple[bool, int]:
        """
        Verifica si la mesa puede aceptar al participante.
        Devuelve (True/False, Puntuacion_Amistad).
        """
        # 1. CHEQUEO DE CAPACIDAD (Hard Constraint)
        if len(self.participantes) >= self.capacidad:
            return False, 0
        
        amistad_score = 0
        
        # 2. CHEQUEO DE INCOMPATIBILIDAD (Hard Constraint)
        
        # 2a. Chequea si el NUEVO participante tiene enemigos en la mesa
        for nombre_enemigo in nuevo_participante.get_enemistades():
            if nombre_enemigo in self.nombres_participantes:
                # Falla si hay un enemigo
                return False, 0 
        
        # 2b. Chequea si ALGUN participante en la MESA tiene al nuevo como enemigo
        for nombre_existente in self.nombres_participantes:
            existente_obj = participante_map.get(nombre_existente)
            if existente_obj and nuevo_participante.nombre in existente_obj.get_enemistades():
                # Falla si alguien en la mesa no quiere al nuevo
                return False, 0 
                
        # 3. CALCULO DE AMISTAD (Soft Constraint)
        # Suma 10 puntos por cada amigo en la mesa.
        for nombre_amigo in nuevo_participante.get_amistades():
            if nombre_amigo in self.nombres_participantes:
                amistad_score += 10 
                
        # 4. CALCULO DE AMISTAD INVERSA
        # Suma 10 puntos por cada participante en la mesa que sea amigo del nuevo.
        for nombre_existente in self.nombres_participantes:
            existente_obj = participante_map.get(nombre_existente)
            if existente_obj and nuevo_participante.nombre in existente_obj.get_amistades():
                amistad_score += 10 
                
        return True, amistad_score

    def asignar(self, participante: Participante):
        """Asigna el participante a la mesa."""
        self.participantes.append(participante)
        self.nombres_participantes.add(participante.nombre)


def asignar_mesas_heuristicas(participantes: list[Participante], num_mesas: int, capacidad_mesa: int):
    """
    Asigna mesas a los participantes usando una heuristica.
    1. Respetar incompatibilidades.
    2. Maximizar amistades.
    3. Balancear mesas.
    """
    
    # Inicializa mesas
    mesas = [Mesa(i + 1, capacidad_mesa) for i in range(num_mesas)]
    participante_map = {p.nombre: p for p in participantes}

    # Define prioridad de asignacion (mayor prioridad = mas restricciones)
    def prioridad_participante(p: Participante):
        # Doble peso a las enemistades para priorizar hard constraints
        peso_enemigo = len(p.get_enemistades()) * 2 
        peso_amigo = len(p.get_amistades())
        return peso_enemigo + peso_amigo

    # Ordena para asignar primero a los mas dificiles
    participantes_pendientes = sorted(participantes, key=prioridad_participante, reverse=True)
    
    participantes_no_asignados = []
    
    for p in participantes_pendientes:
        mejor_mesa = None
        mejor_score = -1
        
        # --- BUSQUEDA DE LA MEJOR MESA DISPONIBLE ---
        
        # calcula el score para cada mesa
        for mesa in mesas:
            es_valida, score = mesa.puede_aceptar(p, participante_map)
            
            if es_valida:
                # Prioriza la mesa con mejor score de amistad
                if score > mejor_score:
                    mejor_score = score
                    mejor_mesa = mesa
                # Score igual, prioriza mesas con menos gente
                elif score == mejor_score and (mejor_mesa is None or len(mesa.participantes) < len(mejor_mesa.participantes)):
                    mejor_mesa = mesa
        
        # Ejecuta la asignacion
        if mejor_mesa is not None:
            mejor_mesa.asignar(p)
        else:
            participantes_no_asignados.append(p.nombre)
            
    # Devuelve la solucion
    solucion = {}
    for mesa in mesas:
        for p in mesa.participantes:
            solucion[p.nombre] = mesa.numero
            
    return solucion, participantes_no_asignados


def ejecutar_asignacion_automatica(gestion_evento_window, nombre_evento: str):
    """
    Coordina la ejecucion de la asignacion automatica usando la heuristica.
    """
    
    evento = event_manager.buscar_evento(nombre_evento)
    
    # Obtiene numero de mesas y capacidad
    num_mesas = evento.get_num_mesas()
    capacidad_mesa = 10 
    
    # Chequea que haya mesas
    if num_mesas == 0:
        QMessageBox.warning(gestion_evento_window, "Advertencia", "El evento no tiene mesas definidas. Anade mesas antes de la asignacion automatica.")
        return

    # Carga los participantes
    todos_participantes = participante_manager.cargar_participantes_por_evento(nombre_evento)

    if not todos_participantes:
        QMessageBox.warning(gestion_evento_window, "Advertencia", "No hay participantes para asignar.")
        return

    # Ejecuta la heuristica
    solucion, participantes_no_asignados = asignar_mesas_heuristicas(todos_participantes, num_mesas, capacidad_mesa)

    participantes_actualizados = 0
    participantes_asignados = len(solucion)
    
    # Aplica la solucion a los objetos Participante y los guarda
    for p in todos_participantes:
        numero_mesa_asignada = solucion.get(p.nombre)
        
        if numero_mesa_asignada is not None:
            p.mesa_asignada = numero_mesa_asignada # Asigna el numero de mesa
        else:
            p.mesa_asignada = None # No asignado
        
        # Prepara los datos para actualizar el CSV
        nuevos_datos_list = [
            p.evento,
            p.nombre,
            p.acompanyantes, 
            p.no_sentar_con, 
            str(p.mesa_asignada) if p.mesa_asignada is not None else ''
        ]

        # Guarda en el CSV 
        if participante_manager.actualizar_participante(nombre_evento, p.nombre, nuevos_datos_list):
            participantes_actualizados += 1

    # Muestra el resultado
    if participantes_no_asignados:
        mensaje = f"Asignacion completada. Se asignaron {participantes_asignados} participantes, pero {len(participantes_no_asignados)} no pudieron ser asignados debido a conflictos de incompatibilidad o falta de capacidad."
        QMessageBox.warning(gestion_evento_window, "Asignacion Heuristica (Alerta)", mensaje)
    else:
        mensaje = f"Asignacion completada con exito. Se asignaron los {participantes_asignados} participantes respetando las incompatibilidades y priorizando amistades."
        QMessageBox.information(gestion_evento_window, "Asignacion Heuristica (Exito)", mensaje)
        
    # Recarga la interfaz de la ventana de gestion
    gestion_evento_window.recargar_datos_tras_actualizacion()


def encontrar_incompatibilidades(participantes: list[Participante]):
    """ (Funcion de reporte interna). Busca pares de participantes con enemistad mutua."""
    conflictos = []
    participante_map = {p.nombre: p for p in participantes}
    
    for nombre_p1, p1 in participante_map.items():
        for nombre_enemigo in p1.get_enemistades():
            if nombre_enemigo in participante_map:
                p2 = participante_map[nombre_enemigo]
                # Verifica si la enemistad es mutua y evita duplicados
                if nombre_p1 in p2.get_enemistades():
                    par = tuple(sorted((nombre_p1, nombre_enemigo)))
                    if par not in [tuple(sorted(c)) for c in conflictos]:
                        conflictos.append(par)
            
    return conflictos