from gurobipy import GRB, Model, quicksum
from gurobipy import *
import pandas as pd # Si sale error, escribir en cmd pip install pandas
import numpy as np # Si sale error, escribir en cmd pip install numpy
from archivos.carga_datos import *

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
costo_vencimiento = costo_vencimiento(tipos)
demanda = demanda(tipos)
distancia_por_pais = distancia_por_pais(rutas)
peso_promedio = peso_promedio(tipos)
stock_inicial = stock_inicial(tipos)
sueldo = sueldo()
vencimiento = vencimiento(tipos)

#------------------------------- Rangos -------------------------------#
cant_de_centros = 20
cant_de_bodegas = 8

T = range(1, 52 + 1)    #tiempo
Tau = range(1, 52 + 1)  #tiempo de llegada
I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento
R = range(1, len(rutas) + 1) # 1:Norte, 2:Centro, 3:Sur
P = range(1, len(paises) + 1) # 1:Chile, 2:Argentina

#------------------------- Parámetros -------------------------#
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

flota_de_camiones = np.array([30,30,30])
N_i = {(i): flota_de_camiones[j] for (i,j) in zip(I,range(len(I)))}
R_i = {"1": "Norte", "2": "Centro", "3": "Sur"}

V_m = 90 # 90 m3 es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
P_m = 31000 # 31000 kg es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 


