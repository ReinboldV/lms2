import unittest


class TestBattery(unittest.TestCase):

    def test_instanciate_battery_v0(self):
        from lms2 import BatteryV0
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 1))
        m.b = BatteryV0()

        UB = 1e6

        data_batt = dict(
            time={None: [0, 15]},
            socmin={None: None},
            socmax={None: None},
            soc0={None: None},
            socf={None: None},
            dpcmax={None: UB},
            dpdmax={None: UB},
            emin={None: 0},
            emax={None: 500},
            pcmax={None: UB},
            pdmax={None: UB},
            e0={None: 0},
            ef={None: 50},
            etac={None: 1.0},
            etad={None: 1.0})

        data = \
            {None:
                {
                    'time': {None: [0, 10]},
                    'b': data_batt
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.b, 'outlet'))
        self.assertIsInstance(m.b.outlet, Port)

        self.assertTrue(hasattr(m.b, 'emin'))
        self.assertTrue(hasattr(m.b, 'emax'))
        self.assertTrue(hasattr(m.b, 'e0'))
        self.assertTrue(hasattr(m.b, 'ef'))
        self.assertTrue(hasattr(m.b, 'etac'))
        self.assertTrue(hasattr(m.b, 'etad'))
        self.assertTrue(hasattr(m.b, 'dpdmax'))
        self.assertTrue(hasattr(m.b, 'dpcmax'))
        self.assertTrue(hasattr(m.b, 'pcmax'))
        self.assertTrue(hasattr(m.b, 'pdmax'))

        self.assertIsInstance(m.b.emin, Param)
        self.assertIsInstance(m.b.emax, Param)
        self.assertIsInstance(m.b.e0, Param)
        self.assertIsInstance(m.b.ef, Param)
        self.assertIsInstance(m.b.etac, Param)
        self.assertIsInstance(m.b.etad, Param)
        self.assertIsInstance(m.b.dpdmax, Param)
        self.assertIsInstance(m.b.dpcmax, Param)
        self.assertIsInstance(m.b.pcmax, Param)
        self.assertIsInstance(m.b.pdmax, Param)

        self.assertTrue(hasattr(m.b, 'e'))
        self.assertTrue(hasattr(m.b, 'de'))
        self.assertTrue(hasattr(m.b, 'p'))
        self.assertTrue(hasattr(m.b, 'dp'))

        self.assertIsInstance(m.b.e, Var)
        self.assertIsInstance(m.b.de, Var)
        self.assertIsInstance(m.b.p, Var)
        self.assertIsInstance(m.b.dp, Var)

    def test_battery_v0(self):
        from lms2 import BatteryV0, AbsPowerLoad, FixedPowerLoad, AbsLModel
        from pyomo.environ import TransformationFactory, SolverFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Arc

        m = AbsLModel()
        m.time = ContinuousSet()
        m.b = BatteryV0()
        m.pl = FixedPowerLoad()
        m.ps = AbsPowerLoad()
        m.arc1 = Arc(source=m.b.outlet, dest=m.pl.inlet)
        m.arc2 = Arc(source=m.b.outlet, dest=m.ps.inlet)

        data_batt = dict(
            time={None: [0, 10]},
            dpcmax={None: 100000},
            dpdmax={None: 100000},
            emin={None: 0},
            emax={None: 500},
            pcmax={None: 80},
            pdmax={None: 80},
            e0={None: 50},
            ef={None: None},
            etac={None: 1.0},
            etad={None: 1.0})

        data_pl = {
            'time': {None: [0, 10]},
            'profile_index': {None: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            'profile_value': dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [10, 0, -10, -90, -20, 20, 30, 40, 40, 10]))
        }

        data_ps = {
            'time': {None: (0, 10)}
        }

        data = \
            {None:
                {
                    'time': {None: [0, 10]},
                    'b': data_batt,
                    'pl': data_pl,
                    'ps': data_ps
                }
            }

        inst = m.create_instance(data)

        from lms2.economic.cost import def_absolute_cost
        from pyomo.environ import Objective
        from pyomo.dae import Integral

        inst.ps.instant_cost = def_absolute_cost(inst.ps, var_name='p')
        inst.new_int = Integral(inst.time, wrt=inst.time, rule=lambda b, t: b.ps.instant_cost[t])

        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=5)
        TransformationFactory("network.expand_arcs").apply_to(inst)

        inst.obj = Objective(expr=inst.new_int)

        opt = SolverFactory("glpk")

        from time import time

        t1 = time()
        results = opt.solve(inst, tee=False)
        print(f'Solve time : {time() - t1:0.4f} s')

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

    def test_battery_v1(self):
        from lms2 import BatteryV1, AbsPowerLoad, FixedPowerLoad, AbsLModel
        from pyomo.environ import TransformationFactory, SolverFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Arc

        m = AbsLModel()
        m.time = ContinuousSet()
        m.b = BatteryV1()
        m.pl = FixedPowerLoad()
        m.ps = AbsPowerLoad()
        m.arc1 = Arc(source=m.b.outlet, dest=m.pl.inlet)
        m.arc2 = Arc(source=m.b.outlet, dest=m.ps.inlet)

        data_batt = dict(
            time={None: [0, 10]},
            dpcmax={None: 100},
            dpdmax={None: 100},
            socmin={None: 10},
            socmax={None: 51},
            soc0={None: 50},
            socf={None: 51},
            emin={None: 0},
            emax={None: 2},
            pcmax={None: 80},
            pdmax={None: 80},
            etac={None: 1.0},
            etad={None: 1.0})

        data_pl = {
            'time': {None: [0, 10]},
            'profile_index': {None: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            'profile_value': dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [0, 0, -10, -80, 10, 20, 30, 40, 40, 10]))
        }

        data_ps = {
            'time': {None: (0, 10)}
        }

        data = {None: {
            'time': {None: [0, 10]},
            'b': data_batt,
            'pl': data_pl,
            'ps': data_ps
        }
        }

        inst = m.create_instance(data)

        from lms2.economic.cost import def_absolute_cost
        from pyomo.environ import Objective
        from pyomo.dae import Integral

        inst.ps.instant_cost = def_absolute_cost(inst.ps, var_name='p')
        inst.new_int = Integral(inst.time, wrt=inst.time, rule=lambda b, t: b.ps.instant_cost[t])

        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=5)
        TransformationFactory("network.expand_arcs").apply_to(inst)

        inst.obj = Objective(expr=inst.new_int)

        opt = SolverFactory("glpk")

        from time import time

        t1 = time()
        results = opt.solve(inst, tee=False)
        print(f'Solve time : {time() - t1:0.4f} s')

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)

    def test_battery_v2(self):
        from lms2 import AbsBatteryV2, AbsPowerLoad, FixedPowerLoad, AbsLModel
        from pyomo.environ import TransformationFactory, SolverFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Arc

        m = AbsLModel()
        m.time = ContinuousSet()
        m.b = AbsBatteryV2()
        m.pl = FixedPowerLoad()
        m.ps = AbsPowerLoad()
        m.arc1 = Arc(source=m.b.outlet, dest=m.pl.inlet)
        m.arc2 = Arc(source=m.b.outlet, dest=m.ps.inlet)

        data_batt = dict(
            time={None: [0, 10]},
            dpcmax={None: 100},
            dpdmax={None: 100},
            socmin={None: 10},
            socmax={None: 55},
            soc0={None: 50},
            socf={None: None},
            emin={None: 0},
            emax={None: 10},
            pcmax={None: 80},
            pdmax={None: 80},
            etac={None: 1.0},
            etad={None: 1.0})

        data_pl = {
            'time': {None: [0, 10]},
            'profile_index': {None: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            'profile_value': dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [0, 0, -10, -40, -10, 20, 30, 40, 40, 10]))
        }

        data_ps = {
            'time': {None: (0, 10)}
        }

        data = {None: {
            'time': {None: [0, 10]},
            'b': data_batt,
            'pl': data_pl,
            'ps': data_ps
        }
        }

        inst = m.create_instance(data)

        from lms2.economic.cost import def_absolute_cost
        from pyomo.environ import Objective
        from pyomo.dae import Integral

        inst.ps.instant_cost = def_absolute_cost(inst.ps, var_name='p')
        inst.new_int = Integral(inst.time, wrt=inst.time, rule=lambda b, t: b.ps.instant_cost[t])

        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=5)
        TransformationFactory("network.expand_arcs").apply_to(inst)

        inst.obj = Objective(expr=inst.new_int)

        opt = SolverFactory("glpk")

        from time import time

        t1 = time()
        results = opt.solve(inst, tee=False)
        print(f'Solve time : {time() - t1:0.4f} s')

        from pyomo.opt import SolverStatus, TerminationCondition
        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)


if __name__ == '__main__':
    unittest.main()
