"""
This module contains Economic blocks.
"""



# abonnement = 130 euros/y
#
#     cout   0.1580€ 	 0.1230€
#
#     cin case : sell all energy
#     ≤ 3 kwc 	18,72 €
#     ≤ 9 kwc 	15,91 €
#     ≤ 36 kwc    12,07 €
#     ≤ 100 kwc   11,19 €
#
#     cin case : autoconsumption
#     ≤ 3 kwc    prime de 400 € /kwc + vente à 10 c€/kWh)
#     ≤ 9 kwc    prime de 300 € /kwc + vente à 10 c€/kWh)
#     ≤ 36 kwc 	prime de 190 € /kwc + vente à 6 c€/kWh)
#     ≤ 100 kwc 	prime de 90 € /kwc + vente à 6 c€/kWh)
#     > 100 kwc 	0
#

from lms2 import DynUnit
from lms2.base.base_units import set_profile

from pyomo.environ import Param, Var, Expression
from pyomo.network import Port, Arc

from pandas import Series


class _OnePortEconomicUnit(DynUnit):
    """
    Dynamic Unit that is exposing one Economic Port
    """

    def __init__(self, *args, time=None, **kwds):

        super(_OnePortEconomicUnit, self).__init__(*args, time=time, **kwds)
        self.v = Var(time)
        self.inlet = Port(initialize={'v': self.v})


class SimpleCost(_OnePortEconomicUnit):
    """
    Unit that computes a Linear Economical Cost.

    For the sake of modularity, cost or other objectives functions may be computed outside of the 'physicals' units.
    This behaviour is also useful to sum up variables from different units and apply them a unique cost.

    """
    def __init__(self, *args, cost=0, time=None, kind='linear', fill_value='extrapolate', **kwds):
        """

        :param cost: float, int or Pandas.Series
        :param time: Set
        :param kind: 'linear' by default
        :param fill_value:  'extrapolate' by default
        """
        super(SimpleCost, self).__init__(*args, time=time, **kwds)

        if cost is not None:
            if isinstance(cost, float) or isinstance(cost, int):
                self.cost = Param(initialize=cost, doc='Cost of energy', mutable=True)
            elif isinstance(cost, Series):
                _init_input, _set_bounds = set_profile(profile=cost, kind=kind, fill_value=fill_value)
                self.cost = Param(time, initialize=_init_input, default=_init_input, doc='buying cost of energy',
                                 mutable=True)
            else:
                self.cost = Param(initialize=0, doc='Cost of energy is null', mutable=False)

        # Definition of the instant objectives to be integrated over the time
        if self.cost.is_indexed() & self.cout.is_indexed():
            def _instant_cost(m, t):
                return (m.v[t] * m.cost[t]) / 3600
        elif (not self.cost.is_indexed()) & (not self.cout.is_indexed()):
            def _instant_cost(m, t):
                return (m.v[t] * m.cost) / 3600
        else:
            raise (NotImplementedError())

        self.instant_cost = Expression(time, rule=_instant_cost, doc='instantaneous cost in euros/s')
        self.instant_cost.tag = 'COST'


class PiecewiseLinearCost(_OnePortEconomicUnit):
    """
    Economic Unit that computes a Piecewise Linear cost.

    See :class:`pyomo.core.base.piecewise.Piecewise` for keywords optional arguments.

    """

    def __init__(self, cost, f_rule, *args, time=None, bound='EQ', repn='SOS2', **kwds):
        """

        :param cost: list, tuple or dictionnary of piecewise breaking points
        :param f_rule: rule, list, tuple for dictionnary
        :param args:
        :param time: time index Set
        :param bound: Indicates the bound type of the piecewise function.
        :param repn: Indicates the type of piecewise representation to use.
        :param kwds: See :class:`pyomo.core.base.piecewise.Piecewise` for keywords optional arguments.
        """
        super(PiecewiseLinearCost, self).__init__(*args, time=time, **kwds)

        from pyomo.core.base.piecewise import Piecewise

        assert isinstance(cost, (list, dict, tuple)), f'"cost" must be an instance of list, tuple or dictionary,' \
                                                      f' but actually is : {cost, type(cost)}'

        self.dcost = Var(time)

        kwds = {'pw_constr_type': bound, 'pw_repn': repn, 'f_rule': f_rule}
        self.piecewise = Piecewise(time, self.dcost, self.v, kwds)

        def _instant_cost(m, t):
            return m.dcost[t] / 3600

        self.instant_cost = Expression(time, rule=_instant_cost, doc='instantaneous cost in euros/s')
        self.instant_cost.tag = 'COST'
