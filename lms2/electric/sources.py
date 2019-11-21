# -*- coding: utf-8 -*-
"""
Electrical sources and loads
"""

from pyomo.environ import PositiveReals, Constraint, Binary

from lms2 import AbsFlowSource, AbsFixedFlowSource, AbsFlowLoad, AbsFixedFlowLoad

__all__ = ['AbsPowerSource', 'AbsFixedPowerSource', 'AbsScalablePowerSource',
           'AbsPowerLoad', 'AbsFixedPowerLoad', 'AbsScalablePowerLoad',
           'AbsProgrammableLoad', 'AbsDebugSource', 'PVPanels']


# TODO unittest
class AbsPowerSource(AbsFlowSource):
    """ Simple Power Source.

    Exposes a power output port.
    """

    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)


# TODO unittest
class AbsFixedPowerSource(AbsFixedFlowSource):
    """
    Abstract Fixed Power Source Unit.

    Abstract Power Source Unit who's power output is fixed using a given index set and indexed profile.
    """

    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)


# TODO unittest
class AbsScalablePowerSource(AbsFixedPowerSource):
    """ Scalable Power Source

    May be used for sizing sources, such as PV panel, wind turbines, etc."""

    def __init__(self, *args, flow_name='p', scale_fact='scale_fact', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)

        scaled_flow_name = flow_name + '_scaled'

        # self.scale_fact = Var(initialize=1, within=PositiveReals, doc='scaling factor within Positve reals')
        self.add_component(scale_fact, Var(initialize=1,
                                           within=PositiveReals,
                                           doc='scaling factor within Positve reals'))
        self.add_component(scaled_flow_name, Var(self.time, doc='Scaled source flow'))

        def _flow_scaling(m, t):
            # return m.find_component(scaled_flow_name)[t] == m.scale_fact*m.find_component(flow_name)[t]
            return m.find_component(scaled_flow_name)[t] == m.find_component(scale_fact) * m.find_component(flow_name)[
                t]

        def _debug_flow_scaling(m, t):
            # return -0.000001, \
            #        m.find_component(scaled_flow_name)[t] - m.scale_fact * m.find_component(flow_name)[t],\
            #        0.000001
            return -0.000001, \
                   m.find_component(scaled_flow_name)[t] - m.find_component(scale_fact) * m.find_component(flow_name)[
                       t], \
                   0.000001

        self.flow_scaling = Constraint(self.time, rule=_flow_scaling,
                                       doc='Constraint equality for flow scaling')
        self.debug_flow_scaling = Constraint(self.time, rule=_debug_flow_scaling,
                                             doc='Constraint equality for flow scaling')

        self.del_component('outlet')
        self.outlet = Port(initialize={'f': (self.component(scaled_flow_name), Port.Conservative)})


class PVPanels(AbsScalablePowerSource):
    """
    Scalable PV panel module.

    Derives from a Abstract scalable power source.
    """

    def __init__(self):
        super().__init__(flow_name='p', scale_fact='surf')


# TODO unittest
class AbsPowerLoad(AbsFlowLoad):
    """ Simple Power Load."""

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param args:
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, flow_name=flow_name, **kwds)


# TODO unittest
class AbsFixedPowerLoad(AbsFixedFlowLoad):
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
class AbsScalablePowerLoad(AbsFixedPowerLoad):
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

        self.scaled_inlet = Port(initialize={'f': (self.component(scaled_flow_name), Port.Conservative)})


# TODO unittest
class AbsProgrammableLoad(AbsPowerSource):
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


class AbsDebugSource(AbsPowerSource):
    """
    Debug Power source.

    Consist of an unbounded power source to force convergence.
    It is associated to an expensive (positive) cost function.
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
    m.prog = AbsProgrammableLoad()
    m.b = AbsDebugSource()
