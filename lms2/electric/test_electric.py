import unittest
from pyomo.environ import *


class BatteriesTests(unittest.TestCase):
    """ Testing Batteries Modules """

    def test_Battery(self):
        """ testing Battery."""

        from lms2.electric.batteries import Battery
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet

        model = LModel(name='model')
        time = Time('00:00:00', '03:00:00', freq='30Min')
        model.t = ContinuousSet(bounds=(time.timeSteps[0], time.timeSteps[-1]))

        model.bat1 = Battery(time=model.t, e0=50, emin=0.0, emax=10000, etac=0.8, etad=0.9, pcmax=10, pdmax=10)

        TransformationFactory('dae.finite_difference').apply_to(model, nfe=30)

        def _obj(m):
            return 0
        model.obj = Objective(rule=_obj)

        opt = SolverFactory('glpk')
        results = opt.solve(model)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

    def test_Battery2(self):
        """ testing Battery 2 """

        from lms2.electric.batteries import Battery
        from lms2.electric.sources import PowerSource
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet
        import pandas as pd

        model = LModel(name='model')
        time = Time('00:00:00', '00:10:00', freq='1Min')
        model.t = ContinuousSet(bounds=(time.timeSteps[0], time.timeSteps[-1]))

        model.bat1 = Battery(time=model.t, e0=500.0, emin=0.0, emax=1000, etac=0.9, etad=0.8, pcmax=10000, pdmax=10000)
        source = pd.Series({0.0: 0.0, 60: -0.5, 300: 1, 400: -1, 600: 0.5})
        model.ps = PowerSource(time=model.t, profile=source, flow_name='p')
        model.connect_flux(model.bat1.p, model.ps.p)

        def _obj(m):
            return 0
        model.obj = Objective(rule=_obj)

        TransformationFactory('dae.finite_difference').apply_to(model, nfe=30)

        opt = SolverFactory('glpk')
        results = opt.solve(model)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)


class SourceTests(unittest.TestCase):
    """ testing Electric Source units. """

    def test_power_source(self):
        from lms2.electric.sources import PowerSource
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet
        from pyomo.dae.plugins.finitedifference import TransformationFactory
        import pandas as pd

        m = LModel(name='model')
        t = Time('00:00:00', '00:00:10', freq='5s')
        m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))
        flow = pd.Series({0.0: 0.0, 10: 5})
        m.ps = PowerSource(time=m.t, profile=flow, flow_name='p')

        discretizer = TransformationFactory('dae.finite_difference')
        discretizer.apply_to(m, wrt=m.t, nfe=10, scheme='BACKWARD')  # BACKWARD or FORWARD

        self.assertEqual(m.ps.p.get_values(), {0.0: 0.0, 10.0: 5.0, 1.0: 0.5, 2.0: 1.0,
                                               3.0: 1.5, 4.0: 2.0, 5.0: 2.5, 6.0: 3.0,
                                               7.0: 3.5, 8.0: 4.0, 9.0: 4.5})

        new_flow = pd.Series({0.0: 0.0, 10: 20})
        m.del_component('ps')
        m.ps = PowerSource(time=m.t, profile=new_flow, flow_name='p')

        self.assertEqual(m.ps.p.get_values(), {0.0: 0.0, 1.0: 2.0, 2.0: 4.0, 3.0: 6.0,
                                               4.0: 8.0, 5.0: 10.0, 6.0: 12.0, 7.0: 14.0,
                                               8.0: 16.0, 9.0: 18.0, 10.0: 20.0})

        self.assertEqual(m.ps.p.sens, 'out')
        self.assertEqual(m.ps.p.port_type, 'flow')


class MainGridTest(unittest.TestCase):
    """ testing Main Grid Units. """

    def test_MainGrid(self):
        from lms2.electric.maingrids import MainGrid
        from lms2.electric.sources import PowerSource
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet
        from pyomo.dae.plugins.finitedifference import TransformationFactory
        import pandas as pd

        m = LModel(name='model')
        t = Time('00:00:00', '00:00:10', freq='1s')
        m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))
        t.nfe = int(t.delta/t.dt)

        cin = pd.Series({0.0: 0.0, 10: 5})
        cout = pd.Series({0.0: 1.0, 10: 6})

        m.mg = MainGrid(time=m.t, cin=cin, cout=cout, pmax=20000, pmin=2000)

        source = pd.Series({0.0: 0.0, 3: -10, 5: 1,  8: -10, 10: 5})
        m.ps = PowerSource(time=m.t, profile=source, flow_name='p')

        m.connect_flux(m.mg.p, m.ps.p)

        discretizer = TransformationFactory('dae.finite_difference')
        discretizer.apply_to(m, wrt=m.t, nfe=10, scheme='BACKWARD')  # BACKWARD or FORWARD

        self.assertEqual(m.mg.cin.extract_values(), {0.0: 0.0, 1.0: 0.5, 2.0: 1.0,
                                                     3.0: 1.5, 4.0: 2.0, 5.0: 2.5,
                                                     6.0: 3.0, 7.0: 3.5, 8.0: 4.0,
                                                     9.0: 4.5, 10.0: 5.0})
        self.assertEqual(m.mg.cout.extract_values(), {0.0: 1.0, 1.0: 1.5, 2.0: 2.0,
                                                      3.0: 2.5, 4.0: 3.0, 5.0: 3.5,
                                                      6.0: 4.0, 7.0: 4.5, 8.0: 5.0,
                                                      9.0: 5.5, 10.0: 6.0})

        m.obj = m.construct_objective_from_expression_list(m.t, m.mg.instant_cost)

        opt = SolverFactory('glpk')
        results = opt.solve(m)

        self.assertEqual(m.obj(), 0.040208333333333325)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)


if __name__ == '__main__':
    unittest.main()
