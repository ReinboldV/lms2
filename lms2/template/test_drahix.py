import unittest


class DrahiXTest(unittest.TestCase):
    """
    unitest.testCase for the DrahiX microgrid.
    """

    def setUp(self):
        import pandas as pd
        from lms2 import Time

        t_start = '2018-06-01 00:00:00'
        t_end = '2018-06-01 12:00:00'
        freq = '30Min'

        self.t = Time(t_start, t_end, freq=freq)

        ppv = [0., 0., 0., 0., 0., 0., 0., 0., 0.002, 0.008, 0.011, 0.019, 0.023, 0.029, 0.031, 0.03,
               0.021, 0.037, 0.111, 0.094, 0.068, 0.065, 0.133, 0.114, 0.1]

        pload = [21.16, 20.11, 20.04, 20.25, 20.04, 22.18, 22.18, 21.61, 30., 27.7,  29.64, 28.26, 27.23, 31.45,
                 33.04, 35.62, 38.17, 41.23, 42.45, 39.9,  40.17, 38.31, 40.08, 43.11, 39.2]

        index = [0.0, 1800.0, 3600.0, 5400.0, 7200.0, 9000.0, 10800.0, 12600.0, 14400.0, 16200.0, 18000.0, 19800.0,
                 21600.0, 23400.0, 25200.0, 27000.0, 28800.0, 30600.0, 32400.0, 34200.0, 36000.0, 37800.0, 39600.0,
                 41400.0, 43200.0]

        self.df = pd.DataFrame({'P_pv': ppv, 'P_load': pload}, index=index)

    def test_DrahiX_cost(self):
        from lms2 import DrahixMicrogridV2
        from pyomo.environ import TransformationFactory, SolverFactory

        m = DrahixMicrogridV2(name='m', dataframe=self.df)
        m.mg.cin = 0.08
        m.mg.cout = 0.15

        #m.ps.scale_fact.setub(10)
        #m.ps.scale_fact.fix(50)
        # m.ps.flow_scaling.activate()
        # m.ps.debug_flow_scaling.deactivate()

        self.assertEqual(m.t.bounds(), (0, 43200))

        m.obj = m.construct_objective_from_expression_list(m.t, m.mg.instant_cost, m.ps.instant_cost)
        TransformationFactory('dae.finite_difference').apply_to(m, nfe=self.t.nfe)
        TransformationFactory("network.expand_arcs").apply_to(m)

        opt = SolverFactory("glpk")
        results = opt.solve(m, tee=False)

        self.assertEqual(m.t.value, [0.0, 1800.0, 3600.0, 5400.0, 7200.0, 9000.0, 10800.0, 12600.0, 14400.0, 16200.0,
                                     18000.0, 19800.0, 21600.0, 23400.0, 25200.0, 27000.0, 28800.0, 30600.0, 32400.0,
                                     34200.0, 36000.0, 37800.0, 39600.0, 41400.0, 43200.0])

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)
        self.assertAlmostEqual(m.obj(), 8.934914973026295, delta=1e-5)
        self.assertAlmostEqual(m.ps.scale_fact(), 752.481210526316, delta=1e-5)

    def test_DrahiX_co2(self):
        from lms2 import DrahixMicrogridV2
        from pyomo.environ import TransformationFactory, SolverFactory

        m = DrahixMicrogridV2(name='m', dataframe=self.df)
        m.mg.mixCO2 = 0.7

        assert m.t.bounds() == (0, 43200)

        m.obj = m.construct_objective_from_expression_list(m.t, m.mg.instant_co2)
        TransformationFactory('dae.finite_difference').apply_to(m, nfe=self.t.nfe)
        TransformationFactory("network.expand_arcs").apply_to(m)

        opt = SolverFactory("glpk")
        results = opt.solve(m, tee=False)

        self.assertEqual(m.t.value, [0.0, 1800.0, 3600.0, 5400.0, 7200.0, 9000.0, 10800.0, 12600.0, 14400.0, 16200.0,
                                     18000.0, 19800.0, 21600.0, 23400.0, 25200.0, 27000.0, 28800.0, 30600.0, 32400.0,
                                     34200.0, 36000.0, 37800.0, 39600.0, 41400.0, 43200.0])

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)
        self.assertAlmostEqual(m.obj(), 84.40195647763156, delta=1e-6)


if __name__ == '__main__':
    unittest.main()
