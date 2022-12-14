from gurobipy import GRB, Model, quicksum
from gurobipy import *
import pandas as pd
import numpy as np
from archivos.carga_datos import *
import matplotlib.pyplot as plt

#------------------------- IMPORTANTE -------------------------#

# Este código está modificado para poder hacer las pruebas de análisis de sensibilidad.
# Se repite la ejecución del código para distintos multiplicadores de demanda, costo
# de almacenamiento, y distintas cantidades de camiones. Todo lo que está dentro de los
# ciclos for corresponde a la definición del modelo, y lo que está antes define los diccionarios
# que se usarán en cada iteración. 

model = Model()
model.setParam("TimeLimit", 60*30) # 30 min time limit

#------------------------- Conjuntos iniciales -------------------------#
paises = ["Chile", "Argentina"]
tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
rutas = ["Norte", "Centro", "Sur"]

#------------------------- Importación de datos de csv -------------------------#
alimentos, cant_por_tipo, total_alimentos = alimentos(tipos)
costo_adicional_camiones = costo_adicional_camiones()
costo_combustible = costo_combustible()
costo_fijo_almacenamiento = costo_fijo_almacenamiento()
costo_mantencion = costo_mantencion()
costo_ruta = costo_ruta()
costo_unitario_almacenamiento = costo_unitario_almacenamiento()
demanda = demanda(tipos)
distancia_por_pais = distancia_por_pais(rutas)
peso_promedio = peso_promedio(tipos)
stock_inicial = stock_inicial(tipos)
sueldo = sueldo()

#------------------------------- Rangos -------------------------------#
cant_de_centros = 1
cant_de_bodegas = 1
cant_de_camiones = 15
tmax = 10

T = range(1, tmax + 1)    #tiempo
I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento
R = range(1, len(rutas) + 1) # 1:Norte, 2:Centro, 3:Sur
P = range(1, len(paises) + 1) # 1:Chile, 2:Argentina
E = range(1, cant_de_camiones + 1)

# Arrays para pruebas
pruebas = [0,1,2]
demandas = [1,1.25,1.5]
array_camiones =  [9,13,17]
mult_costo_alm = [1,1.5,2]

# Array para guardar valores óptimos luego de terminado el TimeLimit
valores_objetivo = np.zeros((3,3))

# Arrays auxiliares para graficar
times = T
fa = 1
fi = 1
fk = K
fe = E

#------------------------- MODELO -------------------------#

