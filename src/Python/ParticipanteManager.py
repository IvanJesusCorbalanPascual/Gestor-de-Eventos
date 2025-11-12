# ParticipanteManager.py

import csv
import os
from Participante import Participante # Importamos la clase Participante

CSV_FILE_PARTICIPANTES = 'participantes.csv'
# Se añade 'Mesa_Asignada' al HEADER
HEADERS_PARTICIPANTES = ['Evento', 'Nombre', 'Acompanyantes', 'NoSentarCon', 'Mesa_Asignada'] 

class ParticipanteManager:
    # Clase para manejar la logica de datos CSV de los participantes
    def __init__(self):
        if not os.path.exists(CSV_FILE_PARTICIPANTES):
            self._crear_csv_inicial()
            
    def _crear_csv_inicial(self):
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS_PARTICIPANTES)
        except IOError:
            pass

    def guardar_participante(self, nuevo_participante: Participante):
        # Añade un nuevo participante al archivo CSV usando el metodo to_list()
        data = nuevo_participante.to_list() 
        try:
            # mode 'a' viene de append, que añade lineas en vez de sobreescribirlas
            with open(CSV_FILE_PARTICIPANTES, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            return True
        except IOError:
            return False

    def cargar_participantes_por_evento(self, nombre_evento) -> list[Participante]:
        # Lee y devuelve todos los participantes de un evento especifico como objetos Participante
        participantes = []
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Saltar los encabezados
                next(reader, None)  
                for row in reader:
                    # Se verifica que el participante pertenezca al evento y la longitud minima
                    if len(row) >= 4 and row[0] == nombre_evento:
                         # Creamos un objeto Participante a partir de la fila del CSV
                         participante_obj = Participante.from_csv_row(row)
                         if participante_obj:
                            participantes.append(participante_obj)
        except FileNotFoundError:
            pass
        return participantes
    
    def cargar_participantes_por_mesa(self, nombre_evento, numero_mesa: int) -> list[Participante]:
        # Nuevo metodo: Devuelve todos los participantes asignados a una mesa especifica
        participantes = self.cargar_participantes_por_evento(nombre_evento)
        # Filtra los participantes por el numero de mesa
        return [p for p in participantes if p.mesa_asignada == numero_mesa]
    
    # Metodo para buscar un solo participante por nombre y evento
    def buscar_participante(self, nombre_evento, nombre_participante):
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  
                for row in reader:
                    # Comprueba Evento (Columna 0) y Nombre (Columna 1)
                    if len(row) >= 4 and row[0] == nombre_evento and row[1] == nombre_participante:
                         return Participante.from_csv_row(row)
        except FileNotFoundError:
            pass
        return None 
    
    # Nuevo metodo para actualizar los datos de un participante
    def actualizar_participante(self, nombre_evento, nombre_original, nuevos_datos_list):
        participantes_actualizados = []
        actualizado = False
        
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Guarda el encabezado
                participantes_actualizados.append(next(reader))

                for row in reader:
                    # Identifica el participante por su Evento y su Nombre original
                    if row and row[0] == nombre_evento and row[1] == nombre_original:
                        participantes_actualizados.append(nuevos_datos_list)
                        actualizado = True
                    else:
                        participantes_actualizados.append(row)

            # Sobrescribir el archivo solo si se encontro y actualizo el participante
            if actualizado:
                with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(participantes_actualizados)
                return True
            return False # No se encontro el participante original
        except (IOError, FileNotFoundError):
            return False
        
    def eliminar_participante(self, nombre_evento, nombre_participante):
            participantesMantenidos = []
            eliminado = False
            try:
                with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)

                    # Se encarga de guardar el encabezado, a menos que el archivo este vacio
                    try:
                        participantesMantenidos.append(next(reader))
                    except StopIteration:
                        return False
            
                    for row in reader:
                            # Si tiene el mismo evento y mismo nombre, lo borra, si no, conservamos la fila
                            if row[0] == nombre_evento and row[1] == nombre_participante:
                                eliminado = True
                            else:
                                participantesMantenidos.append(row)

                if eliminado:
                    with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerows(participantesMantenidos)
                    return True
            
                return False
    
            except (IOError, FileNotFoundError) as e:
                print(f"No se ha podido eliminar un participante: {e}")
                return False

# Instancia global del manager para usar en el resto de los modulos
participante_manager = ParticipanteManager()