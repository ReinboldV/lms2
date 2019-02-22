# -*- coding: utf-8 -*-
"""
Batteries' Module.

Contains electrical batteries linear models.
"""

from lms2 import DynUnit, Var, Param
# from lms2.core.var import Var
# from lms2.core.param import Param
# from lms2.base.base_units import DynUnit

from pyomo.environ import Constraint
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.kernel.set_types import NonNegativeReals, Binary

__all__ = ['Battery']


class Battery(DynUnit):
    """ Simple Battery """

    def __init__(self, *args, time=None, socmin=None, socmax=None, emin=None, emax=None, dpcmax=None, dpdmax=None,
                 pcmax=None, pdmax=None, e0=None, ef=None, etac=1.0, etad=1.0, **kwds):
        """

        :param time: Continuous timeSet
        :param socmin: minimal state of charge (%)
        :param socmax: maximal state of charge (%)
        :param dpcmax: maximum variation of power (kW/s) >0
        :param dpcmin: minimal variation of power (kW/s) >0
        :param emin: Minimum stored energy (kWh)
        :param emax: Maximum stored energy (kWh)
        :param pcmax: Maximum charging power (kW)
        :param pdmax: Maximum descharging power (kW)
        :param e0: Initial stored energy (default = 0)
        :param ef: Final stored energy (default = None, i.e. no final constraint)
        :param etac: charging efficiency (\in [0, 1])
        :param etad: descharging efficiency (\in [0, 1])
        :param args:
        :param kwds:
        """
        super().__init__(*args, time=time, **kwds)

        self.pc = Var(time, doc='charging power', within=NonNegativeReals, initialize=0)
        self.pd = Var(time, doc='discharging power', within=NonNegativeReals, initialize=0)
        self.p = Var(time, doc='energy derivative with respect to time', initialize=0)
        self.p.port_type = 'flow'
        self.p.sens = 'in'
        self.e = Var(time, doc='energy in battery', initialize=0)

        self.dedt = DerivativeVar(self.e, wrt=time, doc='variation of energy in battery with respect to time',
                                  initialize=0)
        if etac is not None:
            assert etac <= 1, 'charging efficiency should be smaller than 1'
            assert etac > 0, 'charging efficiency should be strictly higher than 0'
            self.etac = Param(initialize=etac, doc='charging efficiency', mutable=True)

        if etad is not None:
            assert etad <= 1, 'discharging efficiency should be smaller than 1'
            assert etad > 0, 'discharging efficiency should be strictly higher than 0'
            self.etad = Param(initialize=etad, doc='discharging efficiency', mutable=True)

        if ef is not None:
            assert ef <= emax, 'final energy state should be smaller than emax'
            assert ef >= emin, 'final energy state should be bigger than emin'
            self.ef = Param(initialize=ef, doc='final state ()', mutable=True)

        if e0 is not None:
            self.e0 = Param(initialize=e0, doc='initial state', mutable=True)

        if emin is not None:
            self.emin = Param(initialize=emin, doc='minimum energy', mutable=True)

        if emax is not None:
            self.emax = Param(initialize=emax, doc='maximal energy', mutable=True)

        if socmin is not None:
            self.socmin = Param(initialize=socmin, doc='minimum soc', mutable=True)

        if socmax is not None:
            self.socmax = Param(initialize=socmax, doc='maximal soc', mutable=True)

        if dpdmax is not None:
            self.pdmax = Param(initialize=dpdmax, doc='maximal discharging power', mutable=True)

        if dpcmax is not None:
            self.dpcmax = Param(initialize=dpcmax, doc='maximal charging power', mutable=True)

        if dpcmax is not None or dpdmax is not None:
            self.dp = DerivativeVar(self.p, wrt=time, doc='varioation of the battery power with respect to time', initialize=0)

        if pcmax is not None:
            self.pcmax = Param(initialize=pcmax, doc='maximal charging power', mutable=True)

        if pdmax is not None:
            self.pdmax = Param(initialize=pdmax, doc='maximal discharging power', mutable=True)

        if not (etac == 1. and etad == 1.):
            self.u = Var(time, within=Binary, doc='binary variable for chage and discharge')

        def _e_initial(m, t):
            if e0 is None or t != time.value[0]:
                return Constraint.Skip
            return m.e[t] == m.e0

        self._e_initial = Constraint(time, rule=_e_initial, doc='Initial energy constraint')

        def _energy_balance(m, t):
            if not (etac == 1. and etad == 1.):
                return m.dedt[t] == 1/3600*(m.pc[t] * self.etac - m.pd[t] / m.etad)
            else:
                return m.dedt[t] == 1/3600*(m.pc[t] - m.pd[t])

        self._energy_balance = Constraint(time, rule=_energy_balance, doc='Energy balance constraint')

        def _p_balance(m, t):
            return m.p[t] == m.pc[t] - m.pd[t]

        self._p_balance = Constraint(time, rule=_p_balance, doc='Power balance constraint')

        def _p_init(m, t):
            if t != time.value[0]:
                return Constraint.Skip
            return m.p[t] == 0

        self._p_init = Constraint(time, rule=_p_init, doc='initialize power')

        def _e_final(m, t):
            if ef is None or t != time.value[-1]:
                return Constraint.Skip
            return m.e[t] == m.ef

        self._e_final = Constraint(time, rule=_e_final, doc='Final stored energy constraint')

        def _e_min(m, t):
            if emin is None:
                return Constraint.Skip
            return m.e[t] >= m.emin

        self._e_min = Constraint(time, rule=_e_min, doc='Minimal energy constraint')

        def _e_max(m, t):
            if emax is None:
                return Constraint.Skip
            return m.e[t] <= m.emax

        self._e_max = Constraint(time, rule=_e_max, doc='Maximal energy constraint')

        def _soc_min(m, t):
            if socmin is None:
                return Constraint.Skip
            return m.e[t] >= m.socmin*m.emax/100

        self._soc_min = Constraint(time, rule=_soc_min, doc='Minimal state of charge constraint')

        def _soc_max(m, t):
            if socmax is None:
                return Constraint.Skip
            return m.e[t] <= m.emax*m.socmax/100

        self._soc_max = Constraint(time, rule=_soc_max, doc='Maximal state of charge constraint')

        def _pcmax(m, t):
            if pcmax is None:
                return Constraint.Skip
            if not (etac == 1. and etad == 1.):
                return m.pc[t] - m.u[t] * m.pcmax <= 0
            else:
                return 0, m.pc[t], m.pcmax  # 0 <= m.pc[t] <= m.pcmax

        self._pcmax = Constraint(time, rule=_pcmax, doc='Maximal charging power constraint')

        def _pdmax(m, t):
            if pdmax is None:
                return Constraint.Skip
            if not (etac == 1. and etad == 1.):
                return m.pd[t] + m.u[t] * m.pdmax <= m.pdmax
            else:
                return 0, m.pd[t], m.pdmax  # 0 <= m.pd[t] <= m.pdmax

        self._pdmax = Constraint(time, rule=_pdmax, doc='Maximal descharging power constraint')

        def _dpcmax(m, t):
            if dpcmax is None:
                return Constraint.Skip
            else:
                return m.dp[t] <= m.dpcmax

        self._dpcmax = Constraint(time, rule=_dpcmax, doc='Maximal varation of charging power constraint')

        def _dpdmax(m, t):
            if dpdmax is None:
                return Constraint.Skip
            else:
                return m.dp[t] >= -m.dpdmax

        self._dpdmax = Constraint(time, rule=_dpdmax, doc='Maximal varation of descharging power constraint')
