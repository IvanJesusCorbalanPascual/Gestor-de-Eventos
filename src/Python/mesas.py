class Mesa:
    # Clase para representar una mesa dentro de un evento
    def __init__(self, numero_mesa: int, capacidad: int, participantes: list = None):
        self.numero = numero_mesa
        self.capacidad = capacidad
        # La lista almacenara objetos Participante
        self.participantes = participantes if participantes is not None else [] 

    def asientos_disponibles(self) -> int:
        # Calcula cuantos asientos quedan disponibles
        return self.capacidad - len(self.participantes)

    def asignar_participante(self, participante_obj):
        # Asigna un objeto Participante a esta mesa y actualiza el atributo
        # mesa_asignada del participante
        if self.asientos_disponibles() > 0:
            self.participantes.append(participante_obj)
            participante_obj.mesa_asignada = self.numero # Actualiza el objeto Participante
            return True
        return False

    def quitar_participante(self, nombre_participante: str):
        # Elimina un participante de la mesa por su nombre
        for i, p in enumerate(self.participantes):
            if p.nombre == nombre_participante:
                p.mesa_asignada = None # Resetea el atributo del objeto Participante
                del self.participantes[i]
                return True
        return False
        
    def to_csv_report_row(self) -> list:
        # Devuelve los datos de la mesa y sus participantes para el informe CSV
        nombres_participantes = ", ".join([p.nombre for p in self.participantes])
        return [f"Mesa {self.numero}", nombres_participantes]