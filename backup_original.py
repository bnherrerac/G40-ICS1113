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
# cant_de_centros = 20
# cant_de_bodegas = 8
# cant_de_camiones = 30 # Cantidad total de camiones por categoría de alimento, sumado sobre todos los centros de distribución

cant_de_centros = 4
cant_de_bodegas = 4
cant_de_camiones = 6


# T = range(1, 52 + 1)    #tiempo
# Tau = range(1, 52 + 1)  #tiempo de llegada

T = range(1, 5 + 1)    #tiempo
Tau = range(1, 5 + 1)  #tiempo de llegada


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
flota_de_camiones = np.array([cant_de_camiones,cant_de_camiones,cant_de_camiones])
N_i = {(i): flota_de_camiones[j] for (i,j) in zip(I,range(len(I)))}
R_i = {"1": "Norte", "2": "Centro", "3": "Sur"}
V_m = 90 # 90 m3 es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
P_m = 31000 # 31000 kg es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
CFB_i = {(i): int(costo_fijo_almacenamiento[dict_tipos[i]]) for i in I}
CTr_i = {(i): int(costo_adicional_camiones[dict_tipos[i]]) for i in I}
CAl_i = {(i): float(costo_unitario_almacenamiento[dict_tipos[i]]) for i in I} # Arreglar este valor
q_ai = {(a,i): int(stock_inicial[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}

Omega = 100000000

# Propiedades de los alimentos
d_ai = {(a,i): int(demanda[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
P_ai = {(a,i): float(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
H_ai = {(a,i): float(costo_vencimiento[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}

print("i=1:", dict_tipos[1])
print("a=9", dict_alimentos[1][9])
print("q_ai[(9,1)]=",q_ai[(9,1)])
print("d_ai[(9,1)]=", d_ai[(9,1)])



# Ruta
l_rp = {(r,p): int(distancia_por_pais[dict_rutas[r]][dict_paises[p]]) for r in R for p in P}
PC_p = {(p): int(costo_combustible[dict_paises[p]]) for p in P}
PT_r = {(r): int(costo_ruta[dict_rutas[r]]) for r in R}
S_r = {(r): int(sueldo[dict_rutas[r]]) for r in R}
M_r = {(r): int(costo_mantencion[dict_rutas[r]]) for r in R}

# Vencimiento
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

# Esto checkea que v_taitau está bien definido.
# print(v_ai[(4,1)])
# print([v_taitau[(1,i,8,1)] for i in range(1,20)]) 

### Fuentes de los datos
# Camiones terrestres (pequeños): 90 m3, 12000 kg https://www.avantiatransportes.com/capacidad-de-carga-transporte-terrestre/ 
# Camiones trailer box (más grandes): 90 m3, 31400 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/camion-trailer-box-o-camion-furgon
# Camiones frigoríficos: 85 m3, 31000 kg https://www.dsv.com/es-es/nuestras-soluciones/modos-de-transporte/transporte-por-carretera/medidas-camion-trailer/trailer-frigorifico-o-camion-frigo
# Camiones para congelados: 85 m3, 31000 kg (mismo que arriba) http://www.frigocargo.cl/#project
# Se utiliza en algunos camiones este equipo de enfriamiento https://tkadvancer.thermokinginfo.com/upload/whisper-pro/publication/TK80063_Whisper_Pro_Brochure_05-2021_ES_V2.0_spread.pdf
print("Parámetros definidos")

#------------------------- Variables -------------------------#
print("Definiendo variables")
Cam = model.addVars(E, A, I, J, K, T, vtype=GRB.BINARY, name="Cam")
Tr = model.addVars(A, I, J, K, T, E, vtype=GRB.CONTINUOUS, name="Tr")
Al = model.addVars(Tau, A, I, K, T, vtype=GRB.CONTINUOUS, name="Al")
ExT = model.addVars(T, A, I, K, Tau, vtype=GRB.CONTINUOUS, name="ExT")
print("Variables definidas")
#------------------------- Restricciones -------------------------#
print("Agregando restricciones")

# Restricción 2
# sum_A sum_K sum_J sum_I Cam[e,a,i,j,k,t] \leq 1   \forall t in T, e in E
model.addConstrs( (quicksum(Cam[e,a,i,j,k,t] for i in I for j in J for k in K for a in A) <= 1 for e in E), name="R2")

# Restricción 3
# sum_E sum_K Cam[e,a,i,j,k,t] \leq N[i]    \forall i in I, j in J, t in T
model.addConstrs((quicksum(Cam[e,a,i,j,k,t] for k in K for e in E) <= N_i[i] for i in I for j in J for t in T), name="R3")

# Restricción 4
# Omega * Cam[e,a,i,j,k,t] >= Tr[a,i,j,k,t,e]   \forall i in I, j in J, t in T, k in K, a in A, e in E
model.addConstrs((Omega * Cam[e,a,i,j,k,t] >= Tr[a,i,j,k,t,e] for i in I for j in J for t in T for k in K for a in A for e in E), name="R4")

# Restricción 5
# Tr[a,i,j,k,t,e] * P_ai <= P
model.addConstrs((Tr[a,i,j,k,t,e]*P_ai[(a,i)] <= P_m for a in A for i in I for j in J for k in K for t in T for e in E), name="R5")

# Restricción 9, inventario inicial. q_ai duplicado
model.addConstrs((Al[1,a,i,k,1]== q_ai[a,i]-ExT[1,a,i,k,1] for i in I for a in A for k in K), name="R9")

cont = 0
for t in T:
    print(f"Agregando restricciones acumulativas para t = {t}")
    print("Definiendo intervalo de tiempos pasados para tiempo actual.")
    Tau_array = list(np.array(Tau)[np.array(Tau)<=t])
    print(f"Tau_array para t = {t}: ", Tau_array)
    
    # Esta restricción debería estar mala
    name_6 = "R6_" + str(cont)
    model.addConstrs((quicksum(Al[tau,a,i,k,t] for tau in Tau_array for k in K) >= d_ai[a,i] for a in A for i in I), name=name_6)
    
    name_7 = "R7_" + str(cont)
    model.addConstrs((quicksum(ExT[t,a,i,k,tau] for tau in Tau_array for k in K) >= d_ai[a,i] for a in A for i in I), name=name_7)

    name_8 = "R8_" + str(cont)
    model.addConstrs((ExT[t,a,i,k,tau] <= Al[tau,a,i,k,t] for a in A for i in I for k in K for tau in Tau_array), name=name_8)

    name_11 = "R11_" + str(cont)
    model.addConstrs((Al[tau,a,i,k,t]<=Omega*v_taitau[tau,t,a,i] for tau in Tau_array for k in K for a in A for i in I), name=name_11)

    name_10 = "R10_" + str(cont) 
    if t>=2:
        Tau_array_pop = Tau_array
        Tau_array.pop()
        model.addConstrs((quicksum(Al[tau,a,i,k,t] for tau in Tau_array) == (quicksum(Al[tau,a,i,k,t] for tau in Tau_array_pop) - Tr[a,i,j,k,t-1,e]-quicksum(ExT[t,a,i,k,tau] for tau in Tau_array)) for i in I for a in A for k in K for j in J for e in E), name=name_10)
    cont += 1



#------------------------- Función objetivo -------------------------#

obj = quicksum((PT_r[i]+S_r[i]+quicksum(l_rp[(i,p)]*PC_p[p] for p in P) + M_r[i] + CTr_i[i])*Cam[e,a,i,j,k,t] for a in A for e in E for t in T for i in I for j in J for k in K)

for t in T:
    print(f"Agregando restricciones con Tau en función objetivo para t = {t}.")
    Tau_array_2 = list(np.array(Tau)[np.array(Tau)<=t])
    print(f"Tau_array para t = {t}: ", Tau_array_2)
    print(f"Agregando costo de almacenamiento para t = {t}.")
    obj += quicksum(CFB_i[i]+quicksum(CAl_i[i]*P_ai[a,i]*quicksum(Al[tau,a,i,k,t] for tau in Tau_array_2) for a in A for k in K) for i in I)
    print(f"Agregando costo de vencimiento para t = {t}.")
    obj += quicksum(H_ai[(a,i)]*quicksum((1-v_taitau[(tau,t,a,i)])*Al[tau,a,i,k,t] for tau in Tau_array_2) for i in I for a in A for k in K)

#------------------------- Minimización de costos -------------------------#

model.setObjective(obj, GRB.MINIMIZE)
# model.feasRelaxS(1, False, False, True)
model.optimize()
status = model.status
if status == GRB.UNBOUNDED:
    print("The model cannot be solved because it is unbounded")
elif status == GRB.OPTIMAL:
    print("The optimal objective is %g" %model.ObjVal)
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
        
print("El costo minimizado es de",model.ObjVal,"CLP durante todo el año.")

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
                        sol_Tr += f" \n{int(Tr[a,i,j,k,t,e].x)},{a},{i},{j},{k},{t}.{e}"
            for k in K:
                for tau in Tau:
                    sol_Al += f" \n{int(Al[tau,a,i,k,t].x)},{tau},{a},{i},{k},{t}"
        for k in K:
            for j in J:
                for e in E:
                    for a in A:
                        sol_Cam += f" \n{int(Cam[e,a,i,j,k,t].x)},{e},{a},{i},{j},{k},{t}"    
            for  t in T:
                for tau in Tau:
                    sol_ExT += f" \n{int(ExT[t,a,i,k,tau].x)},{t},{a},{i},{k},{tau}"

with open("resultados/resultados_Tr.csv", "w") as file:
    file.write("Tr,a,i,j,k,t,e")
    file.write(sol_Tr)

with open("resultados/resultados_Cam.csv", "w") as file:
    file.write("Cam,e,a,i,j,k,t")
    file.write(sol_Cam)

with open("resultados/resultados_Al.csv", "w") as file:
    file.write("Al,tau,a,i,k,t")
    file.write(sol_Al)

with open("resultados/resultados_ExT.csv", "w") as file:
    file.write("ExT,t,a,i,k,tau")
    file.write(sol_ExT)