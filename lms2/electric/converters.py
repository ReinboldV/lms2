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

    This block consider unidirectional input/output power flows and an efficiency.

    .. math::
        0 &\\leq p_{in}(t) \\\\
        0 &\leq p_{out}(t) \\leq p_{max} \\\\
        \eta &\\in \\left[0, 1\\right] \\\\
        p_{out}(t) &= \\eta \\times p_{in}(t)

    .. table::
        :width: 100%

        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p_in            input power, >=0 (default unit : kW)
        p_out           output power, >=0 (default unit : kW)
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        eta             efficiency of the converter (within (0,1))
        pmax            maximal output power (default unit : kW)
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _pmax           p_out upper bound
        efficiency      relation between p_in and p_out
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        inlet           inlet port for p_in extensive flow
        outlet          inlet port for p_out extensive flow
        =============== ===================================================================

    """
    b._unit_support = True
    eta = kwargs.pop('eta', 1)
    units = kwargs.pop('units', 'kwatt')
    time = kwargs.pop('time')

    def eta_val(m, value):
        return 0 < value <= 1

    def noneornonnegativereal(m, value):
        return (value is None) or value >= 0

    b.eta = Param(default=eta, validate=eta_val, mutable=True, doc='efficiency of the converter (within (0,1))')
    b.pmax = Param(default=None, validate=noneornonnegativereal,
                   mutable=True, units=units, doc='maximal output power (default unit : kW)')

    b.p_in = Var(time, within=NonNegativeReals, units=units, doc='input power, >=0 (default unit : kW)')
    b.p_out = Var(time, within=NonNegativeReals, units=units, doc='output power, >=0 (default unit : kW)')

    @b.Constraint(time, doc='p_out upper bound')
    def _pmax(m, t):
        if m.pmax.value is None:
            return Constraint.Skip
        return m.p_out[t] <= m.pmax

    @b.Constraint(time, doc='relation between p_in and p_out')
    def efficiency(m, t):
        return m.p_out[t] == m.eta * m.p_in[t]

    b.inlet = Port(initialize={'f': (b.p_in, Port.Extensive, {'include_splitfrac': False})},
                   doc='inlet port for p_in extensive flow')
    b.outlet = Port(initialize={'f': (b.p_out, Port.Extensive, {'include_splitfrac': False})},
                    doc='inlet port for p_out extensive flow')

    return b

