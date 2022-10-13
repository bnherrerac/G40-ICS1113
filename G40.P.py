import gurobipy
from gurobipy import GRB, Model
import pandas as pd
import csv
import numpy as np
from pyexpat import model 

#Parametros


#### ESCRIBA SU MODELO AQUI ####
model= Model("Minimizar los costos anuales de transporte de alimentos hacia Punta Arenas y el almacenamiento de ellos")
model.setParam("TiseLimit",60)

#Variables
Tr = model.addVars(a, i, j, k, t, vtype=GRB.CONTINUOUS, name="Tr")
Cam = model.addVars(i, j, k, t, vtype=GRB.CONTINUOUS, name="Cam")
Al = model.addVars(a, i, k, t, tau, vtype=GRB.CONTINUOUS, name="Al")
ExT = model.addVars(tau, a, i, k, t*, vtype=GRB.CONTINUOUS, name="ExT")


model.update()

#Restricciones

#Función Objetivo

model.setOb
obj = 

model.setObjective(obj, GRB.MINIMIZE) 
model.optimize()

model.objetivo = model.ObjVal

model.printAttr("X")
print("\n-------------\n")
