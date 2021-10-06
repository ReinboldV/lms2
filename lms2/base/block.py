# -*- coding: utf-8 -*-
"""
Basic Units, multi-physical base model
"""

from pyomo.core import Reals
from pyomo.environ import *
from pyomo.network import Port
from pyomo.dae import ContinuousSet

from pyomo.core.base.units_container import units as u

__all__ = ['flow_source', 'flow_load', 'effort_source', 'fix_profile']


def flow_source(b, **options):
    """
    Abstract Flow Source Unit.

    Exposes a conservative output port for generic flow variable.

    :param str doc_flow: documentation for inherited units
    :param str flow_name: name of the flow variable
    """
    flow_name = options.pop('flow_name', 'flow')
    doc_flow = options.pop('doc_flow', 'documentation')
    time = options.pop('time', ContinuousSet(bounds=(0, 1)))

    b.add_component(flow_name, Var(time, initialize=0, within=Reals, doc=doc_flow))
    b.outlet = Port(initialize={'f': (b.component(flow_name), Port.Extensive, {'include_splitfrac': False})},
                    doc='output flow port using source convention. ')
    return b


def flow_load(b, **options):
    """
    Abstract Flow Load Unit.

    Exposes a conservative port for generic flow variable.
    Source convention is used.

    :param str flow_name: name of the flow variable
    """

    flow_name = options.pop('flow_name', 'flow')
    doc_flow = options.pop('doc_flow', 'documentation')
    time = options.pop('time', ContinuousSet(bounds=(0, 1)))

    b.add_component(flow_name, Var(time, initialize=0, within=Reals, doc=doc_flow))
    b.inlet = Port(initialize={'f': (b.component(flow_name), Port.Extensive, {'include_splitfrac': False})},
                   doc='Input flow inlet, using load convention')

    return b


def effort_source(b, **options):
    """
    Abstract Effort source unit.

    Exposes a Equality port for generic effort variable.
    """

    effort_name = options.pop('effort_name', 'effort')
    doc_effort = options.pop('doc_effort', 'documentation')
    time = options.pop('time', ContinuousSet(bounds=(0, 1)))

    b.add_component(effort_name, Var(time, initialize=0, within=Reals, doc=doc_effort))
    b.outlet = Port(initialize={'e': (b.component(effort_name))})

    return b

## OLD CODE : DEPRECIATED
#
def _init_input(m, t, index_name='profile_index', profile_name='profile_value'):
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

    interp_x = list(m.component(index_name).ordered_data())
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

#
# def bound_profile(m, t, flow_name='flow',
#                   index_name='profile_index',
#                   up_profile_name='up_profile_value',
#                   low_profile_name='low_profile_value'):
#     """
#     Method for bounding a variable to given dynamic profiles.
#
#     It bounds the variable "flow_name" by an upper and lower constraints, whom initialization
#     corresponds to the interpolation of given profiles with respect to a given index.
#     It generates One Set, the profile's index, named index_name, and two parameters,
#     namely up_profile_name and low_profile_name.
#
#     :param m: Block or Model
#     :param t: time set
#     :param str flow_name:
#     :param str index_name:
#     :param str up_profile_name:
#     :param str low_profile_name:
#     :return: None
#     """
#
#     def _rule(bl, t):
#         return 0
#
#     m.add_component(index_name, Set())
#     m.add_component(low_profile_name, Param(m.component(index_name), default=_rule))
#     m.add_component(up_profile_name, Param(m.component(index_name), default=_rule))
#
#     m.del_component(flow_name)
#     m.add_component(flow_name, Var(m.time, initialize=_init_input, bounds=_set_bounds))
#
#     m.add_component(flow_name, Param(m.time, bounds=lambda bl, t: _set_bounds(bl, t,
#                                                                               index_name=index_name,
#                                                                               low_profile_name=low_profile_name,
#                                                                               up_profile_name=up_profile_name)))
