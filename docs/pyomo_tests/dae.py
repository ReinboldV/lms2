from pyomo.environ import *
from pyomo.dae.contset import ContinuousSet
from pyomo.dae.diffvar import DerivativeVar

m = ConcreteModel()
m.t = ContinuousSet(bounds=(1, 10))


def _init(m, t):
    return 10*t

m.p = Param(m.t, initialize=_init, default=_init)
m.x = Var(m.t, initialize=_init)

discretizer = TransformationFactory('dae.finite_difference')#'dae.collocation')
discretizer.apply_to(m, wrt=m.t, nfe=9)  # BACKWARD or FORWARD

m.pprint()
m.p.pprint()

