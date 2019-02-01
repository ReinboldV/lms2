from lms2.electric.batteries import Battery
from lms2.electric.maingrids import MainGrid
from lms2.electric.sources import ScalablePowerSource, PowerLoad
from lms2.core.models import LModel
from lms2.core.time import Time

from pyomo.dae.integral import Integral
from pyomo.dae.contset import ContinuousSet
from pyomo.dae.plugins.finitedifference import TransformationFactory
from pyomo.environ import Objective, SolverFactory

import matplotlib
import matplotlib.pyplot as plt
from lms2.base.utils import pplot
import pandas as pd
import numpy as np

time = np.linspace(0, 86400, num=50, endpoint=True)
sigma = 8000
mu = 45000


def irr(t):
    return np.exp( - (t - 45000)**2 / (2 * sigma**2))


irr  = pd.Series([irr(i) for i in time], index=time)   # Gaussian irradiance (kW/m²)
load = pd.Series({0: 2,   86400: 2})  # constant load of 2 kW
cin  = pd.Series({0: 0.1, 86400: 0.1}) # constant selling price of 0.1 euro/kWh
cout = pd.Series({0: 0.1, 86400: 0.1}) # constant buying price of 0.1 euro/kWh

irr.plot(label='irradiance ($kW/m^2$)')
cin.plot(label='selling price (euros/kWh)')
cout.plot(label='buying price (euros/kWh)')
load.plot(label='load (kW)')
plt.xlabel('Time (s)')
plt.legend()
plt.grid(True)




m = LModel(name='model')
t = Time('01-01-2018 00:00:00', '01-02-2018 00:00:00', freq='5min')
m.t = ContinuousSet(bounds=(0, t.delta))
m.bat1  = Battery(time=m.t, e0=100.0, ef=100, emin=10.0, emax=200, etac=0.98, etad=0.98, pcmax=10, pdmax=10)
m.mg    = MainGrid(time=m.t, cin=cin, cout=cout, pmax=6, pmin=6, mixCO2=70)
m.ps    = ScalablePowerSource(time=m.t, profile=irr, flow_name='p')
m.pl    = PowerLoad(time=m.t, profile=load, flow_name='p')
m.connect_flux(m.bat1.p, m.ps.p, m.mg.p, m.pl.p)



opt = SolverFactory("glpk")
import time
t1 = time.time()
results = opt.solve(m)
t2 = time.time() - t1
print(f'Elapsed time : \t {t2}')



print(results)

pplot(m.mg.p, m.ps.p, m.bat1.p, m.pl.p, index=t.datetime, legend=True, title='Main Grid', Marker='x')
plt.grid(True)
pplot(m.mg.cin, m.mg.cout, index=t.datetime, legend=True, title='Prix achat/vente', Marker='x')
plt.grid(True)
pplot(m.bat1.e, index=t.datetime, legend=True, title='Stored Energy (kWh)', Marker='x')
plt.grid(True)
plt.show()