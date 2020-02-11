# -*- coding: utf-8 -*-
"""
Electrical sources and loads
"""
from networkx.algorithms import flow
from pyomo.environ import PositiveReals, Constraint, Var, Param, NonNegativeReals
from pyomo.network import Port

from lms2 import FlowSource, FixedFlowSource, FlowLoad, FixedFlowLoad

__all__ = ['PowerSource', 'FixedPowerSource', 'ScalablePowerSource',
           'PowerLoad', 'FixedPowerLoad', 'ScalablePowerLoad',
           'ProgrammableLoad', 'DebugSource', 'PVPanels']


# TODO unittest
class PowerSource(FlowSource):
    """ Simple Power Source.

    Exposes a power output port.

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
    Ports           Documentation
    =============== ===================================================================
    outlet          Power output port, using source convention (kW)
    =============== ===================================================================

    """

    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, doc_flow='Power output flow (kW)', **kwds)

        self.outlet.doc = 'Power output port, using source convention (kW)'


# TODO unittest
class FixedPowerSource(FixedFlowSource):
    """
    Abstract Fixed Power Source Unit.

    Abstract Power Source Unit who's power output is fixed using a given index set and indexed profile.

    =============== ===================================================================
    Sets            Documentation
    =============== ===================================================================
    profile_index   profile index
    =============== ===================================================================
    =============== ===================================================================
    ContinuousSets  Documentation
    =============== ===================================================================
    time            Time continuous set (s)
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    profile_value   profile value
    p               new profile, indexed by time
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          output flow source using source convention
    =============== ===================================================================

    """

    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)


# TODO unittest
class ScalablePowerSource(FixedPowerSource):
    """ Scalable Power Source

    May be used for sizing sources, such as PV panel, wind turbines, etc.

    =============== ===================================================================
    Sets            Documentation
    =============== ===================================================================
    profile_index   profile index
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p_scaled        Scaled output flow (kW)
    scale_fact      scaling factor within Positve reals (1)
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    profile_value   profile value
    p               new profile, indexed by time
    fact_min        factor lower bound
    fact_max        factor upper bound
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    _scale_fact_bounds optional bound constraint for the scaling factor.
    _flow_scaling   Constraint equality for flow scaling
    _debug_flow_scaling Debug constraint equality for flow scaling
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          output power using source convention
    =============== ===================================================================


    """

    def __init__(self, *args, flow_name='p', scale_fact='scale_fact', curtailable=False, **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)

        scaled_flow_name = flow_name + '_scaled'
        self.fact_min = Param(default=None, mutable=True, doc='factor lower bound')
        self.fact_max = Param(default=None, mutable=True, doc='factor upper bound')

        self.add_component(scaled_flow_name, Var(self.time, doc='Scaled output flow (kW)', initialize=0))

        self.add_component(scale_fact, Var(initialize=1,
                                           within=PositiveReals,
                                           doc='scaling factor within Positve reals (1)'))

        @self.Constraint(self.time, doc='optional bound constraint for the scaling factor.')
        def _scale_fact_bounds(m, t):
            if (m.fact_max.value is None) and (m.fact_min.value is None):
                return Constraint.Skip
            else:
                return m.fact_min, m.find_component(scale_fact), m.fact_max

        if curtailable:
            # creation of a new positive variable, that should be smaller than the production scale_fact*p
            self.p_curt = Var(self.time, within=NonNegativeReals, doc='curtailed flow (kW)')

            @self.Constraint(self.time, doc='Constraint equality for flow scaling')
            def _flow_scaling(m, t):
                return m.find_component(scaled_flow_name)[t] + m.p_curt[t] == \
                       m.find_component(scale_fact) * m.find_component(flow_name)[t]

            @self.Constraint(self.time, doc='Curtailment must be smaller than production')
            def _curt_up_bound(m, t):
                return 0, m.find_component(scaled_flow_name)[t], None

        else:
            @self.Constraint(self.time, doc='Constraint equality for flow scaling')
            def _flow_scaling(m, t):
                return m.find_component(scaled_flow_name)[t] == \
                       m.find_component(scale_fact) * m.find_component(flow_name)[t]

            @self.Constraint(self.time, doc='Debug constraint equality for flow scaling')
            def _debug_flow_scaling(m, t):
                return -0.000001, m.find_component(scaled_flow_name)[t] - \
                       m.find_component(scale_fact) * m.find_component(flow_name)[t], 0.000001

        self.del_component('outlet')
        self.outlet = Port(initialize={'f': (self.component(scaled_flow_name),
                                             Port.Extensive,
                                             {'include_splitfrac': False})}, doc='output power using source convention')


class PVPanels(ScalablePowerSource):
    """
    Scalable PV panel module.

    Derives from a Abstract scalable power source.

    =============== ===================================================================
    Sets            Documentation
    =============== ===================================================================
    profile_index   profile index
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p_scaled        Scaled output flow (kW)
    surf            scaling factor within Positve reals (1)
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    profile_value   profile value
    p               new profile, indexed by time
    fact_min        factor lower bound
    fact_max        factor upper bound
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    _scale_fact_bounds optional bound constraint for the scaling factor.
    _flow_scaling   Constraint equality for flow scaling
    _debug_flow_scaling Debug constraint equality for flow scaling
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          output power using source convention
    =============== ===================================================================
    """

    def __init__(self, **kwds):
        super().__init__(flow_name='p', scale_fact='surf', **kwds)


