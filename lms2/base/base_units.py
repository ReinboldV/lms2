# -*- coding: utf-8 -*-
"""
Basic Units, multi-physical base model
"""

from lms2.core.units import Unit

from pyomo.environ import *
from pyomo.network import Port
from pyomo.dae import DerivativeVar


__all__ = ['DynUnit',           'DynUnitTest',      'AbsDynUnit',           'Storage',          '_OnePortBaseUnit',
           '_TwoPortBaseUnit',  'SourceUnit',       'AbsFixedFlowLoad',     'SourceUnitParam',  'ScalableFlowSource',
           'EffortSource',      'FlowSource',       'AbsFixedFlowSource',   'FlowLoad',         'AbsFlowSource',
           'AbsFlowLoad',       'AbsEffortSource',  'UnitA',                'Abs',              'set_profile',
           '_init_input',       '_set_bounds',      'fix_profile',          'bound_profile',    'AbsTwoFlowUnit',]


class DynUnit(Unit):
    def __init__(self, *args, time=None, **kwds):
        """ DEPRECIATED
        Dynamic Unit

        Standard unit with a time argument for indexing variables and constraints.

        :param args:
        :param time:
        :param kwds:
        """
        from pyomo.dae.contset import ContinuousSet

        super().__init__(*args, **kwds)
        if not isinstance(time, ContinuousSet):
            msg = f'time key word argument should be an instance of pyomo.dae.contest.ContinuousSet, ' \
                  f'and is actually a {type(time)}.'
            raise AttributeError(msg)
        self.doc = self.__doc__

    def get_constraints_values(self):
        return

    def get_duals(self):
        return


class AbsDynUnit(Unit):
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
        self.time = ContinuousSet()
        self.doc = self.__doc__

    def get_constraints_values(self):
        # TODO method for retrieving constraints slack
        return

    def get_duals(self):
        # TODO method for retrieving dual variables
        return

    def pplot(self, **kwargs):

        """
        Plotting method for AbsDyn Unit. It iterates on the component ctype of the Block and plots it.

        Currently, it only works with Var, Constraints and Expressions.

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


class DynUnitTest(DynUnit):
    """ Dynamic Test Unit """

    def __init__(self, *args, time=None, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.e = Var(time, within=NonNegativeReals)
        self.p = DerivativeVar(self.e, wrt=time)


class _OnePortBaseUnit(DynUnit):
    """ DEPRECIATED Dynamic Unit that is exposing one generic Port
    """

    def __init__(self, *args, time=None, **kwds):

        super(_OnePortBaseUnit, self).__init__(*args, time=time, doc=self.__doc__, **kwds)
        self.f = Var(time)
        self.e = Var(time)
        self.inlet = Port(initialize={'flow': self.f, 'effort': self.e})


class _TwoPortBaseUnit(DynUnit):
    """ DEPRECIATED Dynamic unit exposing two generic ports."""

    def __init__(self, *args, time=None, r=1, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.e1 = Var(time, name='e1', doc='input effort variable')
        self.f1 = Var(time, name='f1', doc='input flow variable')
        self.e2 = Var(time, name='e2', doc='output effort variable')
        self.f2 = Var(time, name='f2', doc='output flow variable')

        self.inlet = Port(initialize={'flow': (self.f1, Port.Conservative), 'effort': self.e1})
        self.outlet = Port(initialize={'flow': (self.f2, Port.Conservative), 'effort': self.e2})

        def _flux(m, t):
            return m.f1[t] == m.f2[t]

        self.flux = Constraint(time, rule=_flux, doc='flux conservation constraint.')


class Storage(_OnePortBaseUnit):
    """ DEPRECIATED  General storage unit"""

    def __init__(self, *args, time=None, capa=None, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.dedt = DerivativeVar(self.e, wrt=time, doc='variation of state variable over the time')

        if capa is not None:
            self.c = Param(initialize=capa, doc='capacity', mutable=True)
        else:
            self.c = Var(initialize=1, doc='capacity', within=PositiveReals)

        def _cst(m, t):
            return m.f[t] == m.c * m.dedt[t]

        self.cst = Constraint(time, rule=_cst)


class SourceUnit(DynUnit):
    """DEPRECIATED General Source Unit.

    Generates One variable tha may be fixed. This is a base class for definition of Effort/Flow, Source/Load."""

    def __init__(self, *args, time, flow, kind='linear', fill_value='extrapolate', flow_name='flow', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series flow: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """
        super().__init__(*args, time=time, **kwargs)
        _init_input, _set_bounds = set_profile(profile=flow, kind=kind, fill_value=fill_value)
        self.add_component(flow_name, Var(time, initialize=_init_input, bounds=_set_bounds))


