from datetime import datetime

class Evento:
    """
    Clase para representar un Evento.
    Define la estructura de los datos del evento.
    """
    # Formato de fecha usado por QDateTime y el CSV
    DATE_FORMAT = "yyyy-MM-dd hh:mm:ss"

    def __init__(self, nombre, fecha, ubicacion, organizador, num_mesas):
        self.nombre = nombre
        self.fecha = fecha  
        self.ubicacion = ubicacion
        self.organizador = organizador
        self.num_mesas = num_mesas # Almacenado como string, pero representa la cantidad.

    def to_list(self):
        """
        Devuelve los datos del evento como una lista para ser guardada en el CSV.
        Se mantiene el orden de los HEADERS del EventoManager.
        """
        return [self.nombre, self.fecha, self.ubicacion, self.organizador, self.num_mesas]

    @staticmethod
    def from_csv_row(row):
        """
        Crea un objeto Evento a partir de una fila (lista) leída del CSV.
        """
        if len(row) == 5:
            # Los datos del CSV deben estar en el orden: [Nombre, Fecha, Ubicacion, Organizador, Num_Mesas]
            return Evento(row[0], row[1], row[2], row[3], row[4])
        return None
    
    def get_num_mesas(self) -> int:
        """Devuelve el número de mesas como entero."""
        try:
            return int(self.num_mesas)
        except ValueError:
            return 0