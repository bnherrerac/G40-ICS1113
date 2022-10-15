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
# costo_combustible = costo_combustible()
costo_fijo_almacenamiento = costo_fijo_almacenamiento()
costo_mantencion = costo_mantencion()
costo_ruta = costo_ruta()
costo_unitario_almacenamiento = costo_unitario_almacenamiento()
costo_vencimiento = costo_vencimiento(tipos)
demanda = demanda(tipos)
distancia_por_pais = distancia_por_pais()
# peso_promedio = peso_promedio(tipos)
stock_inicial = stock_inicial(tipos)
sueldo = sueldo()
volumen_promedio = volumen_promedio(tipos)
vencimiento = vencimiento()
volumen_bodegas = volumen_bodegas()

#------------------------------- Rangos -------------------------------#
cant_de_centros = 8
cant_de_bodegas = 9

T = range(1, 52 + 1)    #tiempo
tau = range(1, 52 + 1)  #tiempo de llegada
I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento


#------------------------- Parámetros -------------------------#
# IMPORTANTE: el conjunto I está indexado como 1:Hortofrutícola 2:Congelado 3:Refrigerado
dict_tipos = dict(zip(I, tipos))
# dict_tipos =  {1: 'Hortofruticola', 2: 'Congelado', 3: 'Refrigerado'}

dict_alimentos = {}
for i in I:
    dict_alimentos[i] = dict(zip(A,alimentos[dict_tipos[i]]))
print("dict_alimentos = ", dict_alimentos)

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


CFB_i = {(i): costo_fijo_almacenamiento[dict_tipos[i]] for i in I}
# print(CFB_i)
VB_i = {(i): volumen_bodegas[dict_tipos[i]] for i in I}
# print(VB_i)
CTr_i = {(i): costo_adicional_camiones[dict_tipos[i]] for i in I}
# print(CTr_i)
CAl_i = {(i): costo_unitario_almacenamiento[dict_tipos[i]] for i in I}
# print(CAl_i)
q_ai = {(a,i): stock_inicial[dict_tipos[i]][dict_alimentos[i][a]] for i in I for a in A}
# print(q_ai)
# d_ai = {(a,i): demanda[dict_tipos[i]][dict_alimentos[i][a]] for i in I for a in A}
# print(d_ai)

P_ai = {(a,i): peso_promedio[dict_tipos[i]][dict_alimentos[i][a]] for i in I for a in A}
V_ai = {(a,i): volumen_promedio[dict_tipos[i]][dict_alimentos[i][a]] for i in I for a in A}
H_ai = {(a,i): costo_vencimiento[dict_tipos[i]][dict_alimentos[i][a]] for i in I for a in A}
d_rp = {}
### Los datos aquí abajo están inventados


vol_carga = np.array([90,85,85]) 
# Camiones terrestres (pequeños): 90 m3, 12000 kg https://www.avantiatransportes.com/capacidad-de-carga-transporte-terrestre/ 
# Camiones trailer box (más grandes): 90 m3, 31400 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/camion-trailer-box-o-camion-furgon
# Camiones frigoríficos: 85 m3, 31000 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/trailer-frigorifico-o-camion-frigo
# Camiones para congelados: 85 m3, 31000 kg (mismo que arriba) http://www.frigocargo.cl/#project
# Se utiliza en algunos camiones este equipo de enfriamiento https://tkadvancer.thermokinginfo.com/upload/whisper-pro/publication/TK80063_Whisper_Pro_Brochure_05-2021_ES_V2.0_spread.pdf

peso_carga = np.array([31000,31000,31000])


#Variables
Tr = model.addVars(A, I, J, K, T, vtype=GRB.CONTINUOUS, name="Tr")
Cam = model.addVars(I, J, K, T, vtype=GRB.CONTINUOUS, name="Cam")
Al = model.addVars(A, I, K, T, tau, vtype=GRB.CONTINUOUS, name="Al")
ExT = model.addVars(T, A, I, K, tau, vtype=GRB.CONTINUOUS, name="ExT")


# m.update()

# m.setObjective(x + z, GRB.MAXIMIZE)

# m.addConstr(x + y + z <= 5, name="R1")
# m.addConstr(x - z >= -3, name="R2")
# m.addConstr(x - y - z <= 1, name="R3")
# m.addConstr(x >= 0, name="R4")
# m.addConstr(y >= 0, name="R5")
# m.addConstr(z >= 0, name="R6")

# m.optimize()

# m.printAttr("X")
