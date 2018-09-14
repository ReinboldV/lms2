from pyomo.environ import *
from pyomo.core.base.constraint import Constraint
from pyomo.core.kernel.set_types import *
from pandas import Series

from lms2.core.units import DynUnit
from lms2.core.var import Var
from lms2.core.param import Param


class MainGrid(DynUnit):
    """
    Simple main Grid with time varying costs

    Example ::

        Create Model Instance and add a MinGrid Unit ::



    """
    def __init__(self, time, *args, pmax=None, pmin=None, cin=None, cout=None, **kwgs):

        if cin is None:
            cin = {0: 1, 1: 1}
        if cout is None:
            cout = {0: 1, 1: 1}

        super().__init__(*args, time=time, **kwgs)

        self.pout = Var(time, doc='power to the main grid', within=NonNegativeReals, initialize=0)
        self.pin = Var(time, doc='power from the main grid', within=NonNegativeReals, initialize=0)
        self.u = Var(time, doc='binary variable', within=Binary, initialize=0)
        self.p = Var(time, doc='power from the main grid to the microgrid', initialize=0)
        self.p.port_type = 'flow'
        self.p.sens = 'in'

        def _energy_balance(m, t):
            return m.p[t] == m.pin[t] - m.pout[t]
        self._energy_balance = Constraint(time, rule=_energy_balance)

        if pmin is not None:
            self.pmin = Param(initialize=pmin, mutable=True, doc='maximal power out')

        if pmax is not None:
            self.pmax = Param(initialize=pmax, mutable=True, doc='maximal power in')

        def _pmax(m, t):
            if pmax is None:
                return Constraint.Skip
            return m.pin[t] - m.u[t] * m.pmax <= 0

        self._pmax = Constraint(time, rule=_pmax)

        def _pmin(m, t):
            if pmin is None:
                return Constraint.Skip
            return m.pout[t] + m.u[t] * m.pmin <= m.pmin

        self._pmin = Constraint(time, rule=_pmin)

        # cin is a dictionnary, the cost is considered varibale during the time, horizon, and
        # it is interpolated using the Suffix.LOCAL

        self.cin = Var(time, doc="buying energy from the main grid", initialize=cin)
        self.cout = Var(time, doc="selling energy to the main grid", initialize=cout)

        self.var_input = Suffix(direction=Suffix.LOCAL)
        self.var_input[self.cin] = cin
        self.var_input[self.cout] = cout

        def _obj_use(m, t):
            return sum(m.pin[t]*m.cin[t] + m.pout[t]*m.cout[t])


if __name__ == "__main__":
    from lms2.core.models import LModel
    from lms2.core.time import Time
    # from lms2.electric.maingrids import MainGrid
    from pyomo.environ import *

    m = LModel(name='model')
    m.time = Time('00:00:00', '01:00:00', freq='1Min')
    m.mg = MainGrid(time=m.time.time_contSet, pmax=20, pmin=-20, cin={0: 1, 1080: 2, 2160: 0.5},
                    cout={0: 1, 1080: 0.5, 2160: 1})

    discretizer = TransformationFactory('dae.finite_difference')
    discretizer.apply_to(m, wrt=m.time.time_contSet, nfe=60, scheme='BACKWARD')  # BACKWARD or FORWARD

    m.var_input = Suffix(direction=Suffix.EXPORT)
    m.var_input[m.mg.p] = {0: -10, 780: -15, 3600: 15}


    def _obj(m):
        return 0
    m.obj = Objective(rule=_obj)

    opt = SolverFactory('glpk')
    results = opt.solve(m)



# class MainGrid(DynUnit):
#     """
#     Simple main Grid unit
#     """
#     def __init__(self, time, *args, pmax=None, pmin=None, cout=None, cin=None, interpolate=True, kind='linear', fill_value='extrapolate', **kwgs):
#         from scipy.interpolate.interpolate import interp1d
#         super().__init__(*args, time=time, **kwgs)
#
#         self.pout = Var(time, doc='power to the main grid', within=NonNegativeReals, initialize=0)
#         self.pin = Var(time, doc='power from the main grid', within=NonNegativeReals, initialize=0)
#         self.p = Var(time, doc='power from the main grid to the microgrid', initialize=0)
#         self.p.port_type = 'flow'
#         self.p.sens = 'in'
#
#         def _energy_balance(m, t):
#             return m.p[t] == m.pin[t] - m.pout[t]
#         self._energy_balance = Constraint(time, rule=_energy_balance)
#
#         if pmin is not None:
#             self.pmin = Param(initialize=pmin, mutable=True, doc='maximal power out')
#
#         if pmax is not None:
#             self.pmax = Param(initialize=pmax, mutable=True, doc='maximal power in')
#
#         def _pmax(m, t):
#             if pmax is None:
#                 return Constraint.Skip
#             return m.pin[t] - m.u[t] * m.pmax <= 0
#
#         self._pmax = Constraint(time, rule=_pmax)
#
#         def _pmin(m, t):
#             if pmin is None:
#                 return Constraint.Skip
#             return m.pout[t] + m.u[t] * m.pmin <= m.pmin
#
#         self._pmin = Constraint(time, rule=_pmin)
#
#         # if cin is initialized with a float, the cost is considered fixed during the time horizon,
#         # otherwise, is cin is a pandas.series, the cost is considered varibale during the time, horizon, and
#         # it is interpolated
#         if cin is not None:
#             if isinstance(cin, float) or isinstance(cin, int):
#                 self.cin = Param(initialize=cin, doc='buying cost of energy', mutable=True)
#             elif isinstance(cin, Series):
#                 fun_cin = interp1d(cin.index, cin.values, fill_value=fill_value, kind=kind, interpolate=interpolate)
#
#                 def _init_cin(m, t):
#                     b = float(fun_cin(t))
#                     if b is None:
#                         return 0
#                     else:
#                         return b
#
#                 def _bounds_cin(m, t):
#                     b = float(fun_cin(t))
#                     if b is None:
#                         return 0, 0
#                     else:
#                         return b, b
#                 self.cin = Var(time, initialize=_init_cin, bounds=_bounds_cin)
#
#         # same behaviour than cin
#         if cout is not None:
#             if isinstance(cout, float) or isinstance(cout, int):
#                 self.cout = Param(initialize=cout, doc='selling cost of energy', mutable=True)
#             elif isinstance(cout, Series):
#                 fun_cout = interp1d(cout.index, cout.values, fill_value=fill_value, kind=kind, interpolate=interpolate)
#
#                 def _init_cout(m, t):
#                     b = float(fun_cout(t))
#                     if b is None:
#                         return 0
#                     else:
#                         return b
#
#                 def _bounds_cout(m, t):
#                     b = float(fun_cout(t))
#                     if b is None:
#                         return 0, 0
#                     else:
#                         return b, b
#
#                 self.cout = Var(time, initialize=_init_cout, bounds=_bounds_cout)
#
#         def _obj_use(m):
#             return sum(m.pin[t]*m.cin[t] + m.pout[t]*m.cout[t] for t in time)
