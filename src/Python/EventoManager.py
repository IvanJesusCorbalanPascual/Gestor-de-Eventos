import csv
import os

CSV_FILE = 'eventos.csv'
HEADERS = ['Nombre', 'Fecha', 'Ubicacion', 'Organizador', 'Num_Mesas']

class EventoManager:
    # Clase para manejar la logica de datos (CSV) de los eventos
    def __init__(self):
        # Asegura que el archivo CSV exista con los encabezados al iniciar
        if not os.path.exists(CSV_FILE):
            self._crear_csv_inicial()
            
    def _crear_csv_inicial(self):
        # Crea el archivo CSV si no existe
        try:
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS)
        except IOError:
            pass

    def guardar_evento(self, data):
        # Añade un nuevo evento al archivo CSV
        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            return True
        except IOError:
            return False

    def cargar_eventos(self):
        # Lee y devuelve todos los eventos del archivo CSV
        eventos = []
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Saltar los encabezados
                next(reader, None)  
                for row in reader:
                    # Verifica que la fila tenga el numero correcto de columnas
                    if len(row) == len(HEADERS):
                         eventos.append(row)
        except FileNotFoundError:
            pass
        return eventos

# Instancia global del manager para usar en el resto de los modulos
event_manager = EventoManager()