# TODO unittest
class PowerLoad(FlowLoad):
    """ Simple Power Load."""

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param args:
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, flow_name=flow_name, **kwds)


# TODO unittest
class FixedPowerLoad(FixedFlowLoad):
    """
    Abstract Fixed Power Source Unit.

    Abstract Power Source Unit who's power output is fixed using a given index set and indexed profile.
    """

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param args:
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, flow_name=flow_name, **kwds)


# TODO unittest
class ScalablePowerLoad(FixedPowerLoad):
    """ Scalable Power Load

    May be used for sizing load."""

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param args:
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, flow_name=flow_name, **kwds)

        scaled_flow_name = flow_name + '_scaled'

        self.scale_fact = Var(initialize=1, within=PositiveReals, doc='scaling factor within Positve reals')
        self.add_component(scaled_flow_name, Var(self.time, doc='Scaled source flow'))

        def _flow_scaling(m, t):
            return m.scale_fact * m.find_component(scaled_flow_name)[t] == m.find_component(flow_name)[t]

        def _debug_flow_scaling(m, t):
            return -0.000001, \
                   m.scale_fact * m.find_component(scaled_flow_name)[t] - m.find_component(flow_name)[t], \
                   0.000001

        self.flow_scaling = Constraint(self.time, rule=_flow_scaling,
                                       doc='Constraint equality for flow scaling')
        self.debug_flow_scaling = Constraint(self.time, rule=_debug_flow_scaling,
                                             doc='Constraint equality for flow scaling')

        self.scaled_inlet = Port(initialize={'f': (self.component(scaled_flow_name), Port.Extensive, {'include_splitfrac': False})})


# TODO unittest
class ProgrammableLoad(PowerSource):
    """
    Programmable Load with fixed input profile.

    This load can be programmed to be on at a free moment within t_1 andd t_2, when turning 'on', the load is consuming
    the profile power. Ex : Washing machine.
    """

    def __init__(self, *args, flow_name='p', **kwds):

        from lms2 import fix_profile
        from pyomo.core.base.sets import SimpleSet
        from pyomo.environ import Binary, Param, Var

        super().__init__(*args, flow_name=flow_name, **kwds)

        def _bound_u(m, t):
            if m.window.bounds()[0] <= t <= m.window.bounds()[-1]:
                return 0, 1
            else:
                return 0, 0

        fix_profile(self, flow_name='pp', profile_name='profile_value', index_name='profile_index')

        self.w1 = Param()
        self.w2 = Param()
        self.window = SimpleSet(doc='time window where load can be turned ON.')

        self.u = Var(self.time, bounds=_bound_u, within=Binary,
                     doc='binary, equals to 1 when the load is turned ON, 0 otherwise.')

        def _turned_on(m):
            return sum([m.u[t] for t in m.time]) == 1

        def _bound_p(m, t):
            if m.window.bounds()[0] <= t <= m.window.bounds()[-1]:
                return Constraint.Skip
            else:
                return 0, m.p[t], 0

        self._turned_on = Constraint(rule=_turned_on, doc='the load is turned on only once')
        self._bounds_p = Constraint(self.time, rule=_bound_p, doc='the load is contraint to be off '
                                                                  'outside the time range')

    def compile(self):
        def _delay(m, t):
            if t >= max(m.profile_index):
                return m.p[t] == sum([m.u[t - i] * m.profile_value[i] for i in m.profile_index])
            else:
                return Constraint.Skip

        self._delay = Constraint(self.time, rule=_delay, doc='the load follow the profile')


class DebugSource(PowerSource):
    """
    Debug Power source.

    Consist of an unbounded power source to force convergence.
    It is associated to an expensive (positive) cost function.

    =============== ===================================================================
    ContinuousSets  Documentation
    =============== ===================================================================
    time            Time continuous set (s)
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               Power output flow (kW)
    abs_p           Absolute value of variable p
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    p_cost          cost associated to the absolute value of p (euros/kWh)
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    _bound1         absolute value constraint 2
    _bound2         absolute value constraint 1
    =============== ===================================================================
    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          Power output port, using source convention (kW)
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    _instant_cost   instantaneous bilinear cost (euros/s), associated with variable p
    =============== ===================================================================


    """

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param str flow_name: name of the variable to be weighted


        """
        super().__init__(*args, flow_name=flow_name, **kwds)

        from lms2 import def_absolute_cost

        self.inst_cost = def_absolute_cost(self, var_name='p')


if __name__ == '__main__':
    from pyomo.environ import AbstractModel, Param, Var
    from pyomo.dae import ContinuousSet
    from pyomo.network import Port

    m = AbstractModel()
    m.time = ContinuousSet(bounds=(0, 1))
    m.prog = ProgrammableLoad()
    m.b = DebugSource()
