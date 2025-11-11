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
        # Nota: Idealmente, aquí deberías verificar si la columna 'Mesa_Asignada'
        # existe en el CSV si ya existe el archivo, y añadirla si no está.
            
    def _crear_csv_inicial(self):
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS_PARTICIPANTES)
        except IOError:
            pass

    def guardar_participante(self, nuevo_participante: Participante):
        # Añade un nuevo participante al archivo CSV usando el método to_list()
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
                    # Se verifica que el participante pertenezca al evento y la longitud mínima
                    if len(row) >= 4 and row[0] == nombre_evento:
                         # Creamos un objeto Participante a partir de la fila del CSV
                         participante_obj = Participante.from_csv_row(row)
                         if participante_obj:
                            participantes.append(participante_obj)
        except FileNotFoundError:
            pass
        return participantes
    
    # Método para buscar un solo participante por nombre y evento
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
    
    # Nuevo método para actualizar los datos de un participante
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

            # Sobrescribir el archivo solo si se encontró y actualizó el participante
            if actualizado:
                with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(participantes_actualizados)
                return True
            return False # No se encontró el participante original
        except (IOError, FileNotFoundError):
            return False

# Instancia global del manager para usar en el resto de los modulos
participante_manager = ParticipanteManager()