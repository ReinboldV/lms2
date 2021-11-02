from pyomo.dae import ContinuousSet, Integral
from pyomo.environ import *
from lms2.core.horizon import SimpleHorizon

m = ConcreteModel()
horizon = SimpleHorizon(tstart='2020-01-01 00:00:00', tend='2020-01-02 00:00:00', time_step='10 min')
m.time = ContinuousSet(initialize=[0, horizon.horizon.total_seconds()])
