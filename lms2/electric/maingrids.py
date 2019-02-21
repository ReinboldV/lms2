# -*- coding: utf-8 -*-
"""
Contains maingrid unit, i.e. electrical connection to the distribution grid.
"""
from lms2 import Expression, DynUnit, Var, Param

from pyomo.core.base.constraint import Constraint
from pyomo.core.kernel.set_types import NonNegativeReals, Binary
from pandas import Series


class MainGrid(DynUnit):
    """
    Simple main Grid unit
    """
    def __init__(self, time, *args, pmax=None, pmin=None, cout=None, cin=None, mixco2=None, kind='linear',
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

        super().__init__(*args, time=time, **kwgs)

        # Definition of the Variables

        self.pout = Var(time, doc='power to the main grid', within=NonNegativeReals, initialize=0)
        self.pin = Var(time, doc='power from the main grid', within=NonNegativeReals, initialize=0)
        self.u = Var(time, doc='binary variable', within=Binary, initialize=0)
        self.p = Var(time, doc='power from the main grid to the microgrid', initialize=0)

        # Defintion of the Ports

        self.p.port_type = 'flow'
        self.p.sens = 'out'

        # Definition of parametres and constraints

        def _energy_balance(m, t):
            return m.p[t] == m.pout[t] - m.pin[t]
        self._energy_balance = Constraint(time, rule=_energy_balance)

        if pmin is not None:
            self.pmin = Param(initialize=pmin, mutable=True, doc='maximal power out')

        if pmax is not None:
            self.pmax = Param(initialize=pmax, mutable=True, doc='maximal power in')

        def _pmax(m, t):
            if pmax is None:
                return Constraint.Skip
            return m.pin[t] - m.u[t] * m.pmax <= 0

        self._pmax = Constraint(time, rule=_pmax)

        def _pmin(m, t):
            if pmin is None:
                return Constraint.Skip
            return m.pout[t] + m.u[t] * m.pmin <= m.pmin

        self._pmin = Constraint(time, rule=_pmin)

        # if cin is initialized with a float, the cost is considered fixed during the time horizon,
        # otherwise, if cin is a pandas.series, the cost is considered varibale during the time, horizon, and
        # it is interpolated
        if cin is not None:
            if isinstance(cin, float) or isinstance(cin, int):
                self.cin = Param(initialize=cin, doc='buying cost of energy', mutable=True)
            elif isinstance(cin, Series):
                _init_input, _set_bounds = set_profile(profile=cin, kind=kind, fill_value=fill_value)
                self.cin = Param(time, initialize=_init_input, default=_init_input, doc='buying cost of energy',
                                 mutable=True)
            else:
                self.cin = Param(initialize=0, doc='buying cost of energy is null', mutable=False)

        # same behaviour than cin
        if cout is not None:
            if isinstance(cout, float) or isinstance(cout, int):
                self.cout = Param(initialize=cout, doc='selling cost of energy', mutable=True)
            elif isinstance(cout, Series):
                _init_input, _set_bounds = set_profile(profile=cout, kind=kind, fill_value=fill_value)
                self.cout = Param(time, initialize=_init_input, default=_init_input, doc='selling cost of energy',
                                  mutable=True)
            else:
                self.cout = Param(initialize=0, doc='selling cost of energy is null', mutable=False)

        # same behaviour than cin
        if mixco2 is not None:
            if isinstance(mixco2, float) or isinstance(mixco2, int):
                self.mixCO2 = Param(initialize=mixco2, doc='mass of co2 emitted (gram) per kilowatt hour', mutable=True)
            elif isinstance(mixco2, Series):
                _init_input, _set_bounds = set_profile(profile=mixco2, kind=kind, fill_value=fill_value)
                self.mixCO2 = Param(time, initialize=_init_input, default=_init_input,
                                    doc='mass of co2 emitted (gram) per kilowatt hour', mutable=True)
            else:
                raise(NotImplementedError())

            if self.mixCO2.is_indexed():
                def _instant_co2(m, t):
                    return (- m.pin[t] + m.pout[t]) * m.mixCO2[t] / 3600
            else:
                def _instant_co2(m, t):
                    return (- m.pin[t] + m.pout[t]) * m.mixCO2 / 3600

            self.instant_co2 = Expression(time, rule=_instant_co2, doc='instantaneous CO2 emission in g/s')
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

        self.instant_energy = Expression(time, rule=_instant_energy, doc='instantaneous used energy in kW.h/s '
                                                                         '(only from the main grid)')
        self.instant_energy.tag = 'ENERGY'

        self.instant_pro = Expression(time, rule=_instant_pro, doc='instantaneous used energy in kW.h/s '
                                                                   '(absolute value from and to the main grid)')
        self.instant_pro.tag = 'PROSUMTION'

        self.instant_cost = Expression(time, rule=_instant_cost, doc='instantaneous cost of use in euros/s')
        self.instant_cost.tag = 'COST'

