# -*- coding: utf-8 -*-
"""
Basic Units, multi-physical base model
"""

from pyomo.environ import *
from pyomo.network import Port

from lms2.core.units import Unit

__all__ = ['DynUnit', 'FixedFlowLoad', 'FixedFlowSource', 'FlowSource',
           'FlowLoad', 'EffortSource', '_init_input', '_set_bounds',
           'fix_profile', 'bound_profile', 'TwoFlowUnit', ]


class DynUnit(Unit):
    def __init__(self, *args, **kwds):
        """
        Abstract Dynamic Unit

        Standard unit with time attribute to index variables and constraints.

        :param args:
        :param time:
        :param kwds:
        """
        from pyomo.dae.contset import ContinuousSet

        super().__init__(*args, **kwds)
        self.time = ContinuousSet(initialize=(0, 1), doc='Time continuous set (s)')
        self.doc = self.__doc__

    def get_constraints_values(self):
        # TODO method for retrieving constraints slack
        return

    def get_duals(self):
        # TODO method for retrieving dual variables
        return

    def pplot(self, **kwargs):
        """
        Plotting method for AbsDyn Unit.

        It iterates on the component ctype of the Block and plots it. Currently, it only works with Var,
         Constraints and Expressions.

        Example :

            >>> l, a, f = instance.block.pplot(ctype=Constraint, ncol=2)

        :param kwargs:
        :return: lines, axe and figure
        """

        from lms2.base.utils import pplot

        ctype = kwargs.pop('ctype', Var)
        active = kwargs.pop('active', True)

        lines, ax, fig = pplot(*[v for v in self.component_objects(ctype=ctype, active=active)], **kwargs)

        return lines, ax, fig


class FlowSource(DynUnit):
    """
    Abstract Flow Source Unit.

    Exposes a conservative output port for generic flow variable.
    """

    def __init__(self, *args, flow_name='flow', doc_flow='generic flow', **kwargs):
        """
        :param str doc_flow: documentation for inherited units
        :param str flow_name: name of the flow variable
        """
        super().__init__(*args, **kwargs)
        self.add_component(flow_name, Var(self.time, initialize=0, within=Reals, doc=doc_flow))
        self.outlet = Port(initialize={'f': (self.component(flow_name), Port.Extensive, {'include_splitfrac': False})},
                           doc='output flow port using source convention. ')


class FlowLoad(DynUnit):
    """
    Abstract Flow Load Unit.

    Exposes a conservative port for generic flow variable.
    Source convention is used.
    """

    def __init__(self, *args, flow_name='flow', **kwargs):
        """
        :param str flow_name: name of the flow variable
        """

        super().__init__(*args, **kwargs)
        self.add_component(flow_name, Var(self.time, initialize=0, within=Reals, doc='flow variable'))
        self.inlet = Port(initialize={'f': (self.component(flow_name), Port.Extensive, {'include_splitfrac': False})},
                          doc='Input flow inlet, using load convention')


class EffortSource(DynUnit):
    """
    Abstract Effort source unit.

    Exposes a Equality port for generic effort variable.
    """

    def __init__(self, *args, effort_name='effort', **kwargs):
        super().__init__(*args, **kwargs)
        self.add_component(effort_name, Var(self.time, initialize=0, within=Reals))
        self.outlet = Port(initialize={'e': (self.component(effort_name))})


def _init_input(m, t,
                index_name='profile_index',
                profile_name='profile_value'):
    """
    Rule for initiating variable profile using interpolation of a given profile.

    :param m: Block
    :param t: Set time
    :param index_name: name of the index set
    :param profile_name: name of the profile parameter
    :return: None
    """

    from scipy.interpolate.interpolate import interp1d

    if not hasattr(m, index_name):
        raise AttributeError(f'{m} object has no attribute {index_name}.'
                             f' Cannot proceed interpolation for initialization')
    if not hasattr(m, profile_name):
        raise AttributeError(f'{m} object has no attribute {profile_name}.'
                             f' Cannot proceed interpolation for initialization')
    if not isinstance(m.component(index_name), Set):
        raise TypeError(f'{index_name} is not a instance of Set,'
                        f' but is actually : f{type(m.component(index_name))}. Cannot proceed.')
    if not isinstance(m.component(profile_name), Param):
        raise TypeError(f'{profile_name} is not a instance of Param,'
                        f' but is actually : f{type(m.component(profile_name))}. Cannot proceed.')

    interp_x = list(m.component(index_name).value_list)
    interp_y = list(m.component(profile_name).extract_values().values())
    funct = interp1d(interp_x, interp_y, kind='linear', fill_value='extrapolate')
    b = float(funct(t))
    if b is None:
        Warning('Interpolation of the given profile returned None. '
                'It might be an error from profile or interpolation function.')
        return 0
    else:
        return b


