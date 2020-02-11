from unittest import TestCase


class TestAbsPowerSource(TestCase):
    pass


class TestAbsFixedPowerSource(TestCase):
    pass


class TestAbsScalablePowerSource(TestCase):

    def test_instanciate_curt(self):
        from lms2 import AbsLModel
        from lms2 import ScalablePowerSource

        import pandas as pd
        from pyomo.dae import ContinuousSet
        from pyomo.environ import TransformationFactory

        m = AbsLModel()
        m.time = ContinuousSet()
        m.u    = ScalablePowerSource(curtailable=True)

        df = pd.Series({0: 0, 1: 1, 2: 2, 3: 1, 4: 0})
        data_u = {
            'time': {None: [0, 4]},
            'profile_index': {None: df.index},
            'profile_value': df.to_dict()}

        data = \
            {None:
                {
                    'time': {None: [0, 4]},
                    'u': data_u
                }
            }
        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=4)

        self.assertTrue(hasattr(inst.u, 'p_curt'))

    def test_instanciate(self):
        from lms2 import AbsLModel
        from lms2 import ScalablePowerSource

        import pandas as pd
        from pyomo.dae import ContinuousSet
        from pyomo.environ import TransformationFactory

        m = AbsLModel()
        m.time = ContinuousSet()
        m.u = ScalablePowerSource(curtailable=False)

        df = pd.Series({0: 0, 1: 1, 2: 2, 3: 1, 4: 0})
        data_u = {
            'time': {None: [0, 4]},
            'profile_index': {None: df.index},
            'profile_value': df.to_dict()}

        data = \
            {None:
                {
                    'time': {None: [0, 4]},
                    'u': data_u
                }
            }
        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=4)

        self.assertFalse(hasattr(inst.u, 'p_curt'))
        self.assertTrue(hasattr(inst.u, 'p'))
        self.assertTrue(hasattr(inst.u, 'p_scaled'))
        self.assertTrue(hasattr(inst.u, 'scale_fact'))


class TestAbsPowerLoad(TestCase):
    pass


class TestAbsFixedPowerLoad(TestCase):
    pass


class TestAbsScalablePowerLoad(TestCase):
    pass


class TestAbsDebugSource(TestCase):
    pass


class TestAbsPrommableLoad(TestCase):

    def test_instanciate_prog(self):
        from lms2 import ProgrammableLoad, DebugSource
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        import pandas as pd

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 1))
        m.prog = ProgrammableLoad()

        UB = 1e6

        df = pd.Series({0: 0, 1: 1, 2: 2, 3: 1, 4: 0})

        data_prog = {
            'time': {None: [0, 10]},
            'w1': {None: 3},
            'w2': {None: 8},
            'window': {None: [2, 8]},
            'profile_index': {None: df.index},
            'profile_value': df.to_dict()}

        data = \
            {None:
                {
                    'time': {None: [0, 10]},
                    'prog': data_prog
                }
            }

        inst = m.create_instance(data)
        TransformationFactory('dae.finite_difference').apply_to(inst, nfe=10)

        inst.prog.compile()


if __name__ == '__main__':
    import unittest

    unittest.main()
