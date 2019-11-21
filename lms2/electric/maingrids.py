# -*- coding: utf-8 -*-
"""
Distribution Grid Units

Electrical connection to the distribution grid.

"""
from pandas import Series
from pyomo.environ import Constraint, Var, Param, Block, Expression
from pyomo.environ import NonNegativeReals, Binary
from pyomo.network import Port

from lms2 import AbsDynUnit, AbsPowerSource, def_bilinear_cost, def_linear_cost, def_bilinear_dynamic_cost

__all__ = ['AbsMainGridV0', 'AbsMainGridV1', 'AbsMainGridV2']

UB = 10e6


def def_pin_pout(m):
    # This could be better implemented.
    # In particular, it should not use m.p directly but m.find_component(name_var)

    """
    Defines power 'in' and 'out' variables

    :param m:
    :return:
    """

    assert isinstance(m, Block), f"argument 'm', must be an instance of Block, but is actually {type(m)}."
    assert hasattr(m, 'p'), f"model m does not have attribute named 'p'. This is needed. "

    m.pmax = Param(initialize=UB, mutable=True, doc='maximal power out (kW)')
    m.pmin = Param(initialize=UB, mutable=True, doc='maximal power in (kW)')

    m.pout = Var(m.time, doc='power to the main grid', within=NonNegativeReals, initialize=None)
    m.pin = Var(m.time, doc='power from the main grid', within=NonNegativeReals, initialize=None)
    m.u = Var(m.time, doc='binary variable', within=Binary, initialize=None)

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


class AbsMainGridV0(AbsPowerSource):
    """
    Simple MainGrid Unit.

    One Power port (named 'p' by default) associated with a simple cost (named 'cost').
    (Source convention)

    Variables:
        - p           Supplied power from the maingrid (source convention)

    Param:
        - cost        simple linear cost, associated with variable p

    Ports:
        - outlet

    Expressions:
        - inst_cost  instantaneous linear cost, associated with variable p
    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)
        self.instant_cost = def_linear_cost(self, var_name=flow_name)
        self.component(flow_name).doc = 'Supplied power from the maingrid (source convention)'


class AbsMainGridV1(AbsPowerSource):
    """
    Main Grid Unit.

    Consists of a power source with limits (pmin, pmax),
    associated with a bilinear cost (selling and buying cost, i.e. c_in and c_out).
    A binary variable 'u' is declared to tackle the price discontinuity at p=0.
    (Source convention)

    Variables:
        - p           None
        - pout        power to the main grid
        - pin         power from the main grid
        - u           binary variable

    Param:
        - pmax        maximal power out (kW)
        - pmin        maximal power in (kW)
        - cost_in     buying cost of variable pin
        - cost_out    selling cost of variable pout

    Constraints:
        - _pmin       Low bound
        - _pmax       Up bound
        - _p_balance  Power balance

    Ports:
        - outlet      None

    Expressions:
        - inst_cost  instantaneous bilinear cost, associated with variable pin and pout

    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)

        def_pin_pout(self)

        self.instant_cost = def_bilinear_cost(self, var_in='pin', var_out='pout')


class AbsMainGridV2(AbsPowerSource):
    """
    Main Grid Unit v2.

    Consists of a power source with limits (pmin, pmax),
    associated with a bilinear cost with respect to time (selling and buying cost, i.e. c_in and c_out).
    A binary variable 'u' is declared to tackle the price discontinuity at p=0.
    (Source convention)

    Sets:
        - cost_in_index    None
        - cost_out_index   None

    Variables:
        - p                None
        - pout             power to the main grid
        - pin              power from the main grid
        - u                binary variable

    Param:
        - pmax             maximal power out (kW)
        - pmin             maximal power in (kW)
        - cost_in_value    None
        - cost_in          None
        - cost_out_value   None
        - cost_out         None

    Constraints:
        - _pmin            Low bound
        - _pmax            Up bound
        - _p_balance       Power balance

    Ports:
        - outlet           None

    Expressions:
        - inst_cost     instantaneous bilinear and dynamic cost, associated with variable pin and pout
    """

    def __init__(self, *args, flow_name='p', **kwgs):
        super().__init__(*args, flow_name=flow_name, **kwgs)

        def_pin_pout(self)

        self.inst_cost = def_bilinear_dynamic_cost(self, var_in='pin', var_out='pout')


