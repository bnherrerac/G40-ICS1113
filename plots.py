import matplotlib.pyplot as plt 
from archivos.carga_datos import *
from gurobipy import GRB, Model, quicksum
from gurobipy import *
import numpy as np

alimentos, cant_por_tipo, total_alimentos = alimentos(tipos)

cant_de_centros = 1
cant_de_bodegas = 1
cant_de_camiones = 9

tmax = 10

T = range(1, tmax + 1)    #tiempo

I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento
R = range(1, len(rutas) + 1) # 1:Norte, 2:Centro, 3:Sur
P = range(1, len(paises) + 1) # 1:Chile, 2:Argentina
E = range(1, cant_de_camiones + 1)

# Al[a,i,k,t] ExT[a,i,k,t] Tr[a,i,j,k,t,e] Cam[e,a,i,j,k,t]

Tr = np.zeros((cant_por_tipo[0],len(cant_por_tipo),cant_de_centros,cant_de_bodegas,tmax,cant_de_camiones))
Al = np.zeros((cant_por_tipo[0], len(cant_por_tipo),cant_de_bodegas,tmax))
ExT = np.zeros((cant_por_tipo[0], len(cant_por_tipo),cant_de_bodegas,tmax))
# Cam = np.zeros((cant_de_camiones,cant_por_tipo[0],len(cant_por_tipo),cant_de_centros,cant_de_bodegas,tmax))
Cam = np.zeros((cant_de_camiones,len(cant_por_tipo),cant_de_centros,cant_de_bodegas,tmax))

with open("resultados/resultados_Tr_sv_camch.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # Tr,a,i,j,k,t,e
        data = [int(datum) for datum in data]
        Tr[data[1]-1,data[2]-1,data[3]-1,data[4]-1,data[5]-1,data[6]-1] = data[0]


with open("resultados/resultados_Cam_sv_camch.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # Cam,e,a,i,j,k,t
        data = [int(datum) for datum in data]
        # Cam[data[1]-1,data[2]-1,data[3]-1,data[4]-1,data[5]-1,data[6]-1] = data[0]
        Cam[data[1]-1,data[2]-1,data[3]-1,data[4]-1,data[5]-1] = data[0]

with open("resultados/resultados_Al_sv_camch.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # Al[a,i,k,t]
        data = [int(datum) for datum in data]
        Al[data[1]-1,data[2]-1,data[3]-1,data[4]-1] = data[0]

with open("resultados/resultados_ExT_sv_camch.csv", "r") as file:
    datos = file.readlines()
    file.close()
    datos.pop(0)
    for linea in datos:
        data = linea.strip(" \n").split(",") # ExT[a,i,k,t]
        data = [int(datum) for datum in data]
        ExT[data[1]-1,data[2]-1,data[3]-1,data[4]-1] = data[0]

Al_sample = np.sum(Al, axis=(0,1))
ExT_sample = np.sum(ExT, axis=0)
Cam_sum_over_time = np.sum(Cam, axis=(0,1))
print("np shape Al_sample = ", np.shape(Al_sample))


fig, ax = plt.subplots()
input = Cam_sum_over_time
print(np.shape(input)[0])
for ydim in range(np.shape(input)[0]):
    ax.scatter(T, input[ydim,:,:], label=ydim) # Cambiar slicing para graficar}
# for y in range(np.shape(ExT_sample)[0]):
#     ax.scatter(T, ExT_sample[y,:], label="ExT") 

ax.legend()
ax.grid(True)
fig.suptitle("Título")
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
ax.ticklabel_format(useOffset=False)
plt.show()

# printear (quicksum(Al[a,i,k,t]*P_ai[(a,i)] for a in A for i in I) for k for t

tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
dict_tipos = dict(zip(I, tipos))
dict_alimentos = {}
for i in I:
    dict_alimentos[i] = dict(zip(A,alimentos[dict_tipos[i]]))
peso_promedio = peso_promedio(tipos)
P_ai = {(a,i): float(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}

# print(Tr)

# for k in K:
#     for t in T:
#         current_sum = 0
#         for a in A:
#             for i in I:
#                 current_sum += Al[a-1,i-1,k-1,t-1]*P_ai[(a,i)]
#         print(f"Peso para k = {k} y t = {t} =", current_sum)

P_m = 31000
T = range(1,11)

pesos_cam_tiempo = np.zeros((len(E),len(T)))
for e in E:
    print(f"\nCamión {e}")
    for t in T:
        # print(f"Tiempo {t}")
        current_peso = 0
        for j in J:
            for k in K:
                for i in I:
                    print(f"Tr[:,{i},{j},{k},{t},{e}] = {Tr[:,i-1,j-1,k-1,t-1,e-1]}")
                    if Tr[:,i-1,j-1,k-1,t-1,e-1].any() != 0:
                        print(f"El camión {e} lleva productos de tipo {dict_tipos[i]} en el tiempo t = {t}")
                        for a in A:
                            print(f"Se transportaron {Tr[a-1,i-1,j-1,k-1,t-1,e-1]} unidades de {dict_alimentos[i][a]}.")
                            current_peso += Tr[a-1,i-1,j-1,k-1,t-1,e-1]*P_ai[(a,i)]     
        if current_peso != 0:
            print(f"Peso total para camión e = {e} en tiempo t = {t}")
            print(current_peso)
        pesos_cam_tiempo[e-1,t-1] = current_peso

print(pesos_cam_tiempo)

fig, ax = plt.subplots()
input = pesos_cam_tiempo
print(np.shape(input)[0])
for ydim in range(np.shape(input)[0]):
    ax.scatter(T, input[ydim,:], label=f"Camión {ydim+1}") # Cambiar slicing para graficar}

ax.legend()
ax.grid(True)
fig.suptitle("Peso total por camión por semana")
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
ax.ticklabel_format(useOffset=False)
plt.show()

camiones_array = np.sum(Tr, axis=(0,1,2,3))

fig, ax = plt.subplots()
for camion in E:
    ax.plot(T, camiones_array[:,camion-1], label=f"Sum_(a,i,j) Tr[a,i,j,k,t,{camion}]")
ax.legend()
ax.grid(True)
fig.suptitle("Cantidad de alimentos transportada por cada camión.")
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
ax.ticklabel_format(useOffset=False)
plt.show()