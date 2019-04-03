from lms2 import DrahixMicrogridV2, Time, pplot

from pyomo.environ import TransformationFactory, SolverFactory
import matplotlib.pyplot as plt
import pandas as pd
import os
import time


def to_seconds(timedelta):
    return timedelta.days * 24 * 3600 + timedelta.seconds + timedelta.microseconds / 1e6


os.chdir('/home/admin/Documents/02-Recherche/02-Python/pypeper/')
usecols = ['Date and time (UTC)', 'TGBT', 'Pmax']
df = pd.read_csv('pypeper/data/DrahiX_SIRTA_eCO2mix_20160715_20180930.csv',
                 usecols=usecols, index_col=0, parse_dates=True, dayfirst=True)

t_start = '2018-03-01 00:00:00'
t_end = '2018-04-01 00:00:00'
freq = '5Min'

t = Time(t_start, t_end, freq=freq)
df = df[t_start:t_end]

# change index from timestamps to second
df.index = to_seconds(df.index - df.index[0])
df['Pmax'] = df['Pmax'].fillna(0)/1000
df.rename(columns={'Pmax': 'P_pv', 'TGBT': 'P_load'}, inplace=True)

df = df.apply(lambda x: round(x, 3))

m = DrahixMicrogridV2(name='m', dataframe=df)

m.mg.pmax = 150
m.mg.pmin = 150

m.mg.cin  = 0.10
m.mg.cout = 0.15

m.bat1.emax = 200
m.bat1.pdmax = 20
m.bat1.pcmax = 20
m.bat1.etac = 0.98
m.bat1.etad = 0.95

TransformationFactory("network.expand_arcs").apply_to(m)
m.obj = m.construct_objective_from_expression_list(m.t, m.mg.instant_cost, m.bat1.instant_cost)

# m.construct_objective_from_tagged_expression()

m.pprint()

# m.ps.scale_fact.setlb(10)
# m.ps.scale_fact.setub(500)
m.ps.scale_fact.fix(200)

t1 = time.time()
discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=t.nfe)  # BACKWARD or FORWARD
t2 = time.time() - t1
print(f'Elapsed time for discretization : \t {t2}')


# opt = SolverFactory("glpk")
# opt = SolverFactory("cbc")
opt = SolverFactory("gurobi", solver_io="direct")

t1 = time.time()
# opt.options['tmlim'] = 120
# opt.options['allow'] = 0.1
results = opt.solve(m, tee=False) # tee = true for more outpus
t2 = time.time() - t1
print(f'Elapsed time : \t {t2}')

print(results)
print(m.obj())


f = plt.figure(figsize=(16, 10))
ax = f.subplots(1, 1)

pplot(m.mg.p, m.ps.p, m.bat1.p, m.pl.p, fig=f, ax=ax, index=t.datetime, legend=True, title="Bilan d'énergie", Markers='x')
plt.grid(True)

f = plt.figure(figsize=(16, 10))
ax = f.subplots(1, 1)

pplot(m.bat1.e, fig=f, ax=ax, index=t.datetime, legend=True, title='Stored Energy (kWh)', Marker='x')
plt.grid(True)
plt.show()






