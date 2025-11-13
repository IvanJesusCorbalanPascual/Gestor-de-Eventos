class Participante:
    print("[DEBUG] Participante.py: Clase Participante definida.")
    # Clase para representar un Participante en un Evento
    def __init__(self, evento, nombre, acompanyantes="", no_sentar_con="", mesa_asignada=None):
        self.evento = evento
        self.nombre = nombre
        # Las preferencias se guardan como cadenas (Nombres de atributos originales)
        self.acompanyantes = acompanyantes 
        self.no_sentar_con = no_sentar_con
        # Almacena el numero de mesa asignado
        self.mesa_asignada = mesa_asignada 

    # Metodos para obtener las preferencias como listas de nombres (para el algoritmo)
    def get_amistades(self):
        print(f"[DEBUG] Participante.py: get_amistades llamado para {self.nombre}")
        # Convierte la cadena de acompanyantes a una lista de nombres. 
        if self.acompanyantes and self.acompanyantes.strip():
            # Limpia espacios extra y retorna la lista
            return [n.strip() for n in self.acompanyantes.split(',') if n.strip()]
        return []

    def get_enemistades(self):
        print(f"[DEBUG] Participante.py: get_enemistades llamado para {self.nombre}")
        # Convierte la cadena de no_sentar_con a una lista de nombres.
        if self.no_sentar_con and self.no_sentar_con.strip():
            return [n.strip() for n in self.no_sentar_con.split(',') if n.strip()]
        return []

    def to_list(self):
        print(f"[DEBUG] Participante.py: to_list llamado para {self.nombre}")
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