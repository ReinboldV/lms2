from unittest import TestCase


class TestAbsMainGridV0(TestCase):

    def test_mgv0(self):

        from lms2 import MainGridV0
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 10))
        m.mg = MainGridV0()

        data_main_grid_v0 = {
            'time': {None: [0, 2]},
            'cost': {None: 0.15}
        }

        data = \
            {None:
                {
                    'time'  : {None: [0, 10]},
                    'mg'    : data_main_grid_v0
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.mg, 'outlet'))
        self.assertIsInstance(m.mg.outlet, Port)


class TestAbsMainGridV1(TestCase):

    def test_mgv1(self):

        from lms2 import MainGridV1
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 10))
        m.mg = MainGridV1()

        data_main_grid_v1 = {
            'time':      {None: [0, 2]},
            'pmax':      {None: +100.0},
            'pmin':      {None: -100.0},
            'cost_in':   {None: 0.15},
            'cost_out':  {None: 0.15}}

        data = {None: {
            'time' :    {None: [0, 10]},
            'mg'   :    data_main_grid_v1}}

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.mg, 'outlet'))
        self.assertIsInstance(m.mg.outlet, Port)


class TestAbsMainGridV2(TestCase):

    def test_mgv2(self):

        from lms2 import MainGridV2
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 10))
        m.mg = MainGridV2()

        data_main_grid_v2 = {
            'time':             {None: [0, 2]},
            'pmax':             {None: +100.0},
            'pmin':             {None: -100.0},
            'cost_in_index':    {None: [0, 1, 2]},
            'cost_out_index':   {None: [0, 1, 2]},
            'cost_in_value':   dict(zip([0, 1, 2], [0.1, 0.12, 0.12])),
            'cost_out_value':  dict(zip([0, 1, 2], [0.15, 0.13, 0.13]))
        }

        data = \
            {None:
                {
                    'time': {None: [0, 10]},
                    'mg': data_main_grid_v2
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.mg, 'outlet'))
        self.assertIsInstance(m.mg.outlet, Port)
        self.assertEqual(inst.mg.cost_out.extract_values(), {0: 0.15, 1.0: 0.13, 2: 0.13})
        self.assertEqual(inst.mg.cost_in.extract_values(), {0: 0.1, 1.0: 0.12, 2: 0.12})
        self.assertEqual(inst.mg.cost_in_index.data(), (0, 1, 2))
        self.assertEqual(inst.mg.cost_out_index.data(), (0, 1, 2))


if __name__ == '__main__':
    import unittest
    unittest.main()
