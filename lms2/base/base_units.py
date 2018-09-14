from lms2.core.units import DynUnit

from lms2.core.var import Var
from lms2.core.param import Param
from pyomo.core.base.constraint import Constraint
from pyomo.dae.diffvar import DerivativeVar


class Storage(DynUnit):
    """ General storage """

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
    """ Simple dipole class """

    def __init__(self, *args, time=None, r=1, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.p1 = Var(time, name='p1', doc='input variable')
        self.p2 = Var(time, name='p2', doc='output variable')
        self.r = Param(initialize=r, doc='coefficient between e1 and e2')

        def _cst(m, t):
            return m.p1[t] == m.r * m.p2[t]

        self.cst = Constraint(time, rule=_cst)


class EffortSource(DynUnit):
    """
    Base flow source
    """

    def __init__(self, *args, time, flux, **kwargs):

        super().__init__(*args, time=time, **kwargs)
        self.flux = Var(time, initialize=0, default=0)
        self.flux.type_port = 'effort'
        self.sens = None

        def _init(m ,t):
            return


class FlowSource(DynUnit):
    """
    Base flow source
    """

    def __init__(self, *args, time, flow, kind='linear', fill_value='extrapolate', **kwargs):

        super().__init__(*args, time=time, **kwargs)
        from scipy.interpolate.interpolate import interp1d
        funct = interp1d(flow.index, flow.values, fill_value=fill_value, kind=kind)

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

        self.flow = Var(time, initialize=_init_input, bounds=_set_bounds)
        self.flow.port_type = 'flow'
        self.flow.sens = 'out'


class FlowLoad(FlowSource):
    """
    Base Flux load
    """

    def __init__(self, *args, time, flow, interpolate=True, kind='linear', fill_value='extrapolate', **kwargs):
        super().__init__(*args, time, flow, interpolate=interpolate, kind=kind, fill_value=fill_value, **kwargs)
        self.flow.sens = 'out'
