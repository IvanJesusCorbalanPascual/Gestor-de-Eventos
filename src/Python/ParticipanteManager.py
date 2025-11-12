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

    def cargar_participantes_por_evento(self, nombre_evento: str):
        # Lee y devuelve todos los participantes de un evento especifico como objetos Participante
        participantes = []
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None) # Salta los encabezados
                for row in reader:
                    if row and row[0] == nombre_evento:
                        participante_obj = Participante.from_csv_row(row)
                        if participante_obj:
                            participantes.append(participante_obj)
        except FileNotFoundError:
            pass
        return participantes

    def cargar_participantes_por_mesa(self, nombre_evento: str, numero_mesa: int):
        # Lee y devuelve los participantes asignados a una mesa especifica de un evento
        participantes = []
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None) # Salta los encabezados
                for row in reader:
                    if row and row[0] == nombre_evento:
                        if len(row) > 4 and row[4].strip() == str(numero_mesa):
                            participante_obj = Participante.from_csv_row(row)
                            if participante_obj:
                                participantes.append(participante_obj)
        except FileNotFoundError:
            pass
        return participantes

    def buscar_participante(self, nombre_evento: str, nombre_participante: str):
        # Busca un participante por nombre en un evento especifico
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None) # Salta los encabezados
                for row in reader:
                    if row and row[0] == nombre_evento and row[1] == nombre_participante:
                        return Participante.from_csv_row(row)
        except FileNotFoundError:
            pass
        return None

    def actualizar_participante(self, nombre_evento: str, nombre_participante_original: str, nuevos_datos: list):
        # Actualiza la informacion de un participante en el CSV
        participantesActualizados = []
        actualizado = False
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Guarda el encabezado
                participantesActualizados.append(next(reader))

                for row in reader:
                    if row and row[0] == nombre_evento and row[1] == nombre_participante_original:
                        participantesActualizados.append(nuevos_datos)
                        actualizado = True
                    else:
                        participantesActualizados.append(row)

            if actualizado:
                with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(participantesActualizados)
                return True
            return False
        
        except (IOError, FileNotFoundError):
            return False
            
    def eliminar_participante(self, nombre_evento: str, nombre_participante: str):
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

    # NUEVO METODO: Renumeracion de mesas tras eliminacion
    def renumerar_mesas_tras_eliminacion(self, nombre_evento: str, mesa_eliminada: int) -> bool:
        """
        Elimina la mesa asignada a los participantes de la mesa_eliminada 
        y decrementa en 1 la mesa asignada a todos los participantes con una mesa superior.
        """
        filas_actualizadas = []
        actualizado = False
        try:
            with open(CSV_FILE_PARTICIPANTES, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                # Guarda el encabezado
                try:
                    filas_actualizadas.append(next(reader))
                except StopIteration:
                    return False

                for row in reader:
                    # Solo procesar filas del evento correcto
                    if row[0] == nombre_evento:
                        
                        # La mesa esta en la columna 4 (indice 4)
                        mesa_actual_str = row[4].strip() if len(row) > 4 else ''
                        
                        try:
                            mesa_actual_num = int(mesa_actual_str)
                        except ValueError:
                            # No tiene mesa asignada o no es un numero, se mantiene la fila
                            filas_actualizadas.append(row)
                            continue
                            
                        # Logica de reasignacion/renumeracion
                        if mesa_actual_num == mesa_eliminada:
                            # 1. Mesa eliminada: Se desasigna (mesa = '')
                            row[4] = ''
                            actualizado = True
                        elif mesa_actual_num > mesa_eliminada:
                            # 2. Mesas superiores: Se decrementa el numero de mesa
                            row[4] = str(mesa_actual_num - 1)
                            actualizado = True

                    filas_actualizadas.append(row)

            # Si hubo algun cambio, se sobreescribe el archivo
            if actualizado:
                with open(CSV_FILE_PARTICIPANTES, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(filas_actualizadas)
            
            return actualizado
        
        except (IOError, FileNotFoundError) as e:
            print(f"Error al renumerar mesas: {e}")
            return False


# Instancia global del manager para usar en el resto de los modulos
participante_manager = ParticipanteManager()