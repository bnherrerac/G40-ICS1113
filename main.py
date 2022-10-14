# from gurobipy import GRB, Model
import pandas as pd # Si sale error, escribir en cmd pip install pandas
import csv
import numpy as np # Si sale error, escribir en cmd pip install numpy
import sys

sys.path.append("./archivos")

from carga_datos import *

# model = Model()
# model.setParam("TimeLimit", 3000)

paises = ["Chile", "Argentina"]
tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
regiones = ["Norte", "Centro", "Sur"]

### Los datos aquí abajo están inventados
alimentos = np.arange(3)
cantidad_de_alimentos = np.array([5,4,7])
centros_de_distribucion = np.array([3,2,5])
bodegas = np.array([2,4,6])

flota_de_camiones = np.array([15,7,12])
vol_carga = np.array([90,85,85]) 
# Camiones terrestres (pequeños): 90 m3, 12000 kg https://www.avantiatransportes.com/capacidad-de-carga-transporte-terrestre/ 
# Camiones trailer box (más grandes): 90 m3, 31400 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/camion-trailer-box-o-camion-furgon
# Camiones frigoríficos: 85 m3, 31000 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/trailer-frigorifico-o-camion-frigo
# Camiones para congelados: 85 m3, 31000 kg (mismo que arriba) http://www.frigocargo.cl/#project
# Se utiliza en algunos camiones este equipo de enfriamiento https://tkadvancer.thermokinginfo.com/upload/whisper-pro/publication/TK80063_Whisper_Pro_Brochure_05-2021_ES_V2.0_spread.pdf
peso_carga = np.array([31000,31000,31000])









# for i in range(3):
#     print(f"Tipo {tipos[i]} tiene {cantidad_de_alimentos[i]} subalimentos")




T = range(1, 52 + 1) #tiempo



# x = m.addVar(vtype=GRB.CONTINUOUS, name="x")
# y = m.addVar(vtype=GRB.CONTINUOUS, name="y")
# z = m.addVar(vtype=GRB.CONTINUOUS, name="z")

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
