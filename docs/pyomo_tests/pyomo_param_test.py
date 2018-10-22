
if __name__ == "__main__":

    from lms2.core.time import Time
    from pyomo.dae.diffvar import DerivativeVar
    from pyomo.environ import *

    m = ConcreteModel()

    m.t = RangeSet(1, 10)

    m.x = Var(m.t)
    m.dx = DerivativeVar(m.x, wrt=m.t)

    m.p = Param(m.t, initialize=-10, mutable=True)

    def _cst(m, t):
        return m.dx[t] == m.p[t]

    # def _cst(m, t):
    #     return -10 <= m.x[t] <= 10

    # model.cst = Constraint(time, rule=_cst)
    m.cst = Constraint(m.t, rule=_cst)

    discretizer = TransformationFactory('dae.finite_difference')
    discretizer.apply_to(m, wrt=m.t, nfe=6, scheme='BACKWARD')  # BACKWARD or FORWARD

    m.pprint()










