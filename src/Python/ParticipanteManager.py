import csv
import os

CSV_FILE_PARTICIPANTES = 'participantes.csv'
HEADERS_PARTICIPANTES = ['Evento', 'Nombre', 'Acompanyantes', 'NoSentarCon']

class ParticipanteManager:
    # Clase para manejar la logica de datos CSV de los participantes
    def __init__(self):
        # Asegura que el archivo CSV exista con los encabezados al iniciar
        if not os.path.exists(CSV_FILE_PARTICIPANTES):
            self._crear_csv_inicial()
            
    def _crear_csv_inicial(self):
        # Crea el archivo CSV si no existe
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS_PARTICIPANTES)
        except IOError:
            pass

    def guardar_participante(self, nombre_evento, nombre, acompanyantes, no_sentar_con):
        # Añade un nuevo participante al archivo CSV
        data = [nombre_evento, nombre, acompanyantes, no_sentar_con]
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            return True
        except IOError:
            return False

    def cargar_participantes_por_evento(self, nombre_evento):
        # Lee y devuelve todos los participantes de un evento especifico
        participantes = []
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Saltar los encabezados
                next(reader, None)  
                for row in reader:
                    # Verifica que el participante pertenezca al evento
                    if len(row) == len(HEADERS_PARTICIPANTES) and row[0] == nombre_evento:
                         participantes.append(row)
        except FileNotFoundError:
            pass
        return participantes
    
    def buscar_participante(self, nombre_evento, nombre_participante):
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if row and row[0] == nombre_evento and row[1] == nombre_participante:
                        return row
        except FileNotFoundError:
            pass
        return None
    
    def actualizar_participante(self, nombre_evento, nombre_original, nuevos_datos_completos):
        filas_actualizadas = []
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                filas_actualizadas.append(next(reader))

                for row in reader:
                    if row and row[0] == nombre_evento and row[1] == nombre_original:
                        filas_actualizadas.append(nuevos_datos_completos)
                    else:
                        filas_actualizadas.append(row)

            with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(filas_actualizadas)
            return True
        except (IOError, FileNotFoundError):
            return False
# Instancia global del manager para usar en el resto de los modulos
participante_manager = ParticipanteManager()