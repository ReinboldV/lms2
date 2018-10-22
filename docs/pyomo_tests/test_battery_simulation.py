## not working because pyomo.dae does not handle blocks at the moment

if __name__ == '__main__':

    from lms2.electric.batteries import Battery
    from lms2.core.models import LModel
    from lms2.core.time import Time

    from pyomo.dae.contset import ContinuousSet
    from pyomo.dae.simulator import Simulator
    from pyomo.environ import *

    model = LModel(name='model')
    time = Time('00:00:00', '03:00:00', freq='30Min')
    model.t = ContinuousSet(bounds=(time.timeSteps[0], time.timeSteps[-1]))

    model.bat = Battery(time=model.t, e0=12.0, emin=0.0, emax=500000, etac=0.8, etad=0.9, pcmax=100, pdmax=100)

    b_profile = {0: 10, 100: 20, 200: -20}

    model.var_input = Suffix(direction=Suffix.LOCAL)
    model.var_input[model.bat.p] = b_profile

    sim = Simulator(model, package='scipy')  # doctest: +SKIP
    tsim, profiles = sim.simulate(numpoints=100, integrator='vode', varying_inputs=model.var_input)  # doctest: +SKIP