for prueba in pruebas:
    for p in range(3):
        model.setParam("TimeLimit", 30)        
        #------------------------- Parámetros -------------------------#

        print("Definiendo parámetros")
        dict_rutas = {1:"Norte", 2:"Centro", 3:"Sur"}
        dict_paises = {1:"Chile", 2:"Argentina"}

        dict_tipos = dict(zip(I, tipos))
        # dict_tipos =  {1: 'Hortofruticola', 2: 'Congelado', 3: 'Refrigerado'}

        dict_alimentos = {}
        for i in I:
            dict_alimentos[i] = dict(zip(A,alimentos[dict_tipos[i]]))
        # dict_alimentos = {
        # 1: {1: 'Manzana', 2: 'Pera', 3: 'Naranja'}, 
        # 2: {1: 'Pollo', 2: 'Camaron', 3: 'Hamburguesa'}, 
        # 3: {1: 'Queso', 2: 'Yogur', 3: 'Jamon'}
        # }

        # Carga, transporte y almacenamiento
        if prueba == 1: # Prueba de distintas cantidades de camiones
            cant_de_camiones = array_camiones[p]
        flota_de_camiones = np.array([cant_de_camiones,cant_de_camiones,cant_de_camiones])

        N_i = {(i): flota_de_camiones[j] for (i,j) in zip(I,range(len(I)))}
        R_i = {"1": "Norte", "2": "Centro", "3": "Sur"}
        V_m = 90 # 90 m3 es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
        P_m = 25000 # 31000 kg es lo más común (ver fuentes de abajo), el valor fue reducido para mayor distribución de camiones.
        CFB_i = {(i): int(costo_fijo_almacenamiento[dict_tipos[i]]) for i in I}
        CTr_i = {(i): int(costo_adicional_camiones[dict_tipos[i]]) for i in I}
        
        if prueba == 2: # Prueba de distintos costos unitarios de almacenamiento
            CAl_i = {(i): float(costo_unitario_almacenamiento[dict_tipos[i]])*mult_costo_alm[p] for i in I} # Arreglar este valor
        else:
            CAl_i = {(i): float(costo_unitario_almacenamiento[dict_tipos[i]]) for i in I} # Arreglar este valor

        q_ai = {(a,i): int(stock_inicial[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
        Omega = 10000000

        # Propiedades de los alimentos
        if prueba == 0: # Prueba de distintas demandas de alimentos
            d_ai = {(a,i): int(round(int(demanda[dict_tipos[i]][dict_alimentos[i][a]])*demandas[p])) for i in I for a in A}
        else:
            d_ai = {(a,i): int(round(int(demanda[dict_tipos[i]][dict_alimentos[i][a]]))) for i in I for a in A}

        P_ai = {(a,i): float(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}

        # Ruta
        l_rp = {(r,p): int(distancia_por_pais[dict_rutas[r]][dict_paises[p]]) for r in R for p in P}
        PC_p = {(p): int(int(costo_combustible[dict_paises[p]])) for p in P}
        PT_r = {(r): int(costo_ruta[dict_rutas[r]]) for r in R}
        S_r = {(r): int(sueldo[dict_rutas[r]]) for r in R}
        M_r = {(r): int(costo_mantencion[dict_rutas[r]]) for r in R}

        ### Fuentes de los datos
        # Camiones terrestres (pequeños): 90 m3, 12000 kg https://www.avantiatransportes.com/capacidad-de-carga-transporte-terrestre/ 
        # Camiones trailer box (más grandes): 90 m3, 31400 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/camion-trailer-box-o-camion-furgon
        # Camiones frigoríficos: 85 m3, 31000 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/trailer-frigorifico-o-camion-frigo
        # Camiones para congelados: 85 m3, 31000 kg (mismo que arriba) http://www.frigocargo.cl/#project
        # Se utiliza en algunos camiones este equipo de enfriamiento https://tkadvancer.thermokinginfo.com/upload/whisper-pro/publication/TK80063_Whisper_Pro_Brochure_05-2021_ES_V2.0_spread.pdf
        print("Parámetros definidos")

        #------------------------- Variables -------------------------#
        print("Definiendo variables")
        Cam = model.addVars(E, I, J, K, T, vtype=GRB.BINARY, name="Cam")
        Tr = model.addVars(A, I, J, K, T, E, vtype=GRB.CONTINUOUS, name="Tr")
        Al = model.addVars(A, I, K, T, vtype=GRB.CONTINUOUS, name="Al")
        ExT = model.addVars(A, I, K, T, vtype=GRB.CONTINUOUS, name="ExT")
        print("Variables definidas")
        #------------------------- Restricciones -------------------------#
        print("Agregando restricciones")

        # Cada camión puede llevar 1 solo tipo de cosas
        model.addConstrs((quicksum(Cam[e,i,j,k,t] for j in J for k in K for i in I) <= 1 for t in T for e in E), name="R2")

        # No se pueden llevar más camiones de la cantidad total que hay en cada tiempo.
        model.addConstrs((quicksum(Cam[e,i,j,k,t] for j in J for k in K for e in E for i in I) <= cant_de_camiones for t in T), name="R2b")

        # Si no se transporta nada, Cam = 0
        model.addConstrs((Cam[e,i,j,k,t]*(1/Omega) <= quicksum(Tr[a,i,j,k,t,e] for a in A) for i in I for j in J for t in T for k in K for e in E), name="R4")

        # Restricción sobre peso máximo de los camiones
        model.addConstrs((quicksum(Tr[a,i,j,k,t,e]*P_ai[(a,i)] for a in A ) <= P_m for i in I for j in J for k in K for t in T for e in E), name="Rpeso")

        # Restricción para que si se transportan alimentos, entonces Cam = 1
        model.addConstrs((quicksum(Tr[a,i,j,k,t,e] for a in A)*(1/Omega) <= Cam[e,i,j,k,t] for i in I for e in E for t in T for j in J for k in K), name="R4cond")

        # Restricción de inventario inicial
        model.addConstrs((Al[a,i,k,1] == quicksum(Tr[a,i,j,k,1,e] for j in J for e in E) - ExT[a,i,k,1] for i in I for a in A for k in K), name="R9")

        # Inventario del almacén
        # Lo que entra: suma sobre (j, e) Tr[a,i,j,k,t,e] forall t a i k
        # lo que queda del tiempo anterior: Al[a,i,k,t-1]
        # Lo que sale: ExT[a,i,k,t]
        # Lo que queda del tiempo final: Al[a,i,k,t]
        for t in T:
            if t > 1:
                print(f"t={t}")
                model.addConstrs((quicksum(Tr[a,i,j,k,t,e] for j in J for e in E) + Al[a,i,k,t-1] - ExT[a,i,k,t] == Al[a,i,k,t] for a in A for k in K for i in I), name="R5final")
 

        # Todo lo que se extrae de todas las bodegas es igual a la demanda
        model.addConstrs((quicksum(ExT[a,i,k,t] for k in K) == d_ai[(a,i)] for a in A for i in I for t in T), name="R7")

        #------------------------- Función objetivo -------------------------#

        # Costo por transporte
        obj = quicksum((PT_r[i]+S_r[i]+quicksum(l_rp[(i,p)]*PC_p[p] for p in P) + M_r[i] + CTr_i[i])*Cam[e,i,j,k,t] for e in E for t in T for i in I for j in J for k in K)

        # Costo por almacenamiento
        obj += quicksum(CFB_i[i] + CAl_i[i]*quicksum(Al[a,i,k,t] for a in A) for t in T for i in I for k in K)

        #------------------------- Minimización de costos -------------------------#

        # Minimización
        model.setObjective(obj, GRB.MINIMIZE)
        model.optimize()

        status = model.status
        if status == GRB.UNBOUNDED:
            print("The model cannot be solved because it is unbounded")
        elif status == GRB.OPTIMAL:
            print("The optimal objective is %g" %model.ObjVal)
            print("El costo minimizado es de",model.ObjVal,"CLP durante todo el año.")
        else:
            print("Optimization was stopped with status %d" %status)

        if status == GRB.INFEASIBLE:
            print("Computing IIS")
            model.computeIIS()
            if model.IISMinimal:
                print("IIS is minimal.")
            else:
                print("IIS is not minimal.")
            print("\nThe following constraint(s) cannot be satisfied:")
            for c in model.getConstrs():
                if c.IISConstr:
                    print("%s" %c.constrName)
                
        # Guardado de valores objetivoo
        valores_objetivo[prueba, p] = model.ObjVal
        print(f"El valor objetivo guardado es {valores_objetivo[prueba,p]}")
        #------------------------- Escritura de datos en resultados -------------------------#

        sol_Tr = ""
        sol_Cam = ""
        sol_Al = ""
        sol_ExT = ""


        for t in T:
            for i in I:
                for a in A:
                    for j in J:
                        for k in K:
                            for e in E:
                                sol_Tr += f" \n{int(Tr[a,i,j,k,t,e].x)},{a},{i},{j},{k},{t},{e}"

                    for k in K:
                            sol_Al += f" \n{int(Al[a,i,k,t].x)},{a},{i},{k},{t}"
                for k in K:
                    for j in J:
                        for e in E:
                            sol_Cam += f" \n{int(Cam[e,i,j,k,t].x)},{e},{i},{j},{k},{t}"    
                    for a in A:
                        for t in T:
                            sol_ExT += f" \n{int(ExT[a,i,k,t].x)},{a},{i},{k},{t}"

        if prueba == 0:
            with open(f"resultados/resultados_Tr_demanda_{str(demandas[p])}.csv", "w") as file:
                file.write("Tr,a,i,j,k,t,e")
                file.write(sol_Tr)

            with open(f"resultados/resultados_Cam_demanda_{str(demandas[p])}.csv", "w") as file:
                file.write("Cam,e,i,j,k,t")
                file.write(sol_Cam)

            with open(f"resultados/resultados_Al_demanda_{str(demandas[p])}.csv", "w") as file:
                file.write("Al,a,i,k,t")
                file.write(sol_Al)

            with open(f"resultados/resultados_ExT_demanda_{str(demandas[p])}.csv", "w") as file:
                file.write("ExT,a,i,k,t")
                file.write(sol_ExT)

        elif prueba == 1:
            with open(f"resultados/resultados_Tr_camiones_{str(array_camiones[p])}.csv", "w") as file:
                file.write("Tr,a,i,j,k,t,e")
                file.write(sol_Tr)

            with open(f"resultados/resultados_Cam_camiones_{str(array_camiones[p])}.csv", "w") as file:
                file.write("Cam,e,i,j,k,t")
                file.write(sol_Cam)

            with open(f"resultados/resultados_Al_camiones_{str(array_camiones[p])}.csv", "w") as file:
                file.write("Al,a,i,k,t")
                file.write(sol_Al)

            with open(f"resultados/resultados_ExT_camiones_{str(array_camiones[p])}.csv", "w") as file:
                file.write("ExT,a,i,k,t")
                file.write(sol_ExT)

        elif prueba == 2:
            with open(f"resultados/resultados_Tr_costo_almacenar_{str(mult_costo_alm[p])}.csv", "w") as file:
                file.write("Tr,a,i,j,k,t,e")
                file.write(sol_Tr)

            with open(f"resultados/resultados_Cam_costo_almacenar_{str(mult_costo_alm[p])}.csv", "w") as file:
                file.write("Cam,e,i,j,k,t")
                file.write(sol_Cam)

            with open(f"resultados/resultados_Al_costo_almacenar_{str(mult_costo_alm[p])}.csv", "w") as file:
                file.write("Al,a,i,k,t")
                file.write(sol_Al)

            with open(f"resultados/resultados_ExT_costo_almacenar_{str(mult_costo_alm[p])}.csv", "w") as file:
                file.write("ExT,a,i,k,t")
                file.write(sol_ExT)            

with open(f"resultados/valores_objetivo.csv", "w") as file:
    for i in range(3):
        file.write(f"Prueba {i}")
        for j in range(3):
            file.write(str(valores_objetivo[i,j]))

print("Valores objetivo para prueba 0: ", valores_objetivo[0,:])
print("Valores objetivo para prueba 1: ", valores_objetivo[1,:])
print("Valores objetivo para prueba 2: ", valores_objetivo[2,:])

