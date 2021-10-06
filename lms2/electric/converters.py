# -*- coding: utf-8 -*-
"""
Electrical converters
"""

from pyomo.environ import Var, Param, Constraint, units as u
from pyomo.core import NonNegativeReals
from pyomo.network import Port
from pyomo.dae import ContinuousSet

__all__ = ['converter_simple']


def converter_simple(b, **kwargs):
    """
    Simple Unidirectional converter.

    outlet and inlet and outputs are power ports.
    """
    b._unit_support = True

    time = kwargs.pop('time')

    def eta_val(m, value):
        return 0 < value <= 1

    def noneornonnegativereal(m, value):
        return (value is None) or value >= 0

    b.eta = Param(default=1, validate=eta_val, mutable=True, doc='efficiency of the converter (within (0,1))')
    b.pmax = Param(default=None, validate=noneornonnegativereal, mutable=True, units=u.watt)

    b.p_in = Var(time, within=NonNegativeReals, units=u.watt)
    b.p_out = Var(time, within=NonNegativeReals, units=u.watt)

    @b.Constraint(time)
    def _pmax(m, t):
        if m.pmax.value is None:
            return Constraint.Skip
        return m.p_out[t] <= m.pmax

    @b.Constraint(time)
    def efficiency(m, t):
        return m.p_out[t] == m.eta * m.p_in[t]

    b.inlet = Port(initialize={'f': (b.p_in, Port.Extensive, {'include_splitfrac': False})}) #: inlet
    b.outlet = Port(initialize={'f': (b.p_out, Port.Extensive, {'include_splitfrac': False})}) #: oulte

    return b

