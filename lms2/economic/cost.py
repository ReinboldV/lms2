"""
This module contains Economic blocks.
"""
from lms2 import DynUnit
from lms2.base.base_units import set_profile
from pyomo.environ import Param, Var, Expression, NonNegativeReals, PositiveReals, Constraint
from pyomo.network import Port
from pandas import Series

__all__ = ['def_linear_cost',       'def_bilinear_cost',    'def_bilinear_dynamic_cost',
           'PiecewiseLinearCost',   'SimpleCost',           '_OnePortEconomicUnit']


def def_linear_cost(m, var_name='p'):
    """
    Method for adding a linear constant cost associated to variable 'p', to a block
    Final instantaneous cost expression is called "instant_cost"

    :param m: Block
    :param str var_name: Names of the expensive variable
    :return: pyomo Expression
    """

    m.cost = Param(initialize=0, mutable=True, doc=f'simple linear cost, associated with variable {var_name}, (euros/kWh)')

    def _instant_cost(m, t):
        return m.find_component(var_name)[t] * m.cost / 3600

    return Expression(m.time, rule=_instant_cost,
                      doc=f'instantaneous linear cost (euros/s), associated with variable {var_name}')


def def_absolute_cost(m, var_name='p'):
    """
    Method for adding absolute cost, i.e. a bilinear cost of coefficient -1 and +1 associated with variable 'p'.
    Final instantaneous cost expression is called "instant_cost"

    :param m: Block
    :param var_name: Names of the expensive variable
    :return: pyomo Expression
    """

    m.abs_p = Var(m.time, within=NonNegativeReals)
    m.cost  = Param(default=1, mutable=True,within=PositiveReals,
                    doc=f'cost associated to the absolute value of {var_name} (euros/kWh)')

    def _bound1(m, t):
        return m.abs_p[t] >= -m.cost*m.find_component(var_name)[t]

    def _bound2(m, t):
        return m.abs_p[t] >=  m.cost*m.find_component(var_name)[t]

    def _instant_cost(m, t):
        return m.abs_p[t] * m.cost / 3600

    m._cost_bound1 = Constraint(m.time, rule=_bound1)
    m._cost_bound2 = Constraint(m.time, rule=_bound2)

    return Expression(m.time, rule=_instant_cost,
                      doc=f'instantaneous bilinear cost (euros/s), associated with variable {var_name}')


def def_bilinear_cost(bl, var_in='p_in', var_out='p_out'):
    """
    Method for adding bilinear cost to a block associated to variables 'var_in', 'var_out'.

    Names of costs are 'cost_in' 'cost_out' and are not tunable for the moment.
    Final instantaneous cost expression is called "instant_cost"

    :param bl: Block
    :param str var_in: Name of the input variable
    :param str var_out: Name of the input variable
    :return: pyomo Expression
    """
    bl.cost_in  = Param(default=0, mutable=True, doc=f'buying cost of variable {var_in} (euro/kWh)')
    bl.cost_out = Param(default=0, mutable=True, doc=f'selling cost of variable {var_out} (euro/kWh)')

    def _instant_cost(m, t):
        return (m.find_component(var_out)[t] * m.cost_out - m.find_component(var_in)[t] * m.cost_in)/3600

    return Expression(bl.time, rule=_instant_cost,
                      doc=f'instantaneous bilinear cost (euros/s), associated with variable {var_in} and {var_out}')


