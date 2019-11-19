from unittest import TestCase


class TestAbsPowerSource(TestCase):
    pass


class TestAbsFixedPowerSource(TestCase):
    pass


class TestAbsScalablePowerSource(TestCase):
    pass


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
        from lms2 import AbsProgrammableLoad, AbsDebugSource
        from pyomo.environ import AbstractModel, TransformationFactory, Param, Var
        from pyomo.dae import ContinuousSet
        import pandas as pd

        m = AbstractModel()
        m.time = ContinuousSet(bounds=(0, 1))
        m.prog = AbsProgrammableLoad()

        UB = 1e6

        df = pd.Series({0:0, 1:1, 2:2, 3:1, 4:0})

        data_prog = {
            'time': {None: [0, 10]},
            'w1'  : {None: 3},
            'w2'  : {None: 8},
            'window': {None: [2, 8]},
            'profile_index': {None: df.index},
            'profile_value':df.to_dict()}

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
        inst.pprint()

if __name__ == '__main__':
    import unittest
    unittest.main()
