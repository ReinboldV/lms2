from scipy.stats._multivariate import multi_rv_frozen

from lms2.core.units import DynUnit
from lms2.core.var import Var
from lms2.core.param import Param

from pyomo.core.base.constraint import Constraint
from pyomo.dae.diffvar import DerivativeVar
from pyomo.environ import *


class Storage(DynUnit):
    """ General storage unit"""

    def __init__(self, *args, c=2, time=None, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        c_fix = True

        self.e = Var(time, doc='effort variable')
        self.f = Var(time, doc='effort derivative with respect to time')
        self.dedt = DerivativeVar(self.e, wrt=time, doc='flow variable')

        if c_fix:
            self.c = Param(initialize=c, doc='coefficient between e1 and e2', mutable=True)
        else:
            self.c = Var(initialize=c, doc='coefficient between e1 and e2')

        def _cst(m, t):
            return m.f[t] == m.c * m.dedt[t]

        self.cst = Constraint(time, rule=_cst)


class Dipole(DynUnit):
    """ Simple dipole unit """

    def __init__(self, *args, time=None, r=1, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.p1 = Var(time, name='p1', doc='input variable')
        self.p2 = Var(time, name='p2', doc='output variable')
        self.r = Param(initialize=r, doc='coefficient between p1 and p2')

        def _cst(m, t):
            return m.p1[t] == m.r * m.p2[t]

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


class EffortSource(SourceUnit):
    """ Base Effort Source Unit.
    Generates one effort variable and fixe it using interpolation.
    """

    def __init__(self, *args, time, effort, kind='linear', fill_value='extrapolate', effort_name='flow', **kwargs):
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
        self.component(effort_name).port_type = 'effort'
        self.component(effort_name).sens = None


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
        self.component(flow_name).port_type = 'flow'
        self.component(flow_name).sens = 'out'


class FlowLoad(SourceUnit):
    """ Base Flow Load Unit.
    Generates one flow variable and fixe it using interpolation. Convention is set to sens='in'
    (the flow is counted positive when going in the unit).
    """

    def __init__(self, *args, time, flow, kind='linear', flow_name='flow', fill_value='extrapolate', **kwargs):
        """

        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series flow: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """

        super().__init__(*args, time=time, flow=flow, flow_name=flow_name, kind=kind,
                         fill_value=fill_value, doc=self.__doc__, **kwargs)
        self.component(flow_name).port_type = 'flow'
        self.component(flow_name).sens = 'in'


class UnitA(DynUnit):
    """ Base units for tests """

    def __init__(self, *args, time, flow):

        super().__init__(*args, time=time)
        _init_input, _set_bounds = set_profile(profile=flow, kind='linear', fill_value='extrapolate')
        self.x1 = Var(time, initialize=_init_input, bounds=_set_bounds)
        self.x1.port_type = 'effort'
        self.x2 = Var(time)
        self.x2.port_type = 'effort'
        self.y1 = Var(time, bounds=(0, 100))

        def _cst1(m, t):
            return m.x1[t] - m.x2[t] == m.y1[t]

        self.cst1 = Constraint(time, rule=_cst1)

        def _obj(m):
            return sum(m.y1[t] for t in time)

        self.obj = Objective(rule=_obj)


class Abs(DynUnit):
    """ Absolute Value """

    def __init__(self, *args, time, xmax=None, xmin=None):
        super().__init__(*args, time=time)

        M = 100000

        self.x = Var(time)
        self.component('x').port_type = 'effort'
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

        self.cst1 = Constraint(time,rule=_cst1)
        self.cst2 = Constraint(time,rule=_cst2)
        self.cst3 = Constraint(time,rule=_cst3)


def set_profile(profile, kind='linear', fill_value='extrapolate'):
    """ Generates constraint functions used to set bounds and values of the profile

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
            return 0
        else:
            return b

    def _set_bounds(m, t):
        b = float(funct(t))
        if b is None:
            return 0, 0
        else:
            return b, b

    return _init_input, _set_bounds


