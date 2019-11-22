from lms2.base.base_units import *

import unittest


class BaseUnitsTests(unittest.TestCase):

    def test_source_unit(self):
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet
        from pyomo.dae.plugins.finitedifference import TransformationFactory
        import pandas as pd

        m = LModel(name='model')
        t = Time('00:00:00', '00:00:10', freq='5s')
        m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))
        flow = pd.Series({0.0: 0.0, 10: 5})
        m.fs = SourceUnit(time=m.t, flow=flow, flow_name='flow')

        TransformationFactory('dae.finite_difference').apply_to(m, wrt=m.t, nfe=10, scheme='BACKWARD')
        # BACKWARD or FORWARD

        self.assertEqual(m.fs.flow.get_values(), {0.0: 0.0, 10.0: 5.0, 1.0: 0.5, 2.0: 1.0,
                                                  3.0: 1.5, 4.0: 2.0, 5.0: 2.5, 6.0: 3.0,
                                                  7.0: 3.5, 8.0: 4.0, 9.0: 4.5})

    def test_flow_source(self):
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.environ import SolverFactory, Objective
        from pyomo.network import Arc
        from pyomo.dae.contset import ContinuousSet
        from pyomo.dae.plugins.finitedifference import TransformationFactory
        import pandas as pd

        m = LModel(name='model')
        t = Time('00:00:00', '00:00:10', freq='5s')
        m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))
        flow = pd.Series({0.0: 0.0, 10: 5})
        load = pd.Series({0.0: 0.0, 10: 5})

        m.fs = FlowSource(time=m.t, profile=flow, flow_name='p')
        m.fl = FlowLoad(time=m.t, profile=load, flow_name='p')
        m.arc = Arc(source=m.fs.outlet, dest=m.fl.inlet)

        def _obj(model):
            return 0
        m.obj = Objective(rule=_obj)

        TransformationFactory('dae.finite_difference').apply_to(m, wrt=m.t, nfe=10, scheme='BACKWARD')
        # BACKWARD or FORWARD
        TransformationFactory("network.expand_arcs").apply_to(m)

        self.assertEqual(m.fs.p.get_values(), {0.0: 0.0, 10.0: 5.0, 1.0: 0.5, 2.0: 1.0,
                                               3.0: 1.5, 4.0: 2.0, 5.0: 2.5, 6.0: 3.0,
                                               7.0: 3.5, 8.0: 4.0, 9.0: 4.5})

        self.assertEqual(m.fl.p.get_values(), {0.0: 0.0, 10.0: 5.0, 1.0: 0.5, 2.0: 1.0,
                                               3.0: 1.5, 4.0: 2.0, 5.0: 2.5, 6.0: 3.0,
                                               7.0: 3.5, 8.0: 4.0, 9.0: 4.5})

        opt = SolverFactory('glpk')
        results = opt.solve(m)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

    def test_flow_source_param(self):
        from lms2.core.models import LModel
        from lms2.core.time import Time

        from pyomo.dae.contset import ContinuousSet
        from pyomo.dae.plugins.finitedifference import TransformationFactory
        import pandas as pd

        m = LModel(name='model')
        t = Time('00:00:00', '00:00:10', freq='5s')
        m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))
        flow = pd.Series({0.0: 0.0, 10: 5})
        m.fs = SourceUnitParam(time=m.t, flow=flow, flow_name='p')

        discretizer = TransformationFactory('dae.finite_difference')
        discretizer.apply_to(m, wrt=m.t, nfe=10, scheme='BACKWARD')  # BACKWARD or FORWARD

        self.assertEqual(m.fs.p.extract_values(), {0.0: 0.0, 10.0: 5.0, 1.0: 0.5, 2.0: 1.0,
                                                   3.0: 1.5, 4.0: 2.0, 5.0: 2.5, 6.0: 3.0,
                                                   7.0: 3.5, 8.0: 4.0, 9.0: 4.5})

    def test_abs(self):
        from lms2.core.models import LModel
        from lms2.core.time import Time
        from lms2.base.base_units import Abs

        from pyomo.environ import SolverFactory, Objective
        from pyomo.network import Arc
        from pyomo.dae.contset import ContinuousSet
        from pyomo.dae.plugins.finitedifference import TransformationFactory
        import pandas as pd

        m = LModel(name='model')
        t = Time('00:00:00', '00:01:00', freq='5s')
        m.t = ContinuousSet(bounds=(t.timeSteps[0], t.timeSteps[-1]))

        # source
        flow = pd.Series({0.0: 0.0, 30: -10, 60: 5})
        m.fs = EffortSource(time=m.t, effort=flow, effort_name='e')

        # bloc absolute value
        m.abs = Abs(time=m.t, xmax=1000, xmin=-1000)

        # connection
        m.arc = Arc(source=m.fs.outlet, dest=m.abs.e_inlet)

        def _obj(model):
            return 0
        m.obj = Objective(rule=_obj)

        discretizer = TransformationFactory('dae.finite_difference')
        discretizer.apply_to(m, wrt=m.t, nfe=10, scheme='BACKWARD')  # BACKWARD or FORWARD
        TransformationFactory("network.expand_arcs").apply_to(m)

        opt = SolverFactory('glpk')
        results = opt.solve(m)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

        self.assertEqual(m.abs.s1.extract_values(), {0.0: 0.0, 60.0: 5.0, 36.0: 0.0,
                                                     6.0: 0.0, 42.0: 0.0, 12.0: 0.0,
                                                     48.0: 0.0, 18.0: 0.0, 54.0: 2.0,
                                                     24.0: 0.0, 30.0: 0.0})
        self.assertEqual(m.abs.s2.extract_values(), {0.0: 0.0, 60.0: 0.0, 36.0: 7.0,
                                                     6.0: 2.0, 42.0: 4.0, 12.0: 4.0,
                                                     48.0: 1.0, 18.0: 6.0, 54.0: 0.0,
                                                     24.0: 8.0, 30.0: 10.0})


if __name__ == '__main__':
    unittest.main()
