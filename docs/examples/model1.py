from pyomo.environ import Var, Param, Objective, Constraint
from pyomo.environ import NonNegativeIntegers
from lms2 import AbsLModel

m = AbsLModel(name = 'Model')
m.v = Var(doc='a viariable', within=NonNegativeIntegers)

m.p = Param(default=10, doc='a parameter')
m.c = Param(default=1, doc='cost associated to variable "v"')

m.cst = Constraint(expr= 10 <= m.v*m.p <= 15)
m.obj = Objective(expr=m.c*m.v, sense=1)

inst = m.create_instance()
inst.pprint()

from pyomo.environ import SolverFactory
opt = SolverFactory("glpk")
results = opt.solve(inst, tee=False)
print(inst.v())

data = {None: {'p': {None: 5},
               'c': {None: 2}}}

inst2 = m.create_instance(data)
results = opt.solve(inst2, tee=False)
print(inst.v())