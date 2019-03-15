import unittest
from unittest import TestCase

from lms2 import FlowSource, LModel
from lms2.economic.cost import SimpleCost, PiecewiseLinearCost
from pyomo.environ import TransformationFactory, SolverFactory, Objective
from pyomo.network import Arc
from pandas import Series
from pyomo.dae import ContinuousSet


class TestSimpleCost(TestCase):

    def testSimpleCost(self):
        v = Series({0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 2})

        m = LModel()
        m.t = ContinuousSet(bounds=(0, 5))
        m.source = FlowSource(time=m.t, profile=v)
        m.cost = SimpleCost(time=m.t, cost=10)
        m.arc = Arc(source=m.source.outlet, dest=m.cost.inlet)

        TransformationFactory('dae.finite_difference').apply_to(m, wrt=m.t, nfe=4, scheme='BACKWARD')
        TransformationFactory("network.expand_arcs").apply_to(m)

        from six import StringIO

        os = StringIO()
        m.cost.instant_cost.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
                         """instant_cost : instantaneous cost in euros/s
    Size=5, Index=t
    Key  : Expression
       0 :    cost.cost*0.0002777777777777778*cost.v_in[0]
    1.25 : cost.cost*0.0002777777777777778*cost.v_in[1.25]
     2.5 :  cost.cost*0.0002777777777777778*cost.v_in[2.5]
    3.75 : cost.cost*0.0002777777777777778*cost.v_in[3.75]
       5 :    cost.cost*0.0002777777777777778*cost.v_in[5]
""")

    def testPiecewiseLinearCost(self):
        v = Series({0: 0, 1: 0, 2: 10, 3: 4, 4: -10, 5: -4})

        m = LModel()
        m.t = ContinuousSet(bounds=(0, 5))
        m.source = FlowSource(time=m.t, profile=v)
        m.cost = PiecewiseLinearCost(pw_pts=[-10, -5, 0, 5, 10], f_rule=[2, 1, 0, 2, 3], time=m.t, pw_constr_type='LB', pw_repn='SOS2')
        m.arc = Arc(source=m.source.outlet, dest=m.cost.inlet)

        TransformationFactory('dae.finite_difference').apply_to(m, wrt=m.t, nfe=5, scheme='BACKWARD')
        TransformationFactory("network.expand_arcs").apply_to(m)

        m.obj = m.construct_objective_from_expression_list(m.t, m.cost.instant_cost)
        opt = SolverFactory("gurobi", solver_io="direct")
        results = opt.solve(m)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

        self.assertAlmostEqual(m.obj(), 0.0019444, 6)

    def testPiecewiseLinearCost_rule(self):
        v = Series({0: 0, 1: 0, 2: 10, 3: 4, 4: -10, 5: -4})

        def rule(model, t, x):
            return 0.5 * x * x + 2

        m = LModel()
        m.t = ContinuousSet(bounds=(0, 5))
        m.source = FlowSource(time=m.t, profile=v)
        m.cost = PiecewiseLinearCost(pw_pts=[-10, -5, -1, 0, 1, 5, 10], f_rule=rule, time=m.t, pw_constr_type='LB', pw_repn='SOS2')
        m.arc = Arc(source=m.source.outlet, dest=m.cost.inlet)

        TransformationFactory('dae.finite_difference').apply_to(m, wrt=m.t, nfe=5, scheme='BACKWARD')
        TransformationFactory("network.expand_arcs").apply_to(m)

        m.obj = m.construct_objective_from_expression_list(m.t, m.cost.instant_cost)
        opt = SolverFactory("gurobi", solver_io="direct")
        results = opt.solve(m)

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

        self.assertAlmostEqual(m.obj(), 0.0345138, 6)


if __name__ == '__main__':
    unittest.main()
