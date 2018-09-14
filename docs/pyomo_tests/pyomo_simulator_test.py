# testing dynamic Model and simulation with pyomo with time-varing inputs

from pyomo.core.base.constraint import Constraint
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.kernel.set_types import *
from pyomo.environ import *
from pyomo.dae import *

from lms2.core.units import DynUnit
from lms2.core.var import Var
from lms2.core.param import Param


class DynMechUnit(DynUnit):
    """

    :param DynUnit:
    :return:
    """
    from numpy import sin

    def __init__(self, time, *args, **kwgs):
        super().__init__(*args, time=time, **kwgs)

        # Time-varying inputs
        self.b = Var(time)
        self.c = Param(time, default=5.0)

        self.omega = Var(time, initialize=0)
        self.theta = Var(time, initialize=3.14 - 0.1)

        self.domegadt = DerivativeVar(self.omega, wrt=time, initialize=0)
        self.dthetadt = DerivativeVar(self.theta, wrt=time, initialize=0)

        # Setting the initial conditions
        # self.omega[0] = 0.0
        # self.theta[0] = 3.14 - 0.1

        def _diffeq1(m, t):
            return m.domegadt[t] == -m.b[t] * m.omega[t] - \
                   m.c[t] * sin(m.theta[t])

        self.diffeq1 = Constraint(time, rule=_diffeq1)

        def _diffeq2(m, t):
            return m.dthetadt[t] == m.omega[t]

        self.diffeq2 = Constraint(time, rule=_diffeq2)


if __name__ == "__main__":
    from lms2.core.models import LModel
    from lms2.core.time import Time
    from lms2.electric.batteries import Battery
    from pyomo.environ import *

    m = LModel(name='model')
    m.time = Time('00:00:00', '00:00:50', freq='1Min')

    m.dyn = DynMechUnit(time=m.time.time_contSet)

    # Specifying the piecewise constant inputs
    b_profile = {0: 0.25, 15: 0.025}
    c_profile = {0: 5.0, 7: 50}

    # Declaring a Pyomo Suffix to pass the time-varying inputs to the Simulator
    m.dyn.var_input = Suffix(direction=Suffix.LOCAL)
    m.dyn.var_input[m.dyn.b] = b_profile
    m.dyn.var_input[m.dyn.c] = c_profile

    # Simulate the model using scipy
    from pyomo.dae.simulator import Simulator

    sim = Simulator(m.dyn, package='scipy')
    tsim, profiles = sim.simulate(numpoints=500, integrator='vode', varying_inputs=m.dyn.var_input)

    import matplotlib.pyplot as plt

    f = plt.figure()
    plt.plot(tsim, profiles)
    plt.show()
