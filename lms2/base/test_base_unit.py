from unittest import TestCase


class TestAbsDynUnit(TestCase):

    def test_abs(self):
        from lms2 import AbsDynUnit
        from pyomo.environ import AbstractModel, TransformationFactory
        from pyomo.dae import ContinuousSet

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsDynUnit()

        data_absdyn = dict(
            time={None: [0, 15]})

        data = \
            {None:
                {
                    'time'  : {None: [0, 15]},
                    'u'     : data_absdyn
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=1)
        self.assertEqual(inst.u.time.data(), {0, 15})
        self.assertEqual(inst.time.data(), {0, 15})


class TestAbsFlowSource(TestCase):

    def test_abs(self):
        from lms2 import AbsFlowSource
        from pyomo.environ import AbstractModel, TransformationFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsFlowSource(flow_name='p')

        data_unit = dict(
            time={None: [0, 15]})

        data = \
            {None:
                {
                    'time': {None: [0, 15]},
                    'u'   : data_unit
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=1)

        self.assertTrue(hasattr(m.u, 'p'))
        self.assertTrue(hasattr(m.u, 'outlet'))
        self.assertIsInstance(m.u.outlet, Port)

        self.assertEqual(inst.u.time.data(), {0, 15})
        self.assertEqual(inst.time.data(), {0, 15})


class TestFixVariable(TestCase):

    def test_fix_profile(self):
        from lms2 import AbsFlowSource, fix_profile
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Set
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsFlowSource(flow_name='p')

        fix_profile(m.u, flow_name='p', profile_name='pro', index_name='ind')

        data_unit = {
            'time': {None: (0, 15)},
            'ind': {None: [0, 10, 15]},
            'pro': dict(zip([0, 10, 15], [10, 11, 12]))}

        data = \
            {None:
                {
                    'time': {None: [0, 15]},
                    'u': data_unit
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertTrue(hasattr(m.u, 'p'))
        self.assertTrue(hasattr(m.u, 'outlet'))
        self.assertIsInstance(m.u.outlet, Port)

        self.assertTrue(hasattr(m.u, 'ind'))
        self.assertTrue(hasattr(m.u, 'pro'))
        self.assertIsInstance(m.u.pro, Param)
        self.assertIsInstance(m.u.ind, Set)

        self.assertEqual(inst.u.time.data(), {0, 15, 7.5})
        self.assertEqual(inst.time.data(), {0, 15, 7.5})


class TestAbsFlowLoad(TestCase):

    def test_abs(self):
        from lms2 import AbsFlowLoad
        from pyomo.environ import AbstractModel, TransformationFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsFlowLoad(flow_name='p')

        data_unit = dict(
            time={None: [0, 15]})

        data = \
            {None:
                {
                    'time': {None: [0, 15]},
                    'u': data_unit
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=1)

        self.assertTrue(hasattr(m.u, 'p'))
        self.assertTrue(hasattr(m.u, 'inlet'))
        self.assertIsInstance(m.u.inlet, Port)

        self.assertEqual(inst.u.time.data(), {0, 15})
        self.assertEqual(inst.time.data(), {0, 15})


class TestAbsEffortSource(TestCase):

    def test_abs(self):
        from lms2 import AbsEffortSource
        from pyomo.environ import AbstractModel, TransformationFactory
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsEffortSource(effort_name='e')

        data_unit = dict(
            time={None: [0, 15]})

        data = \
            {None:
                {
                    'time': {None: [0, 15]},
                    'u': data_unit
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=1)

        self.assertTrue(hasattr(m.u, 'e'))
        self.assertTrue(hasattr(m.u, 'outlet'))
        self.assertIsInstance(m.u.outlet, Port)

        self.assertEqual(inst.u.time.data(), {0, 15})
        self.assertEqual(inst.time.data(), {0, 15})


class TestAbsFixedFlowSource(TestCase):

    def test_abs(self):
        from lms2 import AbsFixedFlowSource
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Set
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsFixedFlowSource(flow_name='p')

        self.assertTrue(hasattr(m.u, 'p'))
        self.assertTrue(hasattr(m.u, 'profile_index'))
        self.assertTrue(hasattr(m.u, 'profile_value'))
        self.assertIsInstance(m.u.profile_value, Param)
        self.assertIsInstance(m.u.profile_index, Set)
        self.assertTrue(hasattr(m.u, 'outlet'))
        self.assertIsInstance(m.u.outlet, Port)

        data_source = \
            {
                'time': {None: (0, 15)},
                'profile_index': {None: [0, 10, 15]},
                'profile_value': dict(zip([0, 10, 15], [10, 11, 12]))
            }

        data = \
            {None:
                {
                    'time': {None: [0, 15]},
                    'u': data_source
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertEqual(inst.u.time.data(), {0, 7.5, 15})
        self.assertEqual(inst.time.data(), {0, 7.5, 15})
        self.assertEqual(inst.u.p.extract_values(), {0: 10.0, 7.5: 10.75 , 15: 12.0})


class TestAbsFixedFlowLoad(TestCase):
    def test_abs(self):
        from lms2 import AbsFixedFlowLoad
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Set
        from pyomo.dae import ContinuousSet
        from pyomo.network import Port

        m = AbstractModel()
        m.time = ContinuousSet()
        m.u = AbsFixedFlowLoad(flow_name='p')

        self.assertTrue(hasattr(m.u, 'p'))
        self.assertTrue(hasattr(m.u, 'profile_index'))
        self.assertTrue(hasattr(m.u, 'profile_value'))
        self.assertIsInstance(m.u.profile_value, Param)
        self.assertIsInstance(m.u.profile_index, Set)
        self.assertTrue(hasattr(m.u, 'inlet'))
        self.assertIsInstance(m.u.inlet, Port)

        data_source = \
            {
                'time': {None: (0, 15)},
                'profile_index': {None: [0, 10, 15]},
                'profile_value': dict(zip([0, 10, 15], [10, 11, 12]))
            }

        data = \
            {None:
                {
                    'time': {None: [0, 15]},
                    'u': data_source
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=2)

        self.assertEqual(inst.u.time.data(), {0, 7.5, 15})
        self.assertEqual(inst.time.data(), {0, 7.5, 15})
        self.assertEqual(inst.u.p.extract_values(), {0: 10.0, 7.5: 10.75, 15: 12.0})


if __name__ == '__main__':
    import unittest
    unittest.main()
