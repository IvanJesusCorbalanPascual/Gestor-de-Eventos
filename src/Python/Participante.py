class Participante:
    # Clase para representar un Participante en un Evento
    def __init__(self, evento, nombre, acompanyantes="", no_sentar_con="", mesa_asignada=None):
        self.evento = evento
        self.nombre = nombre
        # Las preferencias se guardan como cadenas
        self.acompanyantes = acompanyantes 
        self.no_sentar_con = no_sentar_con
        # Almacena el numero de mesa asignado
        self.mesa_asignada = mesa_asignada 

    def to_list(self):
        # Devuelve los datos del participante como una lista para ser guardada en el CSV
        return [self.evento, self.nombre, self.acompanyantes, self.no_sentar_con, str(self.mesa_asignada) if self.mesa_asignada is not None else '']

    @staticmethod
    def from_csv_row(row):
        # Crea un objeto Participante a partir de una fila del CSV
        if len(row) >= 4:
            mesa = None
            if len(row) >= 5 and row[4].strip().isdigit():
                mesa = int(row[4].strip())
            
            return Participante(
                evento=row[0], 
                nombre=row[1], 
                acompanyantes=row[2], 
                no_sentar_con=row[3],
                mesa_asignada=mesa
            )
        return None