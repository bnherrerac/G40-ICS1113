from gurobipy import GRB, Model, quicksum
from gurobipy import *
import pandas as pd # Si sale error, escribir en cmd pip install pandas
import numpy as np # Si sale error, escribir en cmd pip install numpy
from archivos.carga_datos import *
import matplotlib.pyplot as plt

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
# costo_vencimiento = costo_vencimiento(tipos)
demanda = demanda(tipos)
distancia_por_pais = distancia_por_pais(rutas)
peso_promedio = peso_promedio(tipos)
stock_inicial = stock_inicial(tipos)
sueldo = sueldo()
# vencimiento = vencimiento(tipos)

#------------------------------- Rangos -------------------------------#
# cant_de_centros = 20
# cant_de_bodegas = 8
# cant_de_camiones = 30 # Cantidad total de camiones por categoría de alimento, sumado sobre todos los centros de distribución

cant_de_centros = 1
cant_de_bodegas = 4
cant_de_camiones = 35


# T = range(1, 52 + 1)    #tiempo
# Tau = range(1, 52 + 1)  #tiempo de llegada

T = range(1, 5 + 1)    #tiempo

I = range(1, len(cant_por_tipo) + 1) # Tipos de alimentos 1: Hortofrutícola 2:Congelado 3:Refrigerado
A = range(1, cant_por_tipo[0] + 1) # Alimentos de cada tipo
J = range(1, cant_de_centros + 1) # Cantidad de centros de distribución
K = range(1, cant_de_bodegas + 1) # Cantidad de bodegas de almacenamiento
R = range(1, len(rutas) + 1) # 1:Norte, 2:Centro, 3:Sur
P = range(1, len(paises) + 1) # 1:Chile, 2:Argentina
E = range(1, cant_de_camiones + 1)

#------------------------- Parámetros -------------------------#
print("Definiendo parámetros")
dict_rutas = {1:"Norte", 2:"Centro", 3:"Sur"}
dict_paises = {1:"Chile", 2:"Argentina"}

dict_tipos = dict(zip(I, tipos))
dict_alimentos = {}
for i in I:
    dict_alimentos[i] = dict(zip(A,alimentos[dict_tipos[i]]))

