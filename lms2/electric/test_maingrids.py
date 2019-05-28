from unittest import TestCase

UB = 10e6


data_main_grid_v0 = {
                    'time': {None: [0, 2]},
                    'cost': {None: 0.15}
                    }


data_main_grid_v1 = {
                    'time':     {None: [0, 2]},
                    'pmax':     {None: 10000000.0},
                    'pmin':     {None: -10000000.0},
                    'cost':     {None: 0.15},
                    'cost_in':  {None: 0.15},
                    'cost_out': {None: 0.15}
                    }


class TestAbsMainGridV0(TestCase):

    def test_mgv0(self):

        from lms2 import AbsMainGridV0
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 1))
        m.mg = AbsMainGridV0()

        UB = 1e6

        data = \
            {None:
                {
                    'time'  : {None: [0, 10]},
                    'mg'    : data_main_grid_v0
                }
            }

        print(data_main_grid_v1)

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.mg, 'outlet'))
        self.assertIsInstance(m.mg.outlet, Port)


class TestAbsMainGridV1(TestCase):

    def test_mgv1(self):

        from lms2 import AbsMainGridV1
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 1))
        m.mg = AbsMainGridV1()

        UB = 1e6

        data = \
            {None:
                {
                    'time'  : {None: [0, 10]},
                    'mg'    : data_main_grid_v1
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.mg, 'outlet'))
        self.assertIsInstance(m.mg.outlet, Port)
