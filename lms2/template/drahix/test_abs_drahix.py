import unittest


class DrahiXTest(unittest.TestCase):
    """
    unitest.testCase for the DrahiX microgrid.
    """

    def setUp(self):

        from lms2 import AbsDrahiX_v1
        from lms2.template.drahix.abs_drahix_tools import get_drahix_data

        kwargs = {
            't_start'   : '2018-06-01 00:00:00',
            't_end'     : '2018-06-02 00:00:00',
            'freq'      : '15Min'
        }

        df, self.t = get_drahix_data(**kwargs)
        self.drx = AbsDrahiX_v1()

        data_batt = {'time'         : {None: [df.index[0], df.index[-1]]},
                     'socmin'       : {None: 10},
                     'socmax'       : {None: 95},
                     'soc0'         : {None: 50},
                     'socf'         : {None: None},
                     'dpcmax'       : {None: 10},
                     'dpdmax'       : {None: 10},
                     'emin'         : {None: 0},
                     'emax'         : {None: 100},
                     'pcmax'        : {None: 10.0},
                     'pdmax'        : {None: 10.0},
                     'etac'         : {None: 0.9},
                     'etad'         : {None: 0.9}}

        data_mg = {
                    'time'          : {None: [df.index[0], df.index[-1]]},
                    'pmax'          : {None: 10},
                    'pmin'          : {None: 10},
                    'cost_in'       : {None: 0.10/3600},
                    'cost_out'      : {None: 0.15/3600}
        }

        data_ps = {
                    'time'          : {None: [df.index[0], df.index[-1]]},
                    'profile_index' : {None: df.index},
                    'profile_value' : df['P_pv'].to_dict()
        }

        data_pl = {
                    'time'          : {None: [df.index[0], df.index[-1]]},
                    'profile_index' : {None: df.index},
                    'profile_value' : df['P_load'].to_dict()
        }

        self.data = {None:
                   {
                    'time'          : {None: [df.index[0], df.index[-1]]},
                    'batt'          : data_batt,
                    'mg'            : data_mg,
                    'ps'            : data_ps,
                    'pl'            : data_pl
                   }
        }

    def test_1(self):
        from pyomo.environ import TransformationFactory, SolverFactory
        from lms2 import AbsLModel

        inst = self.drx.create_instance(self.data)

        inst.obj = AbsLModel.construct_objective_from_expression_list(inst, inst.time, inst.mg.instant_cost)
        inst.ps.flow_scaling.deactivate()

        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=self.t.nfe)
        TransformationFactory("network.expand_arcs").apply_to(inst)

        opt = SolverFactory("gurobi", solver_io="direct")
        results = opt.solve(inst, tee=False)

        self.assertAlmostEqual(inst.obj(), -8.2632719323)

    def test_2(self):
        from pyomo.environ import TransformationFactory, SolverFactory
        from lms2 import AbsLModel

        self.data[None]['batt']['socf'][None] = 50

        inst = self.drx.create_instance(self.data)

        inst.obj = AbsLModel.construct_objective_from_expression_list(inst, inst.time, inst.mg.instant_cost)
        inst.ps.flow_scaling.deactivate()

        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=self.t.nfe)
        TransformationFactory("network.expand_arcs").apply_to(inst)

        opt = SolverFactory("gurobi", solver_io="direct")
        results = opt.solve(inst, tee=False)

        self.assertAlmostEqual(inst.obj(), -4.4339135893)


if __name__ == '__main__':
    unittest.main()
