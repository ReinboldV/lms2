from lms2.electric.batteries import Battery
from lms2.electric.maingrids import MainGrid
from lms2.electric.sources import ScalablePowerSource, PowerLoad
from lms2.core.models import LModel
from lms2.core.time import Time
from lms2.base.utils import pplot

from pyomo.dae.integral import Integral
from pyomo.environ import Objective, SolverFactory, TransformationFactory
from pyomo.dae.contset import ContinuousSet

import matplotlib.pyplot as plt

import pandas as pd


m = LModel(name='model')
t = Time('01-01-2018 00:00:00', '01-02-2018 00:00:00', freq='5min')
m.t = ContinuousSet(bounds=(0, t.delta))


source = pd.Series({0.0: 0.0, 10000: 1, 20000: 3, 25000: 3, 40000: 3.5, 45000: 3, 50000: 1.5, 86000: 0})
charge = pd.Series({0: 2, 86000: 3})
cin = pd.Series( {0.0: 0.1, 20000: 0.15, 50000: 0.2,  75000: 0.2, 86000: 0.15})
cout = pd.Series({0.0: 0.1, 20000: 0.15, 50000: 0.2,  75000: 0.2, 86000: 0.15})

m.bat1  = Battery(time=m.t, e0=100.0, ef=100, emin=10.0, emax=200, etac=0.98, etad=0.98, pcmax=10, pdmax=10)
m.mg    = MainGrid(time=m.t, cin=cin, cout=cout, pmax=5, pmin=5, mixCO2=70)
m.ps    = ScalablePowerSource(time=m.t, profile=source, flow_name='p')
m.pl    = PowerLoad(time=m.t, profile=charge, flow_name='p')

m.connect_flux(m.bat1.p, m.ps.p, m.mg.p, m.pl.p)

discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=t.nfe)  # BACKWARD or FORWARD

# m.mg.energy.reconstruct()
# m.mg.cost.reconstruct()
# m.mg.pro.reconstruct()
#m.obj = Objective(expr=m.mg.cost)


def instant_cost(m, t):
    return (-m.mg.pin[t] * m.mg.cin[t] + m.mg.pout[t] * m.mg.cout[t])/3600

def power(m,t):
    return (-m.mg.pin[t] + m.mg.pout[t])/3600

def instant_prosumation(m,t):
    return (m.mg.pin[t] + m.mg.pout[t])/3600

def instant_co2(m,t):
    return (m.mg.pout[t] - m.mg.pin[t])*m.mg.mixCO2/3600

m.cost = Integral(m.t, wrt=m.t, rule=instant_cost)
m.energy = Integral(m.t, wrt=m.t, rule=power)
m.prosum = Integral(m.t, wrt=m.t, rule=instant_prosumation )

m.obj = Objective(expr=m.cost)

opt = SolverFactory("glpk")
import time
t1 = time.time()
results = opt.solve(m)
t2 = time.time() - t1
print(f'Elapsed time : \t {t2}')

print(m.energy())
print(m.ps.scale_fact())
plt.show()