def _set_bounds(m, t,
                index_name='profile_index',
                up_profile_name='up_profile_value',
                low_profile_name='low_profile_value'):
    """
    Rule to initiating variable bounds using interpolation of two given profiles.

    :param m: Block
    :param t: Set time
    :param str index_name: name of the index set
    :param str up_profile_name: name of the upper bound profile parameter
    :param str low_profile_name: name of the lower bound profile parameter
    :return: None
    """

    from scipy.interpolate.interpolate import interp1d

    if not hasattr(m, index_name):
        raise AttributeError(f'{m} object has no attribute {index_name}.'
                             f' Cannot proceed interpolation for initialization')
    if not hasattr(m, up_profile_name):
        raise AttributeError(f'{m} object has no attribute {up_profile_name}.'
                             f' Cannot proceed interpolation for initialization')
    if not hasattr(m, low_profile_name):
        raise AttributeError(f'{m} object has no attribute {low_profile_name}.'
                             f' Cannot proceed interpolation for initialization')
    if not isinstance(m.component(index_name), Set):
        raise TypeError(f'{index_name} is not a instance of Set,'
                        f' but is actually : f{type(m.component(index_name))}. Cannot proceed.')
    if not isinstance(m.component(up_profile_name), Param):
        raise TypeError(f'{up_profile_name} is not a instance of Param,'
                        f' but is actually : f{type(m.component(up_profile_name))}. Cannot proceed.')
    if not isinstance(m.component(low_profile_name), Param):
        raise TypeError(f'{low_profile_name} is not a instance of Param,'
                        f' but is actually : f{type(m.component(low_profile_name))}. Cannot proceed.')

    interp_x = list(m.component(index_name).value)
    interp_up = list(m.component(up_profile_name).extract_values().values())
    interp_low = list(m.component(low_profile_name).extract_values().values())

    funct_up = interp1d(interp_x, interp_up, kind='linear', fill_value='extrapolate')
    funct_low = interp1d(interp_x, interp_low, kind='linear', fill_value='extrapolate')

    bu = float(funct_up(t))
    bl = float(funct_low(t))

    if bu is None or bl is None:
        Warning('Interpolation of the given profile returned None. '
                'It might be an error from profile or interpolation function.')
        return 0, 0
    else:
        return bl, bu


def fix_profile(m, flow_name='flow', index_name='profile_index', profile_name='profile_value',
                doc_index = 'profile index', doc_value='profile value'):
    """
    Method for fixing a variable to a given dynamic profile.

    It replaces the variable "flow_name" by a parameter, whom initialization
    corresponds to the interpolation of a given profile with respect to his profile index.
    It generates One Set, named index_name, one Parameter, named profile_name.


    :param m: Block
    :param str flow_name: name of the value to be fixed
    :param index_name: name of the index set
    :param profile_name: name of the profile parameter
    :param doc_value: documentation for inherited units
    :param doc_index: documentation for inherited units
    :return: None
    """

    def _rule(bl, t):
        return 0

    m.add_component(index_name, Set(doc=doc_index))
    m.add_component(profile_name, Param(m.component(index_name), default=_rule, doc=doc_value))

    m.del_component(flow_name)
    m.add_component(flow_name, Param(m.time,
                                     doc='new profile, indexed by time',
                                     default=lambda bl, t: _init_input(bl, t,
                                                                       index_name=index_name,
                                                                       profile_name=profile_name)))


def bound_profile(m, t, flow_name='flow',
                  index_name='profile_index',
                  up_profile_name='up_profile_value',
                  low_profile_name='low_profile_value'):
    """
    Method for bounding a variable to given dynamic profiles.

    It bounds the variable "flow_name" by an upper and lower constraints, whom initialization
    corresponds to the interpolation of given profiles with respect to a given index.
    It generates One Set, the profile's index, named index_name, and two parameters,
    namely up_profile_name and low_profile_name.

    :param m: Block or Model
    :param t: time set
    :param str flow_name:
    :param str index_name:
    :param str up_profile_name:
    :param str low_profile_name:
    :return: None
    """

    def _rule(bl, t):
        return 0

    m.add_component(index_name, Set())
    m.add_component(low_profile_name, Param(m.component(index_name), default=_rule))
    m.add_component(up_profile_name, Param(m.component(index_name), default=_rule))

    m.del_component(flow_name)
    m.add_component(flow_name, Var(m.time, initialize=_init_input, bounds=_set_bounds))

    m.add_component(flow_name, Param(m.time, bounds=lambda bl, t: _set_bounds(bl, t,
                                                                              index_name=index_name,
                                                                              low_profile_name=low_profile_name,
                                                                              up_profile_name=up_profile_name)))


class TwoFlowUnit(DynUnit):
    """
    Abstract interface for two conservative ports block

    :param AbsDynUnit:
    :return:
    """

    def __init__(self, *args, flow_names=('flow_in', 'flow_out'), **kwargs):
        super().__init__(*args, **kwargs)

        self.intlet = Port(initialize={'f': (self.component(flow_names[0]), Port.Extensive, {'include_splitfrac': False})})
        self.outlet = Port(initialize={'f': (self.component(flow_names[1]), Port.Extensive, {'include_splitfrac': False})})


class FixedFlowSource(FlowSource):
    """
    Abstract Fixed Flow Source Unit.

    Abstract Source Unit who's flow variable is fixed using a given index set and indexed profile.
    """

    def __init__(self, *args, flow_name='flow', **kwargs):
        super().__init__(*args, flow_name=flow_name, **kwargs)

        fix_profile(self, flow_name=flow_name, index_name='profile_index', profile_name='profile_value')

        self.del_component('outlet')
        self.outlet = Port(initialize={'f': (self.component(flow_name),
                                             Port.Extensive,
                                             {'include_splitfrac': False})},
                           doc='output flow source using source convention')


class FixedFlowLoad(FlowLoad):
    """
    Abstract Fixed Flow Load Unit.

    Flow variable is fixed using a given index set and indexed profile.
    """

    def __init__(self, *args, flow_name='flow', **kwargs):
        super().__init__(*args, flow_name=flow_name, **kwargs)

        def _rule(m, t):
            return 0

        fix_profile(self, flow_name=flow_name, index_name='profile_index', profile_name='profile_value')

        self.del_component('inlet')
        self.inlet = Port(initialize={'f': (self.component(flow_name), Port.Extensive, {'include_splitfrac': False})})
