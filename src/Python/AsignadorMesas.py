from ortools.sat.python import cp_model

class AsignadorMesas:
    
    def asignar_mesas(self, participantes, tamano_mesa, num_mesas):
        model = cp_model.CpModel()
        nombres = [p.nombre for p in participantes]

        if num_mesas<=0:
            print("Error, no hay mesas")
            return None

        # Variables: mesa asignada a cada persona
        mesas = {
            nombre: model.NewIntVar(0, num_mesas - 1, nombre)
            for nombre in nombres
        }

        # Restricciones de amistad y enemistad
        for p in participantes:
            lista_amigos = [nombre.strip() for nombre in p.acompanyantes.split(',') if nombre.strip()]
            
            for amigo in lista_amigos:
                if amigo in mesas:
                    model.Add(mesas[p.nombre] == mesas[amigo])
                        
            lista_enemigos = [nombre.strip() for nombre in p.no_sentar_con.split(',') if nombre.strip()]
            for enemigo in lista_enemigos:
                if enemigo in mesas:
                    model.Add(mesas[p.nombre] != mesas[enemigo])

        # Restricción de tamaño máximo por mesa
        # Usamos variables booleanas para controlar cuántas personas hay en cada mesa
        for m in range(num_mesas):
            # Para cada mesa, creamos indicadores de quién está allí
            indicators = []
            for nombre in nombres:
                b = model.NewBoolVar(f"{nombre}_en_mesa_{m}")
                # Si mesa[nombre] == m, entonces b = 1
                model.Add(mesas[nombre] == m).OnlyEnforceIf(b)
                model.Add(mesas[nombre] != m).OnlyEnforceIf(b.Not())
                indicators.append(b)
            # Máximo tamano_mesa personas por mesa
            model.Add(sum(indicators) <= tamano_mesa)

        # Resolver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        status = solver.Solve(model)

        # Resultado
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {nombre: solver.Value(mesas[nombre]) +1 for nombre in nombres}
        else:
            print("Error, No fue posible la asignacion de mesas")
            return None
