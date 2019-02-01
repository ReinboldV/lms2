
from pyomo.dae.integral import Integral
from pyomo.environ import *
from pyomo.dae.contset import ContinuousSet


m = ConcreteModel(name='m')
time = ContinuousSet(bounds=(0, 1), name='time')

m.block = Block()
m.block.x = Var(m.time)


def _instant_obj(m, t):
    return m.x[t]


m.mg.int_cost = Integral(m.time, wrt=time, rule=_instant_obj)


m.pprint()

#m.block2 = Block1(time=m.t)


# class blokTest(DynUnit):
#     """ Base units for tests """
#
#     def __init__(self, *args, time, flow):
#
#         super().__init__(*args, time=time)
#         _init_input, _set_bounds = set_profile(profile=flow, kind='linear', fill_value='extrapolate')
#
#         self.x1 = Var(time, initialize=_init_input, bounds=_set_bounds)
#         self.x1.port_type = 'effort'
#         self.x2 = Var(time, initialize=0)
#         self.x2.port_type = 'effort'
#         self.y1 = Var(time, bounds=(0, 100))
#
#         def _cst1(m, t):
#             return m.x1[t] - m.x2[t] == m.y1[t]
#
#         self.cst1 = Constraint(time, rule=_cst1)
#
#         def _obj(m):
#             return sum(m.y1[t] for t in time)
#
#         def _instant_obj(m, t):
#             return m.y1[t]
#
#         self.int_cost = Integral(time, wrt=time, rule=_instant_obj)  # this line is the trouble
#
#         def _obj2(m):
#             return m.int_cost
#
#         ##self.obj2 = Objective(rule=_obj2)
#         self.obj = Objective(rule=_obj)
#
#
#
# m = LModel(name='m')
# t = Time('01-01-2018 00:00:00', '01-02-2018 00:00:00', freq='30min')
# t.nfe = int(t.delta/t.dt)
# m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))
#
# low = pd.Series({0.0: 0.0, 86400: 5})
#
# m.u = UnitA(time=m.t, flow=low)
#
# discretizer = TransformationFactory('dae.finite_difference')
# discretizer.apply_to(m, nfe=t.nfe)  # BACKWARD or FORWARD
#
# opt = SolverFactory("glpk")
# results = opt.solve(m)
# print(results)