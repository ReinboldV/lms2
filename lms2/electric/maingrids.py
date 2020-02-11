# -*- coding: utf-8 -*-
"""
Distribution Grid Units

Electrical connection to the distribution grid.

"""
from pandas import Series
from pyomo.environ import Constraint, Var, Param, Block, Expression
from pyomo.environ import NonNegativeReals, Binary
from pyomo.network import Port

from lms2 import DynUnit, PowerSource, def_bilinear_cost, def_linear_cost, def_bilinear_dynamic_cost, def_linear_dyn_cost

__all__ = ['MainGridV0', 'MainGridV1', 'MainGridV2', 'MainGridV3']

UB = 10e6


def def_pin_pout(m):
    # This could be better implemented.
    # In particular, it should not use m.p directly but m.find_component(name_var)

    """
    Defines power flow variables 'in' and 'out'

    :param m:
    :return:
    """

    assert isinstance(m, Block), f"argument 'm', must be an instance of Block, but is actually {type(m)}."
    assert hasattr(m, 'p'), f"model m does not have attribute named 'p'. This is needed. "

    m.pmax = Param(initialize=UB, mutable=True, doc='maximal power out (kW)')
    m.pmin = Param(initialize=UB, mutable=True, doc='maximal power in (kW)')

    m.pout = Var(m.time, doc='power to the main grid', within=NonNegativeReals, initialize=0)
    m.pin = Var(m.time, doc='power from the main grid', within=NonNegativeReals, initialize=0)
    m.u = Var(m.time, doc='binary variable', within=Binary, initialize=0)

    def _power_balance(b, t):
        return b.p[t] - b.pout[t] + b.pin[t] == 0

    def _pmax(b, t):
        if b.pmax.value is None:
            return Constraint.Skip
        return b.pout[t] - b.u[t] * b.pmax <= 0

    def _pmin(b, t):
        if b.pmin.value is None:
            return Constraint.Skip
        return b.pin[t] + b.u[t] * b.pmin <= b.pmin

    m._pmin = Constraint(m.time, rule=_pmin, doc='low bound')
    m._pmax = Constraint(m.time, rule=_pmax, doc='up bound')
    m._p_balance = Constraint(m.time, rule=_power_balance, doc='power balance')


class MainGridV0(PowerSource):
    """
    Simple MainGrid Unit.

    One Power port (named 'p' by default) associated with a simple cost (named 'cost').
    (Source convention)

    =============== ===================================================================
    ContinuousSets  Documentation
    =============== ===================================================================
    time            Time continuous set (s)
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               Supplied power from the maingrid (source convention)
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    cost            simple linear cost, associated with variable p, (euros/kWh)
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          Power output port, using source convention (kW)
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    instant_cost    instantaneous linear cost (euros/s), associated with variable p
    =============== ===================================================================

    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)
        self.instant_cost = def_linear_cost(self, var_name=flow_name)
        self.component(flow_name).doc = 'Supplied power from the maingrid (source convention)'


class MainGridV1(PowerSource):
    """
    Main Grid Unit.

    Consists of a power source with limits (pmin, pmax),
    associated with a bilinear cost (selling and buying cost, i.e. c_in and c_out).
    A binary variable 'u' is declared to tackle the price discontinuity at p=0.
    (Source convention)

    =============== ===================================================================
    ContinuousSets  Documentation
    =============== ===================================================================
    time            Time continuous set (s)
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               Power output flow (kW)
    pout            power to the main grid
    pin             power from the main grid
    u               binary variable
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    pmax            maximal power out (kW)
    pmin            maximal power in (kW)
    cost_in         buying cost of variable pin (euro/kWh)
    cost_out        selling cost of variable pout (euro/kWh)
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    _pmin           low bound
    _pmax           up bound
    _p_balance      power balance
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          Power output port, using source convention (kW)
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    instant_cost    instantaneous bilinear cost (euros/s), associated with variable pin and pout
    =============== ===================================================================

    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)

        def_pin_pout(self)

        self.instant_cost = def_bilinear_cost(self, var_in='pin', var_out='pout')


class MainGridV2(PowerSource):
    """
    Main Grid Unit v2.

    Consists of a power source with limits (pmin, pmax),
    associated with a bilinear cost with respect to time (selling and buying cost, i.e. c_in and c_out).
    A binary variable 'u' is declared to tackle the price discontinuity at p=0.
    (Source convention)

    =============== ===================================================================
    Sets            Documentation
    =============== ===================================================================
    cost_in_index   index for the dynamic cost related to variable pin
    cost_out_index  index for the dynamic cost related to variable pout
    =============== ===================================================================
    =============== ===================================================================
    ContinuousSets  Documentation
    =============== ===================================================================
    time            Time continuous set (s)
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               Power output flow (kW)
    pout            power to the main grid
    pin             power from the main grid
    u               binary variable
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    pmax            maximal power out (kW)
    pmin            maximal power in (kW)
    cost_in_value   values for dynamic cost related to variable pin
    cost_in         new profile, indexed by time
    cost_out_value  values for dynamic cost related to variable pout
    cost_out        new profile, indexed by time
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    _pmin           low bound
    _pmax           up bound
    _p_balance      power balance
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          Power output port, using source convention (kW)
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    inst_cost       instantaneous bilinear and dynamic cost, associated with variable pin and pout
    =============== ===================================================================


    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)

        def_pin_pout(self)

        self.inst_cost = def_bilinear_dynamic_cost(self, var_in='pin', var_out='pout')


class MainGridV3(PowerSource):
    """
    Main Grid Unit v3.

    Consists of a power source with limits (pmin, pmax),
    associated with a dynamic cost with respect to time (buying cost and no selling possible).
    A binary variable 'u' is declared to tackle the price discontinuity at p=0.
    (Source convention)

    =============== ===================================================================
    Sets            Documentation
    =============== ===================================================================
    cost_index      profile index
    =============== ===================================================================
    =============== ===================================================================
    ContinuousSets  Documentation
    =============== ===================================================================
    time            Time continuous set (s)
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               Power output flow (kW)
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    pmax            maximal power out (kW)
    cost_value      profile value
    cost            new profile, indexed by time
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          Power output port, using source convention (kW)
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    inst_cost       instantaneous linear cost (euros/s), associated with variable p
    =============== ===================================================================

    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)

        self.pmax = Param(initialize=UB, mutable=True, doc='maximal power out (kW)')

        self.inst_cost = def_linear_dyn_cost(self, var_name=flow_name)