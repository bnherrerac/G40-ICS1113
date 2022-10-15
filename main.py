from gurobipy import GRB, Model, quicksum
from gurobipy import *
import pandas as pd # Si sale error, escribir en cmd pip install pandas
import csv
import numpy as np # Si sale error, escribir en cmd pip install numpy
from archivos.carga_datos import *

model = Model()
model.setParam("TimeLimit", 3000)

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
volumen_promedio = volumen_promedio(tipos)
vencimiento = vencimiento(tipos)
volumen_bodegas = volumen_bodegas()

#------------------------------- Rangos -------------------------------#
cant_de_centros = 8
cant_de_bodegas = 9

T = range(1, 52 + 1)    #tiempo
Tau = range(1, 52 + 1)  #tiempo de llegada
I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento
R = range(1, len(rutas) + 1) # 1:Norte, 2:Centro, 3:Sur
P = range(1, len(paises) + 1) # 1:Chile, 2:Argentina

#------------------------- Parámetros -------------------------#
# IMPORTANTE: el conjunto I está indexado como 1:Hortofrutícola 2:Congelado 3:Refrigerado
dict_tipos = dict(zip(I, tipos))
# dict_tipos =  {1: 'Hortofruticola', 2: 'Congelado', 3: 'Refrigerado'}

dict_alimentos = {}
for i in I:
    dict_alimentos[i] = dict(zip(A,alimentos[dict_tipos[i]]))
# print("dict_alimentos = ", dict_alimentos)

dict_rutas = {1:"Norte", 2:"Centro", 3:"Sur"}
dict_paises = {1:"Chile", 2:"Argentina"}

# dict_alimentos = {
# 1: {1: 'Manzana', 2: 'Pera', 3: 'Naranja'}, 
# 2: {1: 'Pollo', 2: 'Camaron', 3: 'Hamburguesa'}, 
# 3: {1: 'Queso', 2: 'Yogur', 3: 'Jamon'}
# }

flota_de_camiones = np.array([15,7,12])
N_i = {(i): flota_de_camiones[j] for (i,j) in zip(I,range(len(I)))}
# print(N_i)

R_i = {"1": "Norte", "2": "Centro", "3": "Sur"}

V_m = 90 # 90 m3 es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
P_m = 31000 # 31000 kg es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 


CFB_i = {(i): int(costo_fijo_almacenamiento[dict_tipos[i]]) for i in I}
# print(CFB_i)
VB_i = {(i): int(volumen_bodegas[dict_tipos[i]]) for i in I}
# print(VB_i)
CTr_i = {(i): int(costo_adicional_camiones[dict_tipos[i]]) for i in I}
# print(CTr_i)
CAl_i = {(i): int(costo_unitario_almacenamiento[dict_tipos[i]]) for i in I}
# print(CAl_i)
q_ai = {(a,i): int(stock_inicial[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
# print(q_ai)
d_ai = {(a,i): int(demanda[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
# print(d_ai)

P_ai = {(a,i): int(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
V_ai = {(a,i): int(volumen_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
H_ai = {(a,i): int(costo_vencimiento[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
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

model.addConstr((Cam[i,j,k,t] <= N_i for i in I for j in J for k in K for t in T), name="R2")
model.addConstr((Tr[a,i,j,k,t] <= P_m for a in A for i in I for j in J for k in K for t in T), name="R3.1")
model.addConstr((Tr[a,i,j,k,t] <= V_m for a in A for i in I for j in J for k in K for t in T), name="R3.2")
model.addConstr((quicksum(Al[tau,a,i,k,t] for tau in list(np.array(Tau)[np.array(Tau)<t])) <= VB_i for a in A for i in I for k in K for tau in list(np.array(Tau)[np.array(Tau)<t]) for t in T), name="R4")
model.addConstr((Al[tau,a,i,k,t] >= d_ai[a,i] for a in A for i in I for k in K for tau in list(np.array(Tau)[np.array(Tau)<t])), name="R5")
model.addConstr((quicksum(quicksum(ExT[tau,t,a,i,k] for tau in list(np.array(Tau)[np.array(Tau)<t])) for k in K) <= d_ai[a,i] for a in A for i in I for t in T), name="R6")
model.addConstr((ExT[tau,t,a,i,k] <= Al[tau,a,i,k,t] for a in A for i in I for k in K for tau in list(np.array(Tau)[np.array(Tau)<t])), name="R7")
model.addConstr((Al[tau,a,i,k,t] > ExT[tau,t,a,i,k] for a in A for i in I for k in K for t in T), name="R8") 
model.addConstr((Cam[i,j,k,t] >= quicksum(((Tr[a,i,j,k,t]*V_ai)/V_m) for a in A) for i in I for t in T for j in J for k in K), name="R9")
model.addConstr((quicksum(Al[tau,a,i,k,1] for tau in list(np.array(Tau)[np.array(Tau)<t]))== q_ai[a,i]-d_ai[1,a,i] for i in I for a in A for k in K for j in J), name="R10")
#model.addConstr((quicksum(Al[tau,a,i,k,t] for tau in list(np.array(Tau)[np.array(Tau)<t])) == (quicksum(Al[tau,a,i,k,t] for tau in (list(np.array(Tau)[np.array(Tau)<t])-1)) - Tr[a,i,j,k,t-1]-d_ai[t,a,i]) for i in I for a in A for k in K for t in range(2,53) for j in J), name="R11")
#a la R11 le falta poner que la suma vaya desde tau=o a tau= tau-1
#------------------------- Función objetivo -------------------------#

obj = quicksum( 
        quicksum(
            quicksum(
                quicksum((PT_r[i]+S_r[i]+quicksum(l_rp[(i,p)*PC_p[p]] for p in P) + M_r[i] + CTr_i[i])*Cam[i,j,k,t] 
                for k in K)
            for j in J)
        for i in I)
    for t in T)

obj +=  quicksum(
            quicksum(
                CFB_i[i] + quicksum(quicksum(CAl_i[i]*V_ai[(a,i)]*(quicksum(Al[tau,a,i,k,t]-d_ai[(a,i)] for tau in list(np.array(Tau)[np.array(Tau)<t]))) for k in K) for a in A)
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

model.setObjective(obj)
model.optimize()
valor_objetivo = model.ObjVal

# Guardado de resultados