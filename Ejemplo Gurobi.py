from gurobipy import GRB, Model

m = Model()

x = m.addVar(vtype=GRB.CONTINUOUS, name="x")
y = m.addVar(vtype=GRB.CONTINUOUS, name="y")
z = m.addVar(vtype=GRB.CONTINUOUS, name="z")

m.update()

m.setObjective(x + z, GRB.MAXIMIZE)

m.addConstr(x + y + z <= 5, name="R1")
m.addConstr(x - z >= -3, name="R2")
m.addConstr(x - y - z <= 1, name="R3")
m.addConstr(x >= 0, name="R4")
m.addConstr(y >= 0, name="R5")
m.addConstr(z >= 0, name="R6")

m.optimize()

m.printAttr("X")