# Carga, transporte y almacenamiento
flota_de_camiones = np.array([cant_de_camiones,cant_de_camiones,cant_de_camiones])
N_i = {(i): flota_de_camiones[j] for (i,j) in zip(I,range(len(I)))}
R_i = {"1": "Norte", "2": "Centro", "3": "Sur"}
P_m = 31000 # 31000 kg es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
CFB_i = {(i): int(costo_fijo_almacenamiento[dict_tipos[i]]) for i in I}
CTr_i = {(i): int(costo_adicional_camiones[dict_tipos[i]]) for i in I}
CAl_i = {(i): float(costo_unitario_almacenamiento[dict_tipos[i]]) for i in I} # Arreglar este valor
q_ai = {(a,i): int(stock_inicial[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
Omega = 1000000

# Propiedades de los alimentos
d_ai = {(a,i): int(demanda[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
P_ai = {(a,i): float(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}


peso_en_demanda = {(a,i): d_ai[(a,i)]*P_ai[(a,i)] for i in I for a in A}
print(peso_en_demanda)
print("Max peso en demanda: ", max(peso_en_demanda))
print("Alimento para el que es máximo: ", peso_en_demanda[max(peso_en_demanda, key=peso_en_demanda.get)])

# Ruta
l_rp = {(r,p): int(distancia_por_pais[dict_rutas[r]][dict_paises[p]]) for r in R for p in P}
PC_p = {(p): int(costo_combustible[dict_paises[p]]) for p in P}
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
# Cam e, j, k, t, i
Cam = model.addVars(E, A, I, J, K, T, vtype=GRB.BINARY, name="Cam")
Tr = model.addVars(A, I, J, K, T, E, vtype=GRB.CONTINUOUS, name="Tr")
Al = model.addVars(A, I, K, T, vtype=GRB.CONTINUOUS, name="Al")
ExT = model.addVars(A, I, K, T, vtype=GRB.CONTINUOUS, name="ExT")
print("Variables definidas")
#------------------------- Restricciones -------------------------#
print("Agregando restricciones")

# Restricción 1
# sum_A sum_K sum_J sum_I Cam[e,a,i,j,k,t] \leq 1   \forall t in T, e in E
model.addConstrs((quicksum(Cam[e,a,i,j,k,t] for j in J for k in K for a in A for i in I) <= 1  for t in T for e in E), name="R1")

# Restricción 2
model.addConstrs((Cam[e,a,i,j,k,t] <= Tr[a,i,j,k,t,e] for i in I for j in J for t in T for k in K for a in A for e in E), name="R2")

# Restricción 3
model.addConstrs((quicksum(Tr[a,i,j,k,t,e]*P_ai[(a,i)] for a in A for i in I) <= P_m for j in J for k in K for t in T for e in E), name="R3")

# Restricción 4
model.addConstrs((quicksum(Al[a,i,k,t]*P_ai[(a,i)] for a in A for i in I) <= quicksum(2*d_ai[(a,i)]*(1/cant_de_bodegas)*P_ai[(a,i)] for a in A for i in I) for k in K for t in T), name="R4")

# Restricción 5
model.addConstrs((Tr[a,i,j,k,t,e]*(1/Omega) <= Cam[e,a,i,j,k,t] for i in I for e in E for t in T for j in J for k in K for a in A), name="R5")

# Restricción 6
model.addConstrs((Al[a,i,k,1] == quicksum(Tr[a,i,j,k,1,e] for j in J for e in E) - ExT[a,i,k,1] for i in I for a in A for k in K), name="R6")

# Restricción 7, inventario del almacén
for t in T:
    if t > 1:
        print(f"t={t}")
        model.addConstrs((quicksum(Tr[a,i,j,k,t,e] for j in J for e in E) + Al[a,i,k,t-1] - ExT[a,i,k,t] == Al[a,i,k,t] for a in A for k in K for i in I), name="R7")

# Restricción 8
model.addConstrs((quicksum(ExT[a,i,k,t] for k in K) >= d_ai[(a,i)] for a in A for i in I for t in T), name="R8")

#------------------------- Función objetivo -------------------------#

obj = quicksum((PT_r[i]+S_r[i]+quicksum(l_rp[(i,p)]*PC_p[p] for p in P) + M_r[i] + CTr_i[i])*Cam[e,a,i,j,k,t] for a in A for e in E for t in T for i in I for j in J for k in K)

obj += quicksum(CFB_i[i] + CAl_i[i]*quicksum(Al[a,i,k,t] for a in A) for t in T for i in I for k in K)

#------------------------- Minimización de costos -------------------------#

# 

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

#------------------------- Escritura de datos en resultados -------------------------#

sol_Tr = ""
sol_Cam = ""
sol_Al = ""
sol_ExT = ""

# times = T
# fa = 1
# fi = 1
# fk = K
# al_array = np.zeros((np.shape(times)[0],np.shape(fk)[0]))
# tr_array = np.zeros((np.shape(times)[0],np.shape(fk)[0]))

# Al[a,i,k,t] ExT[a,i,k,t] Tr[a,i,j,k,t,e] Cam[e,a,i,j,k,t]
for t in T:
    for i in I:
        for a in A:
            for j in J:
                for k in K:
                    for e in E:
                        sol_Tr += f" \n{int(Tr[a,i,j,k,t,e].x)},{a},{i},{j},{k},{t},{e}"
                        # if a == fa and i == fi:
                            # tr_array[t-1,k-1]=int(quicksum(Tr[a,i,j,k,t,e].x for e in E for j in J).getValue())
            for k in K:
                    sol_Al += f" \n{int(Al[a,i,k,t].x)},{a},{i},{k},{t}"
                    # if a == fa and i == fi:
                        # al_array[t-1,k-1]=int(Al[a,i,k,t].x)    

        for k in K:
            for j in J:
                for e in E:
                    for a in A:
                        sol_Cam += f" \n{int(Cam[e,a,i,j,k,t].x)},{e},{a},{i},{j},{k},{t}"    
            for  t in T:
                sol_ExT += f" \n{int(ExT[a,i,k,t].x)},{a},{i},{k},{t}"

with open("resultados/resultados_Tr_sv.csv", "w") as file:
    file.write("Tr,a,i,j,k,t,e")
    file.write(sol_Tr)

with open("resultados/resultados_Cam_sv.csv", "w") as file:
    file.write("Cam,e,a,i,j,k,t")
    file.write(sol_Cam)

with open("resultados/resultados_Al_sv.csv", "w") as file:
    file.write("Al,a,i,k,t")
    file.write(sol_Al)

with open("resultados/resultados_ExT_sv.csv", "w") as file:
    file.write("ExT,a,i,k,t")
    file.write(sol_ExT)

# fig, ax = plt.subplots()
# for current_k in fk:
#     ax.scatter(T, al_array[:,current_k-1], label=f"Al[1,1,{current_k},t]")
#     ax.scatter(T, tr_array[:,current_k-1], label=f"sum_e,j Tr[1,1,j,{current_k},t,e]")
# ax.legend()
# ax.grid(True)
# plt.show()