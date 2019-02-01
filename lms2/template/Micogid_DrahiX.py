
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
import os


os.chdir('/home/admin/Documents/02-Recherche/02-Python/pypeper/')
usecols = ['Date and time (UTC)', 'TGBT', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'Pmax']
df = pd.read_csv('pypeper/data/DrahiX_SIRTA_eCO2mix_20160715_20180930.csv',
              usecols=usecols, index_col=0, parse_dates=True)

df['Pmax'] = df['Pmax'].fillna(0)


t_start = '05-01-2018 00:00:00'
t_end   = '05-11-2018 00:00:00'
freq    = '15Min'

t = Time(t_start, t_end, freq=freq)

pv    = df['Pmax'][t_start:t_end].resample(freq).interpolate()/1000
conso = df['TGBT'][t_start:t_end].resample(freq).interpolate()
cin   = 0.15#0.1452
cout  = 0.15#0.1680

m = LModel(name='model')
m.t = ContinuousSet(bounds=(0, t.delta))

df2 = pd.DataFrame({'date': pv.index, 'pv': pv.values, 'conso': conso.values}, index=t.timeSteps)

m.bat1  = Battery(time=m.t, e0=25.0, ef=25.0, emin=5.0, emax=500, etac=1, etad=1, pcmax=15, pdmax=15)
m.mg    = MainGrid(time=m.t, cin=cin, cout=cout, pmax=500, pmin=500, mixCO2=70)
m.ps    = ScalablePowerSource(time=m.t, profile=df2['pv'], flow_name='p')
m.pl    = PowerLoad(time=m.t, profile=df2['conso'], flow_name='p')

m.connect_flux(m.bat1.p, m.ps.p, m.mg.p, m.pl.p)

discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=t.nfe)  # BACKWARD or FORWARD

# m.mg.energy.reconstruct()
# m.mg.cost.reconstruct()
# m.mg.pro.reconstruct()
#m.obj = Objective(expr=m.mg.cost)


from pyomo.environ import Suffix, Var, Constraint

m.dual = Suffix(direction=Suffix.IMPORT)
m.x = Var()
#m.obj = Objective(expr=m.x)
m.con = Constraint(expr=m.x>=1.0)



def instant_cost(m, t):
    return (-m.mg.pin[t] * m.mg.cin + m.mg.pout[t] * m.mg.cout)/3600


def power(m, t):
    return (-m.mg.pin[t] + m.mg.pout[t])/3600


def instant_prosumation(m, t):
    return (m.mg.pin[t] + m.mg.pout[t])/3600


def instant_co2(m, t):
    return (m.mg.pout[t] - m.mg.pin[t])*m.mg.mixCO2/3600


m.cost = Integral(m.t, wrt=m.t, rule=instant_cost)
m.energy = Integral(m.t, wrt=m.t, rule=power)
m.prosum = Integral(m.t, wrt=m.t, rule=instant_prosumation )

m.obj = Objective(expr=m.cost)


import time
t1 = time.time()
results = SolverFactory("glpk").solve(m,  tee=True)
t2 = time.time() - t1
print(results)
print(f'Elapsed time : \t {t2}')

## PLOTTING

# fig = plt.figure(figsize=(15, 10))
# ax = fig.subplots(2, 1)
#
# pplot(m.mg.p, m.ps.p, m.bat1.p, m.pl.p, fig=fig, ax=ax[0], index=t.datetime, legend=True,
#       title='Power Balance', Marker='x')
#
# pplot(m.bat1.e,  index=t.datetime, legend=True, grid=True, fig=fig, ax=ax[1], title='Storage Energy', Marker='x')
#
# print(m.energy())
# print(m.ps.scale_fact())
# print(m.cost())
# plt.show()

## GET SLACK VARIABLES

#df = m.bat1.get_slack()

## GET DUAL VARIABLES
# Fixing binary variables

for u in m.component_objects(Var):
    if u.is_indexed():
        for ui in u.itervalues():
            if ui.is_binary():
                ui.fix(ui.value)
    else:
        if u.is_binary():
            u.fix(u.value)

# solving the new LP problem

t1 = time.time()
results = SolverFactory("glpk").solve(m,  tee=True)
t2 = time.time() - t1
print(results)
print(f'Elapsed time : \t {t2}')



df = m.get_duals()

df.sum()



