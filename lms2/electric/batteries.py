# -*- coding: utf-8 -*-
"""
Batteries' Module.

Contains electrical batteries linear models.
"""

from lms2.core.units import DynUnit
from lms2.core.var import Var

from pyomo.core.base.param import Param
from pyomo.core.base.constraint import Constraint
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.kernel.set_types import *


class Battery(DynUnit):
    """ Simple Battery """

    def __init__(self, *args, time=None, emin=0, emax=30, pcmax=None, pdmax=None, e0=None, ef=None, etac=1.0, etad=1.0, **kwds):
        """

        :param args:
        :param time: Continuous timeSet
        :param emin: Minimum stored energy (kWh)
        :param emax: Maximum stored energy (kWh)
        :param pcmax: Maximum charging power (kW)
        :param pdmax: Maximum descharging power (kW)
        :param e0: Initial stored energy (default = 0)
        :param ef: Final stored energy (default = None, i.e. no final constraint)
        :param etac: charging efficiency (\in [0, 1])
        :param etad: descharging efficiency (\in [0, 1])
        :param kwds:
        """
        super().__init__(*args, time=time, **kwds)


        self.pc = Var(time, doc='charging power', within=NonNegativeReals, initialize=0)
        self.pd = Var(time, doc='discharging power', within=NonNegativeReals, initialize=0)
        self.p = Var(time, doc='energy derivative with respect to time', initialize=0)
        self.p.port_type = 'flow'
        self.p.sens = 'in'

        if etac is not None:
            assert etac <= 1, 'charging efficiency should be smaller than 1'
            assert etac > 0, 'charging efficiency should be strictly higher than 0'
            self.etac = Param(initialize=etac, doc='charging efficiency', within=(0, 1), mutable=True)

        if etad is not None:
            assert etad <= 1, 'discharging efficiency should be smaller than 1'
            assert etad > 0, 'discharging efficiency should be strictly higher than 0'
            self.etad = Param(initialize=etad, doc='discharging efficiency', within=(0, 1), mutable=True)

        if ef is not None:
            self.ef = Param(initialize=ef, doc='final state ()', mutable=True)

        if e0 is not None:
            self.e = Var(time, doc='energy in battery', initialize=e0)
            def _e_initial(m, t):
                if t != time.value[0]:
                    return Constraint.Skip
                return m.e[t] == m.e0

            self.e0 = Param(initialize=e0, doc='initial state', mutable=True)
            self._e_initial = Constraint(time, rule=_e_initial, doc='Initial energy constraint')
        else:
            self.e = Var(time, doc='energy in battery', initialize=0)
        self.dedt = DerivativeVar(self.e, wrt=time, doc='variation of energy in battery with respect to time',
                                  initialize=0)

        if emin is not None:
            self.emin = Param(initialize=emin, doc='minimum energy', mutable=True)

        if emax is not None:
            self.emax = Param(initialize=emax, doc='maximal energy', mutable=True)

        if pcmax is not None:
            self.pcmax = Param(initialize=pcmax, doc='maximal charging power', mutable=True)

        if pdmax is not None:
            self.pdmax = Param(initialize=pdmax, doc='maximal discharging power', mutable=True)

        if not (etac == 1. and etad == 1.):
            self.u = Var(time, within=Binary, doc='binary variable for chage and discharge')

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

        def _pcmax(m, t):
            if pcmax is None:
                return Constraint.Skip
            if not (etac == 1. and etad == 1.):
                return m.pc[t] - m.u[t] * m.pcmax <= 0
            else:
                return 0 <= m.pc[t] <= m.pcmax

        self._pcmax = Constraint(time, rule=_pcmax, doc='Maximal charging power constraint')

        def _pdmax(m, t):
            if pdmax is None:
                return Constraint.Skip
            if not (etac == 1. and etad == 1.):
                return m.pd[t] + m.u[t] * m.pdmax <= m.pdmax
            else:
                return 0 <= m.pd[t] <= m.pdmax

        self._pdmax = Constraint(time, rule=_pdmax, doc='Maximal descharging power constraint')
