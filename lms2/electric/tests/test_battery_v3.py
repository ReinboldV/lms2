import unittest


class TestBatteryV3(unittest.TestCase):

    def test_battery_v3(self):
        from lms2 import BatteryV3, FixedPowerLoad, AbsLModel, PVPanels, DebugSource, MainGridV1
        from lms2.economic.cost import absolute_cost

        from pyomo.environ import TransformationFactory, SolverFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Arc

        import numpy as np
        import pandas as pd

        m = AbsLModel()
        m.time = ContinuousSet(initialize=(0, 10))
        m.b = BatteryV3(method='piecewise')
        m.pl = FixedPowerLoad()
        m.debug = DebugSource()
        m.mg = MainGridV1()
        m.ps = PVPanels(curtailable=True)
        m.arc1 = Arc(source=m.b.outlet, dest=m.pl.inlet)
        m.arc2 = Arc(source=m.ps.outlet, dest=m.pl.inlet)
        m.arc3 = Arc(source=m.debug.outlet, dest=m.pl.inlet)
        m.arc4 = Arc(source=m.mg.outlet, dest=m.pl.inlet)

        m.b.inst_cost = absolute_cost(m.b, var_name='dp')

        t = pd.timedelta_range(start=0, end='2 days', freq='30Min').total_seconds()
        ps = [(-np.cos(2 * np.pi * i / (86400)) + 1) ** 6 / 2 ** 6 * (0.2 * np.sin(2 * np.pi * i / (86400 * 7)) + 0.4) * 10 for
              i in t]
        pl = np.array([5] * len(t))
        time = (t[0], 86400*2)
        nfe = 24*2*60/30

        data_batt = dict(
            time={None: time},
            dpcmax={None: 100},
            dpdmax={None: 100},
            socmin={None: 40},
            socmax={None: 100},
            soc0={None: 50},
            socf={None: 50},  # final soc
            socabs={None: 85},  # absorption soc
            emin={None: 40},
            emax={None: 100},
            pcmax={None: 20},
            pdmax={None: 20},
            etac={None: 0.90},
            etad={None: 0.90},
            pw_i={None: [1, 2, 3]},
            pw_j={None: [1, 2]},

            pw_soc={1: 40, 2: 85, 3: 100},
            pw_pcmax={1: 20, 2: 20, 3: 1},

            pfloat={None: 0.125},
            max_cycles={None: 10},
            cycle_passed={None: 8},
            dp_cost={None: 0})

        data_mg = {
            'time': {None: time},
            'cost_out': {None: 0.15},
            'cost_in': {None: 0},
            'pmax': {None: 30},
            'pmin': {None: 0}}

        data_pl = {
            'time': {None: time},
            'profile_index': {None: t},
            'profile_value': dict(zip(t, pl))
        }

        data_ps = {
            'time': {None: time},
            'profile_index': {None: t},
            'profile_value': dict(zip(t, ps))
        }

        data_debug = {'time': {None: time},
                      'p_cost': {None: 10}}

        data = {None: dict(time={None: time},
                           b=data_batt,
                           mg=data_mg,
                           ps=data_ps,
                           debug=data_debug,
                           pl=data_pl)}

        inst = m.create_instance(data)
        inst.ps.surf.fix(4)

        from lms2.economic.cost import absolute_cost
        from pyomo.environ import Objective
        from pyomo.dae import Integral
        from pyomo.opt import SolverStatus, TerminationCondition

        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=nfe)
        TransformationFactory("network.expand_arcs").apply_to(inst)

        inst.ps.instant_cost = absolute_cost(inst.ps, var_name='p')
        inst.new_int = Integral(inst.time, wrt=inst.time,
                                rule=lambda b, t: b.debug.inst_cost[t] + b.b.inst_cost[t] + b.mg.instant_cost[t])

        inst.b._nbr_charge.reconstruct()
        inst.obj = Objective(expr=inst.new_int)

        opt = SolverFactory("gurobi", solver_io="direct")

        results = opt.solve(inst, tee=False)

        self.assertTrue(results.solver.status == SolverStatus.ok)
        self.assertTrue(results.solver.termination_condition == TerminationCondition.optimal)
        self.assertAlmostEqual(7.8386091, inst.obj(), places=5)


if __name__ == '__main__':
    unittest.main()