CFB_i = {(i): int(costo_fijo_almacenamiento[dict_tipos[i]]) for i in I}
CTr_i = {(i): int(costo_adicional_camiones[dict_tipos[i]]) for i in I}
CAl_i = {(i): float(costo_unitario_almacenamiento[dict_tipos[i]]) for i in I}
q_ai = {(a,i): int(stock_inicial[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
d_ai = {(a,i): int(demanda[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
P_ai = {(a,i): float(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
H_ai = {(a,i): float(costo_vencimiento[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
l_rp = {(r,p): int(distancia_por_pais[dict_rutas[r]][dict_paises[p]]) for r in R for p in P}
PC_p = {(p): int(costo_combustible[dict_paises[p]]) for p in P}
PT_r = {(r): int(costo_ruta[dict_rutas[r]]) for r in R}
S_r = {(r): int(sueldo[dict_rutas[r]]) for r in R}
M_r = {(r): int(costo_mantencion[dict_rutas[r]]) for r in R}
v_ai = {(a,i): int(vencimiento[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
v_taitau = {}
for t in T:
    for tau in Tau:
        for a in A:
            for i in I:
                if t-tau>= v_ai[(a,i)]:
                    v_taitau[(tau,t,a,i)] = 0
                else:
                    v_taitau[(tau,t,a,i)] = 1


### Fuentes de los datos
# Camiones terrestres (pequeños): 90 m3, 12000 kg https://www.avantiatransportes.com/capacidad-de-carga-transporte-terrestre/ 
# Camiones trailer box (más grandes): 90 m3, 31400 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/camion-trailer-box-o-camion-furgon
# Camiones frigoríficos: 85 m3, 31000 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/trailer-frigorifico-o-camion-frigo
# Camiones para congelados: 85 m3, 31000 kg (mismo que arriba) http://www.frigocargo.cl/#project
# Se utiliza en algunos camiones este equipo de enfriamiento https://tkadvancer.thermokinginfo.com/upload/whisper-pro/publication/TK80063_Whisper_Pro_Brochure_05-2021_ES_V2.0_spread.pdf

#------------------------- Variables -------------------------#
Tr = model.addVars(A, I, J, K, T, vtype=GRB.CONTINUOUS, name="Tr")
Cam = model.addVars(I, J, K, T, vtype=GRB.CONTINUOUS, name="Cam")
Al = model.addVars(Tau, A, I, K, T, vtype=GRB.CONTINUOUS, name="Al")
ExT = model.addVars(T, A, I, K, Tau, vtype=GRB.CONTINUOUS, name="ExT")

#------------------------- Restricciones -------------------------#
print("Agregando restricciones")
model.addConstrs((Cam[i,j,k,t] <= N_i[i] for i in I for j in J for k in K for t in T), name="R2")
model.addConstrs((Tr[a,i,j,k,t]*P_ai[(a,i)] <= P_m for a in A for i in I for j in J for k in K for t in T), name="R3.1")
cont = 0
for t in T:
    print(f"Agregando restricciones acumulativas para t = {t}")
    name_5 = "R5_" + str(cont)
    model.addConstrs((Al[tau,a,i,k,t] >= d_ai[a,i] for a in A for i in I for k in K for tau in list(np.array(Tau)[np.array(Tau)<t])), name=name_5)
    name_6 = "R6_" + str(cont)
    model.addConstrs((quicksum(quicksum(ExT[t,a,i,k,tau] for tau in list(np.array(Tau)[np.array(Tau)<t])) for k in K) <= d_ai[a,i] for a in A for i in I), name=name_6)
    name_7 = "R7_" + str(cont)
    model.addConstrs((ExT[t,a,i,k,tau] <= Al[tau,a,i,k,t] for a in A for i in I for k in K for tau in list(np.array(Tau)[np.array(Tau)<t])), name=name_7)
    name_10 = "R10_" + str(cont)
    model.addConstrs((quicksum(Al[tau,a,i,k,1] for tau in list(np.array(Tau)[np.array(Tau)<t]))== q_ai[a,i]-d_ai[a,i] for i in I for a in A for k in K for j in J), name=name_10)
    name_11 = "R11_" + str(cont) 
    if t>=2:
        model.addConstrs((quicksum(Al[tau,a,i,k,t] for tau in list(np.array(Tau)[np.array(Tau)<t])) == (quicksum(Al[tau,a,i,k,t] for tau in (list(np.array(Tau)[np.array(Tau)<t-1]))) - Tr[a,i,j,k,t-1]-d_ai[a,i]) for i in I for a in A for k in K for j in J), name=name_11)
    cont += 1

model.addConstrs((Al[tau,a,i,k,t] >= ExT[t,a,i,k,tau] for a in A for i in I for k in K for t in T), name="R8") 

#------------------------- Función objetivo -------------------------#

obj = quicksum( 
        quicksum(
            quicksum(
                quicksum((PT_r[i]+S_r[i]+quicksum(l_rp[(i,p)]*PC_p[p] for p in P) + M_r[i] + CTr_i[i])*Cam[i,j,k,t] 
                for k in K)
            for j in J)
        for i in I)
    for t in T)

obj +=  quicksum(
            quicksum(
                CFB_i[i] + quicksum(quicksum(CAl_i[i]*P_ai[(a,i)]*(quicksum(Al[tau,a,i,k,t]-d_ai[(a,i)] for tau in list(np.array(Tau)[np.array(Tau)<t]))) for k in K) for a in A)
            for k in K)
        for j in J)

obj += quicksum( 
        quicksum(
            quicksum(
                quicksum(
                    H_ai[(a,i)]*quicksum((1-v_taitau[(tau,t,a,i)])*Al[tau,a,i,k,t] for tau in list(np.array(Tau)[np.array(Tau)<t]))
                for k in K)
            for j in J)
        for i in I)
    for t in T)

#------------------------- Minimización de costos -------------------------#

model.setObjective(obj, GRB.MINIMIZE)
model.optimize()
model.computeIIS()
# valor_objetivo = model.ObjNVal
# print(f"El costo minimizado es de {valor_objetivo} CLP durante todo el año.")

#------------------------- Escritura de datos en resultados -------------------------#

# sol_Tr = ""
# sol_Cam = ""
# sol_Al = ""
# sol_ExT = ""

# for t in T:
#     for i in I:
#         for a in A:
#             for j in J:
#                 for k in K:
#                     sol_Tr += f" \n{int(Tr[a,i,j,k,t].x)},{a},{i},{j},{k},{t}"
#             for k in K:
#                 for tau in Tau:
#                     sol_Al += f" \n{int(Al[tau,a,i,k,t].x)},{tau},{a},{i},{k},{t}"
#         for k in K:
#             for j in J:
#                 sol_Cam += f" \n{int(Cam[i,j,k,t].x)},{i},{j},{k},{t}"    
#             for  t in T:
#                 for tau in Tau:
#                     sol_ExT += f" \n{int(ExT[tau,t,a,i,k].x)},{tau},{t},{a},{i},{k}"

# with open("resultados/resultados_Tr.csv", "w") as file:
#     file.write("Tr,a,i,j,k,t")
#     file.write("sol_Tr")

# with open("resultados/resultados_Cam.csv", "w") as file:
#     file.write("Cam,i,j,k,t")
#     file.write("sol_Cam")

# with open("resultados/resultados_Al.csv", "w") as file:
#     file.write("Al,tau,a,i,k,t")
#     file.write("sol_Al")

# with open("resultados/resultados_ExT.csv", "w") as file:
#     file.write("ExT,tau,t,a,i,k")
#     file.write("sol_ExT")


# Guardado de resultados