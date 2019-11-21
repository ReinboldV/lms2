# -*- coding: utf-8 -*-
"""
Electrical converters
"""

from pyomo.environ import Var, Param, NonNegativeReals, Constraint
from pyomo.network import Port

from lms2 import AbsDynUnit

__all__ = ['SimpleConverter']


class SimpleConverter(AbsDynUnit):
    """
    Simple Unidirectional converter.

    Inputs and outputs are powers ports.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def eta_val(m, value):
            return 0 < value <= 1

        def noneornonnegativereal(m, value):
            return (value is None) or value >= 0

        self.eta = Param(default=1, validate=eta_val, mutable=True, doc='efficiency of the converter (within (0,1))')
        self.pmax = Param(default=None, validate=noneornonnegativereal, mutable=True)

        self.p_in = Var(self.time, within=NonNegativeReals)
        self.p_out = Var(self.time, within=NonNegativeReals)

        @self.Constraint(self.time)
        def _pmax(m, t):
            if m.pmax.value is None:
                return Constraint.Skip
            return m.p_out[t] <= m.pmax

        @self.Constraint(self.time)
        def efficiency(m, t):
            return m.p_out[t] == m.eta * m.p_in[t]

        self.inlet = Port(initialize={'f': (self.p_in, Port.Conservative)})
        self.outlet = Port(initialize={'f': (self.p_out, Port.Conservative)})


if __name__ == "__main__":
    from lms2 import AbsLModel
    from pyomo.dae import ContinuousSet

    m = AbsLModel(name='test')
    m.time = ContinuousSet
    m.b = SimpleConverter()

    data_conv = {
        'time': {None: (0, 1)},
        'pmax': {None: -10},
        'eta': {None: 1}}

    data = {None: dict(time={None: [0, 1]},
                       b=data_conv)}

    inst = m.create_instance(data)
    inst.pprint()
