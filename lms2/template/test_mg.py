from lms2.electric.batteries import Battery
from lms2.electric.maingrids import MainGrid
from lms2.electric.sources import PowerSource
from lms2.core.models import LModel
from lms2.core.time import Time

from pyomo.environ import Objective, SolverFactory, TransformationFactory
from pyomo.dae.contset import ContinuousSet

import matplotlib
import matplotlib.pyplot as plt
from lms2.base.utils import pplot
import pandas as pd

matplotlib.use('Agg')

m = LModel(name='model')
t = Time('01-01-2018 00:00:00', '01-02-2018 00:00:00', freq='15min')
t.nfe = int(t.delta/t.dt)
m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))


source = pd.Series({0.0: 0.0, 10000: 1, 20000: 3, 25000: 3, 40000: 3.5, 45000: 3, 50000: 1.5, 86000: 0})


cin = pd.Series( {0.0: 7.0, 20000: 4, 50000: 2,  75000: 2, 86000: 2.0})
cout = pd.Series({0.0: 7.0, 20000: 4, 50000: 2,  75000: 2, 86000: 2.0})

m.bat1  = Battery(time=m.t, e0=100.0, ef=100, emin=10.0, emax=200, etac=1, etad=1, pcmax=10, pdmax=10)
m.mg    = MainGrid(time=m.t, cin=cin, cout=cout, pmax=5, pmin=5)
m.ps    = PowerSource(time=m.t, profile=source, flow_name='p')
m.connect_flux(m.bat1.p, m.ps.p, m.mg.p)

discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=t.nfe)  # BACKWARD or FORWARD

# m.mg.energy.reconstruct()
m.mg.cost.reconstruct()
# m.mg.pro.reconstruct()
m.obj = Objective(expr=m.mg.pro)

# def _cost(m):
#      return sum(- m.mg.pin[t] * m.mg.cin[t] + m.mg.pout[t] * m.mg.cout[t] for t in m.t)

# m.obj = Objective(rule=_cost)

# opt = SolverFactory('gurobi')
opt = SolverFactory("glpk")
results = opt.solve(m)
print(results)

pplot(m.mg.pout, m.mg.pin, m.mg.p, m.ps.p, m.bat1.pc, m.bat1.pd, m.bat1.p, index=t.datetime, legend=True, title='Main Grid', Marker='x')

pplot(m.mg.cin, m.mg.cout, index=t.datetime, legend=True, title='Prix achat/vente', Marker='x')

pplot(m.bat1.e)

plt.show()