class AbsMainGrid_old(AbsDynUnit):
    """
    DEPRECIATED 
    Simple main Grid unit
    """

    def __init__(self, *args, pmax=None, pmin=None, cout=None, cin=None, mixco2=None, kind='linear',
                 fill_value='extrapolate', **kwgs):
        """

        :param time: Contiunous Time Set
        :param pmax: maximal power (kW)
        :param pmin: minimal power (kW)
        :param cout: selling cost (euro/kWh)
        :param cin: buying cost (euro/kWh)
        :param mix: CO2 mix of energy (eqCO2/kWh)
        :param kind: default : 'linear'
        :param fill_value: default : 'extrapolate'
        :param kwgs:
        """
        from lms2.base.base_units import set_profile

        super().__init__(*args, **kwgs)

        # Definition of the Variables

        self.pout = Var(self.time, doc='power to the main grid', within=NonNegativeReals, initialize=0)
        self.pin = Var(self.time, doc='power from the main grid', within=NonNegativeReals, initialize=0)
        self.u = Var(self.time, doc='binary variable', within=Binary, initialize=0)
        self.p = Var(self.time, doc='power from the main grid to the microgrid', initialize=0)

        # Defintion of the Ports

        self.outlet = Port(initialize={'f': (self.p, Port.Conservative)})

        # Definition of parametres and constraints

        def _energy_balance(m, t):
            return m.p[t] == m.pout[t] - m.pin[t]

        self._energy_balance = Constraint(self.time, rule=_energy_balance)

        if pmin is not None:
            self.pmin = Param(initialize=pmin, mutable=True, doc='maximal power out')

        if pmax is not None:
            self.pmax = Param(initialize=pmax, mutable=True, doc='maximal power in')

        def _pmax(m, t):
            if pmax is None:
                return Constraint.Skip
            return m.pin[t] - m.u[t] * m.pmax <= 0

        self._pmax = Constraint(self.time, rule=_pmax)

        def _pmin(m, t):
            if pmin is None:
                return Constraint.Skip
            return m.pout[t] + m.u[t] * m.pmin <= m.pmin

        self._pmin = Constraint(self.time, rule=_pmin)

        # if cin is initialized with a float, the cost is considered fixed during the time horizon,
        # otherwise, if cin is a pandas.series, the cost is considered varibale during the time, horizon, and
        # it is interpolated
        if cin is not None:
            if isinstance(cin, float) or isinstance(cin, int):
                self.cin = Param(initialize=cin, doc='buying cost of energy', mutable=True)
            elif isinstance(cin, Series):
                _init_input, _set_bounds = set_profile(profile=cin, kind=kind, fill_value=fill_value)
                self.cin = Param(self.time, initialize=_init_input, default=_init_input, doc='buying cost of energy',
                                 mutable=True)
            else:
                self.cin = Param(initialize=0, doc='buying cost of energy is null', mutable=False)

        # same behaviour than cin
        if cout is not None:
            if isinstance(cout, float) or isinstance(cout, int):
                self.cout = Param(initialize=cout, doc='selling cost of energy', mutable=True)
            elif isinstance(cout, Series):
                _init_input, _set_bounds = set_profile(profile=cout, kind=kind, fill_value=fill_value)
                self.cout = Param(self.time, initialize=_init_input, default=_init_input, doc='selling cost of energy',
                                  mutable=True)
            else:
                self.cout = Param(initialize=0, doc='selling cost of energy is null', mutable=False)

        # same behaviour than cin
        if mixco2 is not None:
            if isinstance(mixco2, float) or isinstance(mixco2, int):
                self.mixCO2 = Param(initialize=mixco2, doc='mass of co2 emitted (gram per kilowatt hour)', mutable=True)
            elif isinstance(mixco2, Series):
                _init_input, _set_bounds = set_profile(profile=mixco2, kind=kind, fill_value=fill_value)
                self.mixCO2 = Param(self.time, initialize=_init_input, default=_init_input,
                                    doc='mass of co2 emitted (gram per kilowatt hour)', mutable=True)
            else:
                raise (NotImplementedError())

            if self.mixCO2.is_indexed():
                def _instant_co2(m, t):
                    return m.pout[t] * m.mixCO2[t] / 3600
            else:
                def _instant_co2(m, t):
                    return m.pout[t] * m.mixCO2 / 3600

            self.instant_co2 = Expression(self.time, rule=_instant_co2, doc='instantaneous CO2 emission in g/s')
            self.instant_co2.tag = 'CO2'

        # Definition of the instant objectives to be integrated over the time in the upper model
        if self.cin.is_indexed() & self.cout.is_indexed():
            def _instant_cost(m, t):
                return (-m.pin[t] * m.cin[t] + m.pout[t] * m.cout[t]) / 3600
        elif (not self.cin.is_indexed()) & (not self.cout.is_indexed()):
            def _instant_cost(m, t):
                return (-m.pin[t] * m.cin + m.pout[t] * m.cout) / 3600
        else:
            raise (NotImplementedError())

        def _instant_energy(m, t):
            return m.pin[t] / 3600

        def _instant_pro(m, t):
            return (m.pin[t] + m.pout[t]) / 3600

        self.instant_energy = Expression(self.time, rule=_instant_energy,
                                         doc='instantaneous used energy in kW.h/s (only from the main grid)')

        self.instant_pro = Expression(self.time, rule=_instant_pro,
                                      doc='instantaneous used energy in kW.h/s (absolute value from and to the '
                                          'main grid)')

        self.instant_cost = Expression(self.time, rule=_instant_cost, doc='instantaneous cost of use in euros/s')
