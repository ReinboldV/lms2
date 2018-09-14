import unittest
from pyomo.environ import *


class BatteriesTests(unittest.TestCase):
    """ Testing Batteries Modules """

    def test_Battery(self):
        """ testing Battery """

        from lms2.electric.batteries import Battery
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet

        model = LModel(name='model')
        time = Time('00:00:00', '03:00:00', freq='30Min')
        model.t = ContinuousSet(bounds=(time.timeSteps[0], time.timeSteps[-1]))

        model.bat1 = Battery(time=model.t, e0=12.0, emin=0.0, emax=500000, etac=0.8, etad=0.9, pcmax=100, pdmax=100)

        discretizer = TransformationFactory('dae.finite_difference')
        discretizer.apply_to(model, nfe=30)  # BACKWARD or FORWARD

        def _obj(m):
            return 0
        model.obj = Objective(rule=_obj)

        opt = SolverFactory('glpk')
        results = opt.solve(model)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)


if __name__ == '__main__':
    suite = unittest.TestLoader().discover(start_dir='.', pattern='test_*.py')
    unittest.TextTestRunner(verbosity=2).run(suite)