class SourceUnitParam(DynUnit):
    """DEPRECIATED General Source Unit.

    Generates One parameter that may be fixed. This is a base class for definition of Effort/Flow, Source/Load."""

    def __init__(self, *args, time, flow, kind='linear', fill_value='extrapolate', flow_name='flow', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series flow: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """
        super().__init__(*args, time=time, **kwargs)
        _init_input, _set_bounds = set_profile(profile=flow, kind=kind, fill_value=fill_value)
        self.add_component(flow_name, Param(time, initialize=_init_input, default=_init_input, mutable=True))


class ScalableFlowSource(DynUnit):
    """DEPRECIATED General Scalable Flow Source Unit.

    Generates One parameter that may be fixed using a Time series. The flow is scaled using a variable scaling factor 'scale_fact'.
    This unit may be used for sizing of soucres, e.g. PV panels, Wind turbines, etc. """

    def __init__(self, *args, time, flow, kind='linear', fill_value='extrapolate', flow_name='flow', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series flow: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """
        super().__init__(*args, time=time, **kwargs)
        _init_input, _set_bounds = set_profile(profile=flow, kind=kind, fill_value=fill_value)
        self.add_component(flow_name+'_u',
                           Param(time, initialize=_init_input, default=_init_input, mutable=True,
                                 doc='Source flow for scale factor of 1'))
        self.add_component(flow_name,
                           Var(time, initialize=_init_input, doc='Scaled source flow'))
        self.scale_fact = Var(initialize=1, within=PositiveReals,
                              doc='scaling factor within Positve reals')

        def _flow_scaling(m, t):
            return m.scale_fact*m.find_component(flow_name+'_u')[t] == m.find_component(flow_name)[t]

        def _debug_flow_scaling(m, t):
            return -0.000001, m.scale_fact * m.find_component(flow_name + '_u')[t] \
                   - m.find_component(flow_name)[t], 0.000001

        # self.flow_scaling = Constraint(time, rule=_flow_scaling, doc='Constraint equality for flow scaling')
        # self.flow_scaling.deactivate()
        self.debug_flow_scaling = Constraint(time, rule=_debug_flow_scaling, doc='Constraint equality for flow scaling')
        self.outlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class EffortSource(SourceUnit):
    """ DEPRECIATED Base Effort Source Unit.
    Generates one effort variable and fixe it using interpolation.
    """

    def __init__(self, *args, time, effort, kind='linear', fill_value='extrapolate', effort_name='effort', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series effort: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """
        super().__init__(*args, time=time, flow=effort, flow_name=effort_name,
                         kind=kind, fill_value=fill_value, doc=self.__doc__, **kwargs)
        self.outlet = Port(initialize={'e': (self.component(effort_name), Port.Equality)})


class FlowSource(SourceUnit):
    """ DEPRECIATED Base Flow Source Unit.
    Generates one flow variable and fixe it using interpolation. Convention is set to sens='out'
    (the flow is counted positive when going out of the unit).
    """

    def __init__(self, *args, time, profile, kind='linear', fill_value='extrapolate', flow_name='flow', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series profile: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """

        super().__init__(*args, time=time, flow=profile, flow_name=flow_name, kind=kind,
                         fill_value=fill_value, doc=self.__doc__, **kwargs)

        self.outlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class FlowLoad(SourceUnit):
    """ DEPRECIATED Base Flow Load Unit.
    Generates one flow variable and fixe it using interpolation. Convention is set to sens='in'
    (the flow is counted positive when going in the unit).
    """

    def __init__(self, *args, time, profile, kind='linear', flow_name='flow', fill_value='extrapolate', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series flow: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """

        super().__init__(*args, time=time, flow=profile, flow_name=flow_name, kind=kind,
                         fill_value=fill_value, doc=self.__doc__, **kwargs)
        self.inlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class UnitA(DynUnit):
    """ DEPRECIATED Base units for tests """

    def __init__(self, *args, time, flow):

        super().__init__(*args, time=time)
        _init_input, _set_bounds = set_profile(profile=flow, kind='linear', fill_value='extrapolate')
        self.x1 = Var(time, initialize=_init_input, bounds=_set_bounds)
        self.x2 = Var(time, initialize=0)
        self.y1 = Var(time, bounds=(0, 100))

        def _cst1(m, t):
            return m.x1[t] - m.x2[t] == m.y1[t]

        self.cst1 = Constraint(time, rule=_cst1)

        def _instant_obj(m, t):
            return m.y1[t]

        self.inst_obj = Expression(time, rule=_instant_obj)


class Abs(DynUnit):
    """ DEPRECIATED Absolute Value """

    def __init__(self, *args, time, xmax=None, xmin=None):
        super().__init__(*args, time=time)

        M = 100000

        self.x = Var(time)

        if xmin is None:
            if xmax is None:
                xmin = -M
            else:
                xmin = -xmax
        if xmax is None:
            xmax = M

        self.xmax = Param(initialize=xmax)
        self.xmin = Param(initialize=xmin)

        self.s1 = Var(time, within=PositiveReals)
        self.s2 = Var(time, within=PositiveReals)
        self.u = Var(time, within=Binary)

        def _cst1(m,t):
            return m.s1[t] <= m.xmax*m.u[t]

        def _cst2(m, t):
            return m.s2[t] <= -m.xmin * (1-m.u[t])

        def _cst3(m, t):
            return m.s1[t] - m.s2[t] == m.x[t]

        self.cst1 = Constraint(time, rule=_cst1)
        self.cst2 = Constraint(time, rule=_cst2)
        self.cst3 = Constraint(time, rule=_cst3)

        self.f_inlet = Port(initialize={'f': (self.x, Port.Conservative)})
        self.f_outlet = Port(initialize={'f': (self.x, Port.Conservative)})
        self.e_inlet = Port(initialize={'e': (self.x, Port.Equality)})


class AbsFlowSource(AbsDynUnit):
    """
    Abstract Flow Source Unit.

    Exposes a conservative port for generic flow variable.
    """
    def __init__(self, *args, flow_name='flow', **kwargs):
        """
        :param str flow_name: name of the flow variable
        """
        super().__init__(*args, **kwargs)
        self.add_component(flow_name, Var(self.time, initialize=None, within=Reals))
        self.outlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class AbsFlowLoad(AbsDynUnit):
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
        self.add_component(flow_name, Var(self.time, initialize=0, within=Reals))
        self.inlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class AbsEffortSource(AbsDynUnit):
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

    interp_x = list(m.component(index_name).value)
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

    interp_x   = list(m.component(index_name).value)
    interp_up  = list(m.component(up_profile_name).extract_values().values())
    interp_low = list(m.component(low_profile_name).extract_values().values())

    funct_up  = interp1d(interp_x, interp_up,  kind='linear', fill_value='extrapolate')
    funct_low = interp1d(interp_x, interp_low, kind='linear', fill_value='extrapolate')

    bu = float(funct_up(t))
    bl = float(funct_low(t))

    if bu is None or bl is None:
        Warning('Interpolation of the given profile returned None. '
                'It might be an error from profile or interpolation function.')
        return 0, 0
    else:
        return bl, bu

def fix_profile(m, flow_name='flow', index_name='profile_index', profile_name='profile_value'):

    """
    Method for fixing a variable to a given dynamic profile.

    It replaces the variable "flow_name" by a parameter, whom initialization
    corresponds to the interpolation of a given profile with respect to his profile index.
    It generates One Set, named index_name, one Parameter, named profile_name.

    :param m: Block
    :param str flow_name: name of the value to be fixed
    :param index_name: name of the index set
    :param profile_name: name of the profile parameter
    :return: None
    """

    def _rule(bl, t):
        return 0

    m.add_component(index_name, Set())
    m.add_component(profile_name, Param(m.component(index_name), default=_rule))

    m.del_component(flow_name)
    m.add_component(flow_name, Param(m.time, default=lambda bl, t : _init_input(bl, t,
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
    m.add_component(up_profile_name,  Param(m.component(index_name), default=_rule))

    m.del_component(flow_name)
    m.add_component(flow_name, Var(m.time, initialize=_init_input, bounds=_set_bounds))

    m.add_component(flow_name, Param(m.time, bounds=lambda bl, t: _set_bounds(bl, t,
                                                                              index_name=index_name,
                                                                              low_profile_name=low_profile_name,
                                                                              up_profile_name=up_profile_name)))


class AbsTwoFlowUnit(AbsDynUnit):
    """
    Abstract interface for two conservative ports block

    :param AbsDynUnit:
    :return:
    """

    def __init__(self, *args, flow_names=('flow_in', 'flow_out'), **kwargs):
        super().__init__(*args, **kwargs)

        self.intlet = Port(initialize={'f': (self.component(flow_names[0]), Port.Conservative)})
        self.outlet = Port(initialize={'f': (self.component(flow_names[1]), Port.Conservative)})


class AbsFixedFlowSource(AbsFlowSource):
    """
    Abstract Fixed Flow Source Unit.

    Abstract Source Unit who's flow variable is fixed using a given index set and indexed profile.
    """

    def __init__(self, *args, flow_name='flow', **kwargs):

        super().__init__(*args, flow_name = flow_name, **kwargs)

        fix_profile(self, flow_name=flow_name, index_name='profile_index', profile_name='profile_value')

        self.del_component('outlet')
        self.outlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class AbsFixedFlowLoad(AbsFlowLoad):
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
        self.inlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})

def set_profile(profile, kind='linear', fill_value='extrapolate'):
    """ DEPRECIATED
    Generates constraint functions used to set bounds and values of profiles

    :param pandas Serie profile: Series that describes the input profile
    :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
    :param str fill_value: see scipy.interpolate.interpolate.interp1d
    :return:
    """

    from scipy.interpolate.interpolate import interp1d
    from pandas import Series
    assert isinstance(profile, Series), f'argument flow  should be a pandas serie.'

    funct = interp1d(profile.index, profile.values, fill_value=fill_value, kind=kind)

    def _init_input(m, t):
        b = float(funct(t))
        if b is None:
            Warning('Interpolation of the given profile returned None. '
                    'It might be an error from profile or interpolation function.')
            return 0
        else:
            return b

    def _set_bounds(m, t):
        b = float(funct(t))
        if b is None:
            Warning('Interpolation of the given profile returned None. '
                    'It might be an error from profile or interpolation function.')
            return 0, 0
        else:
            return b, b

    return _init_input, _set_bounds



