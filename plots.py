import matplotlib.pyplot as plt 
from archivos.carga_datos import *
from gurobipy import GRB, Model, quicksum
from gurobipy import *
import numpy as np

cant_de_centros = 1
cant_de_bodegas = 1
cant_de_camiones = 10

alimentos, cant_por_tipo, total_alimentos = alimentos(tipos)

T = range(1, 14 + 1)    #tiempo

I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento
R = range(1, len(rutas) + 1) # 1:Norte, 2:Centro, 3:Sur
P = range(1, len(paises) + 1) # 1:Chile, 2:Argentina
E = range(1, cant_de_camiones + 1)

# Al[a,i,k,t] ExT[a,i,k,t] Tr[a,i,j,k,t,e] Cam[e,a,i,j,k,t]

Tr = np.zeros((cant_por_tipo[0],len(cant_por_tipo),cant_de_centros,cant_de_bodegas,14,cant_de_camiones))
Al = np.zeros((cant_por_tipo[0], len(cant_por_tipo),cant_de_bodegas,14))
ExT = np.zeros((cant_por_tipo[0], len(cant_por_tipo),cant_de_bodegas,14))
Cam = np.zeros((cant_de_camiones,cant_por_tipo[0],len(cant_por_tipo),cant_de_centros,cant_de_bodegas,14))

with open("resultados/resultados_Tr_sv.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # Tr,a,i,j,k,t,e
        data = [int(datum) for datum in data]
        Tr[data[1]-1,data[2]-1,data[3]-1,data[4]-1,data[5]-1,data[6]-1] = data[0]


with open("resultados/resultados_Cam_sv.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # Cam,e,a,i,j,k,t
        data = [int(datum) for datum in data]
        Cam[data[1]-1,data[2]-1,data[3]-1,data[4]-1,data[5]-1,data[6]-1] = data[0]

with open("resultados/resultados_Al_sv.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # Al[a,i,k,t]
        data = [int(datum) for datum in data]
        Al[data[1]-1,data[2]-1,data[3]-1,data[4]-1] = data[0]

with open("resultados/resultados_ExT_sv.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # ExT[a,i,k,t]
        data = [int(datum) for datum in data]
        ExT[data[1]-1,data[2]-1,data[3]-1,data[4]-1] = data[0]

Al_sample = np.sum(Al, axis=(0,1))
Cam_sum_over_time = np.sum(Cam, axis=(0,1))
print("np shape Al_sample = ", np.shape(Al_sample))


fig, ax = plt.subplots()
input = Cam_sum_over_time
print(np.shape(input)[0])
for ydim in range(np.shape(input)[0]):
    ax.scatter(T, input[ydim,:,:], label=ydim) # Cambiar slicing para graficar

ax.legend()
ax.grid(True)
fig.suptitle("Título")
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
ax.ticklabel_format(useOffset=False)
plt.show()