def def_bilinear_dynamic_cost(bl, var_in='p_in', var_out='p_out'):
    """
    Method for adding bilinear dynamic cost to a block associated to variables 'var_in', 'var_out'.

    Names of costs are 'cost_in' 'cost_out' and are not tunable for the moment.
    Final instantaneous cost expression is called "instant_cost"

    :param bl: Block
    :param str var_in: Name of the input variable
    :param str var_out: Name of the input variable
    :return: Expression
    """

    # bl.cost_in  = Param(bl.time, default=0, mutable=True,
    #                     doc=f'buying cost of variable {var_in} with respect to time')
    # bl.cost_out = Param(bl.time, default=0, mutable=True,
    #                     doc=f'selling cost of variable {var_out} with respect to time')

    from lms2.base.base_units import fix_profile

    fix_profile(bl, flow_name='cost_in',  index_name='cost_in_index',  profile_name='cost_in_value')
    fix_profile(bl, flow_name='cost_out', index_name='cost_out_index', profile_name='cost_out_value')

    def _instant_cost(m, t):
        return (m.find_component(var_out)[t] * m.cost_out[t] - m.find_component(var_in)[t] * m.cost_in[t])/3600

    return Expression(bl.time, rule=_instant_cost,
                      doc=f'instantaneous bilinear and dynamic cost, associated with variable {var_in} and {var_out}')


class _OnePortEconomicUnit(DynUnit):
    """
    Dynamic Economical Unit that is exposing one Economic Port
    """

    def __init__(self, *args, time=None, **kwds):

        super(_OnePortEconomicUnit, self).__init__(*args, time=time, **kwds)
        self.v_in   = Var(time)
        self.inlet  = Port(initialize={'f': (self.v_in, Port.Conservative)})


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
                self.cost = Param(initialize=cost, doc='Cost of energy (euro/kWh)', mutable=True)
            elif isinstance(cost, Series):
                _init_input, _set_bounds = set_profile(profile=cost, kind=kind, fill_value=fill_value)
                self.cost = Param(time, initialize=_init_input, default=_init_input, doc='buying cost of energy (euro/kWh)',
                                 mutable=True)
            else:
                self.cost = Param(initialize=0, doc='Cost of energy is null', mutable=False)

        # Definition of the instant objectives to be integrated over the time
        if self.cost.is_indexed():
            def _instant_cost(m, t):
                return (m.v_in[t] * m.cost[t]) / 3600
        else :
            def _instant_cost(m, t):
                return (m.v_in[t] * m.cost) / 3600

        self.instant_cost = Expression(time, rule=_instant_cost, doc='instantaneous cost in euros/s')


class PiecewiseLinearCost(_OnePortEconomicUnit):
    """
    Economic Unit that computes a Piecewise Linear cost.

    See :class:`pyomo.core.base.piecewise.Piecewise` for keywords optional arguments.

    """
    def __init__(self, pw_pts, f_rule, *args, time=None, pw_constr_type='LB', pw_repn='SOS2', **kwds):
        """

        :param pw_pts: list, tuple or dictionary of piecewise breaking points
        :param f_rule: rule, list, tuple for dictionary
        :param args:
        :param time: time index Set
        :param pw_constr_type: Indicates the bound type of the piecewise function.
        :param pw_repn: Indicates the type of piecewise representation to use.
        :param kwds: See :class:`pyomo.core.base.piecewise.Piecewise` for keywords optional arguments.
        """
        super(PiecewiseLinearCost, self).__init__(*args, time=time, **kwds)

        from pyomo.core.base.piecewise import Piecewise

        assert isinstance(pw_pts, (list, dict, tuple)), f'"cost" must be an instance of list, tuple or dictionary,' \
                                                      f' but actually is : {pw_pts, type(pw_pts)}'

        self.dcost = Var(time)
        del self.v_in
        del self.inlet
        self.v_in = Var(time, bounds=(min(pw_pts), max(pw_pts)))
        self.inlet = Port(initialize={'f': (self.v_in, Port.Conservative)})

        self.piecewise = Piecewise(time, self.dcost, self.v_in,
                                   f_rule=f_rule,
                                   pw_pts=pw_pts,
                                   pw_repn=pw_repn,
                                   pw_constr_type=pw_constr_type)

        def _instant_cost(m, t):
            return m.dcost[t] / 3600

        self.instant_cost = Expression(time, rule=_instant_cost, doc='instantaneous cost in euros/s')
