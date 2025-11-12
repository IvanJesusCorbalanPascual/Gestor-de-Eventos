import csv
import os
from Evento import Evento # Importamos la clase Evento

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

    def guardar_evento(self, nuevo_evento: Evento):
        # Añade un nuevo evento al archivo CSV
        data = nuevo_evento.to_list() 
        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            return True
        except IOError:
            return False

    def cargar_eventos(self):
        # Lee y devuelve todos los eventos del archivo CSV como objetos Evento
        eventos = []
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Saltar los encabezados
                next(reader, None)  
                for row in reader:
                    if len(row) == len(HEADERS):
                         # Creamos un objeto Evento a partir de la fila del CSV
                         evento_obj = Evento.from_csv_row(row)
                         if evento_obj:
                            eventos.append(evento_obj)
        except FileNotFoundError:
            pass
        return eventos
    
    def eliminar_evento(self, nombre_evento):
        eventos_mantenidos = []
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)

                # Guarda el encabezado
                try:
                    eventos_mantenidos.append(next(reader))
                except StopIteration:
                    return False
                
                # Guardamos las filas que no coincidan con el nombre
                for row in reader:
                    if row and row[0] != nombre_evento:
                        eventos_mantenidos.append(row)

                # Hacemos que el archivo CSV se sobrescriba con los eventos mantenidos
                with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(eventos_mantenidos)
                return True
            
        except (IOError, FileNotFoundError) as e:
            print(f"Error encontrado al eliminar un evento: {e}")
            return False
        
    def buscar_evento(self, nombre_evento) -> Evento | None:
        # Busca y devuelve los datos de un evento por su nombre como objeto Evento
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Salta los encabezados
                next(reader, None)
                for row in reader:
                    if row and row[0] == nombre_evento:
                        return Evento.from_csv_row(row)
        except FileNotFoundError:
            pass
        return None 
    
    def actualizar_evento(self, nombre_original, nuevos_datos: list):
        # nuevos_datos DEBE ser una lista en formato [Nombre, Fecha, Ubicacion, Organizador, Num_Mesas]
        eventosActualizados = []
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Guarda el encabezado
                eventosActualizados.append(next(reader))

                for row in reader:
                    if row and row[0] == nombre_original:
                        eventosActualizados.append(nuevos_datos)
                    else:
                        eventosActualizados.append(row)

            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(eventosActualizados)
            return True
        except (IOError, FileNotFoundError):
            return False
                
# Instancia global del manager para usar en el resto de los modulos
event_manager = EventoManager()