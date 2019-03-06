# -*- coding: utf-8 -*-
"""
Basic Units, multi-physical base model
"""

from lms2.core.units import DynUnit
from lms2.core.var import Var
from lms2.core.param import Param

from pyomo.environ import Constraint, PositiveReals, Binary, Reals, Objective, Expression
from pyomo.network import Port
from pyomo.dae import DerivativeVar

__all__ = ['Storage', 'TwoPortBaseUnit', 'SourceUnit', 'SourceUnitParam', 'ScalableFlowSource', 'EffortSource', 'FlowSource',
           'FlowLoad', 'UnitA', 'Abs', 'set_profile']


class _OnePortBaseUnit(DynUnit):
    """ Dynamic Unit that is exposing one generic Port
    """

    def __init__(self, *args, time=None, **kwds):

        super(_OnePortBaseUnit, self).__init__(*args, time=time, doc=self.__doc__, **kwds)
        self.f = Var(time)
        self.e = Var(time)
        self.inlet = Port(initialize={'flow': self.f, 'effort': self.e})


class TwoPortBaseUnit(DynUnit):
    """ Dynamic unit exposing two generic ports."""

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
    """ General storage unit"""

    def __init__(self, *args, time=None, capa=None, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        # self.e = Var(time, doc='effort variable')
        # self.f = Var(time, doc='effort derivative with respect to time')
        self.dedt = DerivativeVar(self.e, wrt=time, doc='variation of state variable over the time')

        if capa is not None:
            self.c = Param(initialize=capa, doc='capacity', mutable=True)
        else:
            self.c = Var(initialize=1, doc='capacity', within=PositiveReals)

        def _cst(m, t):
            return m.f[t] == m.c * m.dedt[t]

        self.cst = Constraint(time, rule=_cst)


class SourceUnit(DynUnit):
    """General Source Unit.

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
    """General Source Unit.

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
    """General Scalable Flow Source Unit.

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

        self.flow_scaling = Constraint(time, rule=_flow_scaling, doc='Constraint equality for flow scaling')
        self.flow_scaling.deactivate()
        self.debug_flow_scaling = Constraint(time, rule=_debug_flow_scaling, doc='Constraint equality for flow scaling')
        self.outlet = Port(initialize={'f': (self.component(flow_name), Port.Conservative)})


class EffortSource(SourceUnit):
    """ Base Effort Source Unit.
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
    """ Base Flow Source Unit.
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
    """ Base Flow Load Unit.
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
    """ Base units for tests """

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
    """ Absolute Value """

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


def set_profile(profile, kind='linear', fill_value='extrapolate'):
    """ Generates constraint functions used to set bounds and values of profiles

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


