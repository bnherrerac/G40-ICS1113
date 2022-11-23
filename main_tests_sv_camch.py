from gurobipy import GRB, Model, quicksum
from gurobipy import *
import pandas as pd # Si sale error, escribir en cmd pip install pandas
import numpy as np # Si sale error, escribir en cmd pip install numpy
from archivos.carga_datos import *
import matplotlib.pyplot as plt

model = Model()
# model.setParam("TimeLimit", 60*30) # 30 min time limit
model.setParam('MIPGap', 0.01)



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

demandas = [1,1.2,1.5]
mult_costo_combustible = []
array_camiones =  [7,9,11,13]
costo_unitario_almacenamiento [1,1.5,2]
# Cantidad de camiones pareja por tipo

times = T
fa = 1
fi = 1
fk = K
fe = E
# al_array = np.zeros((np.shape(times)[0],np.shape(fk)[0]))
# tr_array = np.zeros((np.shape(times)[0],np.shape(fk)[0]))
al_array_d = np.zeros((np.shape(times)[0],np.shape(fk)[0],len(demandas)))
tr_array_d = np.zeros((np.shape(times)[0],np.shape(fk)[0],len(demandas)))
for p in range(len(demandas)):

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
    P_m = 25000 # 31000 kg es lo más común en camiones de transporte de alimentos, ver fuentes de abajo. 
    CFB_i = {(i): int(costo_fijo_almacenamiento[dict_tipos[i]]) for i in I}
    CTr_i = {(i): int(costo_adicional_camiones[dict_tipos[i]]) for i in I}
    CAl_i = {(i): float(costo_unitario_almacenamiento[dict_tipos[i]]) for i in I} # Arreglar este valor
    q_ai = {(a,i): int(stock_inicial[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}

    Omega = 10000000
    # Propiedades de los alimentos
    d_ai = {(a,i): int(demanda[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}
    P_ai = {(a,i): float(peso_promedio[dict_tipos[i]][dict_alimentos[i][a]]) for i in I for a in A}


    # peso_en_demanda = {(a,i): d_ai[(a,i)]*P_ai[(a,i)] for i in I for a in A}
    # print(peso_en_demanda)
    # print("Max peso en demanda: ", max(peso_en_demanda))
    # print("Alimento para el que es máximo: ", peso_en_demanda[max(peso_en_demanda, key=peso_en_demanda.get)])

    # print("i=1:", dict_tipos[1])
    # print("a=8", dict_alimentos[1][8])
    # print("q_ai[(8,1)]=",q_ai[(8,1)])
    # print("d_ai[(8,1)]=", d_ai[(8,1)])

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

    # Restricción 2
    # sum_A sum_K sum_J sum_I Cam[e,a,i,j,k,t] \leq 1   \forall t in T, e in E

    # Cada camión puede llevar 1 solo tipo de cosas
    # suma sobre i da 1
    model.addConstrs((quicksum(Cam[e,i,j,k,t] for j in J for k in K for i in I) <= 1 for t in T for e in E), name="R2")
    model.addConstrs((quicksum(Cam[e,i,j,k,t] for j in J for k in K for e in E for i in I) <= cant_de_camiones for t in T), name="R2b")

    # model.addConstrs((quicksum(Cam[e,i,j,k,t] for j in J for k in K for e in E for i in I)), name="R2c")

    # para cierto t, j, k, e Cam[e,i,j,k,t] = 1 entonces Cam[e,i,j,k,t] = 0 para los otros
 
    for i in T:
        t_var = list(T)
        print(t_var)
        t_var.remove(i)
        print(f"t_var para i = {i}")
        print(t_var)
        model.addConstrs(((1/Omega)*quicksum(Cam[e,i,j,k,i1] for i1 in t_var)<=Cam[e,i,j,k,t] for i in I for j in J for k in K for e in E for t in T), name="R2c")

    # Restricción 4
    # Si no se transporta nada, Cam = 0
    # Omega * Cam[e,a,i,j,k,t] >= Tr[a,i,j,k,t,e]   \forall i in I, j in J, t in T, k in K, a in A, e in E
    model.addConstrs((Cam[e,i,j,k,t]*(1/Omega) <= quicksum(Tr[a,i,j,k,t,e] for a in A) for i in I for j in J for t in T for k in K for e in E), name="R4")

    # Restricción sobre peso máximo de los camiones
    model.addConstrs((quicksum(Tr[a,i,j,k,t,e]*P_ai[(a,i)] for a in A ) <= P_m for i in I for j in J for k in K for t in T for e in E), name="Rpeso")

    # Máximo de capacidad en peso: doble de la demanda
    # model.addConstrs((quicksum(Al[a,i,k,t]*P_ai[(a,i)] for a in A for i in I) <= 50000 for k in K for t in T), name="Rbodega")

    # Restricción para que si se transporta, Cam = 1
    # Tr > 0 entonces Cam = 1
    model.addConstrs((quicksum(Tr[a,i,j,k,t,e] for a in A)*(1/Omega) <= Cam[e,i,j,k,t] for i in I for e in E for t in T for j in J for k in K), name="R4cond")

    # Restricción 9, inventario inicial
    # Inicialmente hay 0 y llega lo que se transporta
    # Después de la extracción hay Al
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


    ######### NUEVA
    # model.addConstrs((quicksum(Al[a,i,k,tmax] for k in K) >= d_ai[(a,i)] for a in A for i in I),name="RTfinal") 

    # Restricción 7
    # Todo lo que se extrae de todas las bodegas es igual a la demanda
    model.addConstrs((quicksum(ExT[a,i,k,t] for k in K) == d_ai[(a,i)] for a in A for i in I for t in T), name="R7")

    #------------------------- Función objetivo -------------------------#

    obj = quicksum((PT_r[i]+S_r[i]+quicksum(l_rp[(i,p)]*PC_p[p] for p in P) + M_r[i] + CTr_i[i])*Cam[e,i,j,k,t] for e in E for t in T for i in I for j in J for k in K)

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


    camiones_array = np.zeros((np.shape(times)[0],np.shape(fe)[0]))

    # Al[a,i,k,t] ExT[a,i,k,t] Tr[a,i,j,k,t,e] Cam[e,a,i,j,k,t]
    for t in T:
        for i in I:
            for a in A:
                for j in J:
                    for k in K:
                        for e in E:
                            sol_Tr += f" \n{int(Tr[a,i,j,k,t,e].x)},{a},{i},{j},{k},{t},{e}"
                            if a == fa and i == fi:
                                tr_array_d[t-1,k-1,p]=float(quicksum(Tr[a,i,j,k,t,e].x for a in A for i in I for e in E for j in J).getValue())
                                camiones_array[t-1,e-1]=float(quicksum(Tr[a,i,j,k,t,e].x for k in K for a in A for i in I for j in J).getValue())


                for k in K:
                        sol_Al += f" \n{int(Al[a,i,k,t].x)},{a},{i},{k},{t}"
                        if a == fa and i == fi:
                            al_array_d[t-1,k-1,p]=float(quicksum(Al[a,i,k,t].x for a in A for i in I).getValue())    
                            # platanos_array[t-1,k-1]=float()
            for k in K:
                for j in J:
                    for e in E:
                        sol_Cam += f" \n{int(Cam[e,i,j,k,t].x)},{e},{i},{j},{k},{t}"    
                for a in A:
                    for t in T:
                        sol_ExT += f" \n{int(ExT[a,i,k,t].x)},{a},{i},{k},{t}"

    with open("resultados/resultados_Tr_sv_camch.csv", "w") as file:
        file.write("Tr,a,i,j,k,t,e")
        file.write(sol_Tr)

    with open("resultados/resultados_Cam_sv_camch.csv", "w") as file:
        file.write("Cam,e,i,j,k,t")
        file.write(sol_Cam)

    with open("resultados/resultados_Al_sv_camch.csv", "w") as file:
        file.write("Al,a,i,k,t")
        file.write(sol_Al)

    with open("resultados/resultados_ExT_sv_camch.csv", "w") as file:
        file.write("ExT,a,i,k,t")
        file.write(sol_ExT)

fig, ax = plt.subplots()

for p in range(len(demandas)):
    for current_k in fk:
        ax.plot(T, al_array_d[:,current_k-1,p], label=f"sum_(a,i) Al[a,i,{current_k},t]; C={demandas[p]}")
        ax.plot(T, tr_array_d[:,current_k-1,p], label=f"Sum_(a,i,e,j) Tr[a,i,j,{current_k},t,e]; C={demandas[p]}")
ax.legend()
ax.grid(True)
fig.suptitle("Cantidad almacenada y cantidad transportada de todos los alimentos, según multiplicador de costo de combustible C.")
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
ax.ticklabel_format(useOffset=False)
plt.show()

fig, ax = plt.subplots()
for camion in fe:
    ax.plot(T, camiones_array[:,camion-1], label=f"Sum_(a,i,j) Tr[a,i,j,k,t,{camion}]")
ax.legend()
ax.grid(True)
fig.suptitle("Cantidad de alimentos transportada por cada camión.")
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
ax.ticklabel_format(useOffset=False)
plt.show()

