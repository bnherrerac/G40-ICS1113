from gurobipy import GRB, Model, quicksum
from gurobipy import *
import pandas as pd # Si sale error, escribir en cmd pip install pandas
import csv
import numpy as np # Si sale error, escribir en cmd pip install numpy
from archivos.carga_datos import *

model = Model()
model.setParam("TimeLimit", 3000)

paises = ["Chile", "Argentina"]
tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
regiones = ["Norte", "Centro", "Sur"]

### Los datos aquí abajo están inventados

flota_de_camiones = np.array([15,7,12])
vol_carga = np.array([90,85,85]) 
# Camiones terrestres (pequeños): 90 m3, 12000 kg https://www.avantiatransportes.com/capacidad-de-carga-transporte-terrestre/ 
# Camiones trailer box (más grandes): 90 m3, 31400 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/camion-trailer-box-o-camion-furgon
# Camiones frigoríficos: 85 m3, 31000 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/trailer-frigorifico-o-camion-frigo
# Camiones para congelados: 85 m3, 31000 kg (mismo que arriba) http://www.frigocargo.cl/#project
# Se utiliza en algunos camiones este equipo de enfriamiento https://tkadvancer.thermokinginfo.com/upload/whisper-pro/publication/TK80063_Whisper_Pro_Brochure_05-2021_ES_V2.0_spread.pdf

peso_carga = np.array([31000,31000,31000])

# Importación de datos de csv
alimentos, cant_por_tipo, total_alimentos = alimentos(tipos)
costo_adicional_camiones = costo_adicional_camiones()
costo_combustible = costo_combustible()
costo_fijo_almacenamiento = costo_fijo_almacenamiento()
costo_mantencion = costo_mantencion()
costo_ruta = costo_ruta()
costo_unitario_almacenamiento = costo_unitario_almacenamiento()
costo_vencimiento = costo_vencimiento()
demanda = demanda()
distancia_por_pais = distancia_por_pais()
peso_promedio = peso_promedio()
stock_inicial = stock_inicial()
sueldo = sueldo()
volumen_alimentos = volumen_alimentos()
vencimiento = vencimiento()

cant_de_centros = 8
cant_de_bodegas = 9

T = range(1, 52 + 1)    #tiempo
tau = range(1, 52 + 1)  #tiempo de llegada
I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento


#Variables
Tr = model.addVars(A, J, K, T, vtype=GRB.CONTINUOUS, name="Tr")
Cam = model.addVars(I, J, K, T, vtype=GRB.CONTINUOUS, name="Cam")
Al = model.addVars(A, K, T, tau, vtype=GRB.CONTINUOUS, name="Al")
ExT = model.addVars(tau, A, K, T, vtype=GRB.CONTINUOUS, name="ExT")


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
