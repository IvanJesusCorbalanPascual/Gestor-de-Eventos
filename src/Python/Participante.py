class Participante:
    """
    Clase para representar un Participante en un Evento.
    Define la estructura de los datos del participante y sus preferencias.
    """
    def __init__(self, evento, nombre, acompanyantes="", no_sentar_con="", mesa_asignada=None):
        self.evento = evento
        self.nombre = nombre
        # Las preferencias se guardan como cadenas. Asume que 'acompañantes' es un nombre/lista de nombres
        self.acompanyantes = acompanyantes 
        self.no_sentar_con = no_sentar_con
        # Almacena el número de mesa asignado
        self.mesa_asignada = mesa_asignada 

    def to_list(self):
        """
        Devuelve los datos del participante como una lista para ser guardada en el CSV.
        Incluimos la mesa asignada para persistencia.
        """
        # Se guarda: [Evento, Nombre, Acompañantes, NoSentarCon, MesaAsignada]
        return [self.evento, self.nombre, self.acompanyantes, self.no_sentar_con, str(self.mesa_asignada)]

    @staticmethod
    def from_csv_row(row):
        """
        Crea un objeto Participante a partir de una fila (lista) leída del CSV.
        """
        # Debe manejar 5 o 4 columnas si el CSV es antiguo o no tiene la columna de mesa
        if len(row) >= 4:
            mesa = int(row[4]) if len(row) >= 5 and row[4].isdigit() else None
            return Participante(
                evento=row[0], 
                nombre=row[1], 
                acompanyantes=row[2], 
                no_sentar_con=row[3],
                mesa_asignada=mesa
            )
        return None