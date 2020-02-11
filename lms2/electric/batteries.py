# -*- coding: utf-8 -*-
"""
Batteries' Module.

Contains electrical batteries linear models.
"""

from pyomo.core.kernel.set_types import NonNegativeReals, Binary
from pyomo.dae.diffvar import DerivativeVar
from pyomo.dae import Integral
from pyomo.environ import Constraint, Var, Param, Expression, PositiveReals, Set
from pyomo.network import Port

from lms2 import DynUnit

__all__ = ['BatteryV0', 'BatteryV1', 'BatteryV2', 'BatteryV3']

UB = 10e6

data = dict(
    time={None: (0, 1)},
    socmin={None: 0},
    socmax={None: 100},
    dpcmax={None: None},
    dpcmin={None: None},
    emin={None: 0},
    emax={None: None},
    pcmax={None: UB},
    pdmax={None: UB},
    e0={None: None},
    ef={None: None},
    etac={None: 1.0},
    etad={None: 1.0}
)


#   TODO  : add different model of ageing.
#   do bibliography and add model from D. TENFEN

class BatteryV0(DynUnit):
    """
    Battery with ideal efficiency.

    This battery is limited in power, variation of power and energy. One can fix initial and final stored energy.
    For fixing initial en final state of charge, consider using `AbsBatteryV1`.
    It exposes one power port using source convention.

    """

    def __init__(self, *args, **kwds):
        """

        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p               energy derivative with respect to time
        e               energy in battery
        =============== ===================================================================

        =============== ===================================================================
        Derivative Var  Documentation
        =============== ===================================================================
        de              variation of energy  with respect to time
        dp              variation of the battery power with respect to time
        =============== ===================================================================

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        emin            minimum energy (kWh)
        emax            maximal energy
        e0              initial state
        ef              final state
        etac            charging efficiency
        etad            discharging efficiency
        dpdmax          maximal discharging power
        dpcmax          maximal charging power
        pcmax           maximal charging power
        pdmax           maximal discharging power
        =============== ===================================================================

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _e_balance      Energy balance constraint
        _p_init         Initialize power
        _e_initial      Initial energy constraint
        _e_final        Final stored energy constraint
        _e_min          Minimal energy constraint
        _e_max          Maximal energy constraint
        _pmax           Power bounds constraint
        _dpdmax         Maximal varation of descharging power constraint
        _dpcmax         Maximal varation of charging power constraint
        =============== ===================================================================

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        outlet          None
        =============== ===================================================================

        """

        super().__init__(*args, **kwds)

        self.p = Var(self.time, doc='Output power of the battery (kW)', initialize=0) #: initial value: par1
        self.e = Var(self.time, doc='Energy in battery (kWh)', initialize=0)

        self.emin = Param(default=0, doc='minimum energy (kWh)', mutable=True, within=NonNegativeReals)
        self.emax = Param(default=UB, doc='maximal energy', mutable=True)
        self.e0 = Param(default=None, doc='initial state', mutable=True)
        self.ef = Param(default=None, doc='final state', mutable=True)
        self.etac = Param(default=1.0, doc='charging efficiency', mutable=True)
        self.etad = Param(default=1.0, doc='discharging efficiency', mutable=True)
        self.dpdmax = Param(default=UB, doc='maximal discharging power', mutable=True)
        self.dpcmax = Param(default=UB, doc='maximal charging power', mutable=True)

        self.pcmax = Param(default=UB, doc='maximal charging power', mutable=True, within=PositiveReals)
        self.pdmax = Param(default=UB, doc='maximal discharging power', mutable=True, within=PositiveReals)

        self.de = DerivativeVar(self.e, wrt=self.time, initialize=0,
                                doc='variation of energy  with respect to time')
        self.dp = DerivativeVar(self.p, wrt=self.time, initialize=0,
                                doc='variation of the battery power with respect to time',
                                bounds=lambda m, t: (-m.dpcmax, m.dpdmax))

        self.outlet = Port(initialize={'f': (self.p, Port.Extensive, {'include_splitfrac': False})})

        def _p_init(m, t):
            if t == m.time.bounds()[0]:
                return m.p[t] == 0
            return Constraint.Skip

        def _e_initial(m, t):
            if m.e0.value is not None:
                if t == 0:
                    return m.e[t] == m.e0
            return Constraint.Skip

        def _e_final(m, t):
            if m.ef.value is None:
                return Constraint.Skip
            if t == m.time.last():
                return m.ef - 1e-5, m.e[t], m.ef + 1e-5
            else:
                return Constraint.Skip

        def _e_min(m, t):
            if m.emin.value is None:
                return Constraint.Skip
            return m.e[t] >= m.emin

        def _e_max(m, t):
            if m.emax.value is None:
                return Constraint.Skip
            return m.e[t] <= m.emax

        def _pmax(m, t):
            if m.pcmax.value is None:
                return Constraint.Skip
            else:
                return -m.pcmax, m.p[t], m.pdmax

        def _dpcmax(m, t):
            if m.dpcmax.value is None:
                return Constraint.Skip
            else:
                return m.dp[t] >= -m.dpcmax

        def _dpdmax(m, t):
            if m.dpdmax.value is None:
                return Constraint.Skip
            else:
                return m.dp[t] <= m.dpdmax

        def _energy_balance(m, t):
            return m.de[t] == 1 / 3600 * (m.p[t])

        self._e_balance = Constraint(self.time, rule=_energy_balance, doc='Energy balance constraint')
        self._p_init = Constraint(self.time, rule=_p_init, doc='Initialize power')
        self._e_initial = Constraint(self.time, rule=_e_initial, doc='Initial energy constraint')
        self._e_final = Constraint(self.time, rule=_e_final, doc='Final stored energy constraint')
        self._e_min = Constraint(self.time, rule=_e_min, doc='Minimal energy constraint')
        self._e_max = Constraint(self.time, rule=_e_max, doc='Maximal energy constraint')
        self._pmax = Constraint(self.time, rule=_pmax, doc='Power bounds constraint')
        self._dpdmax = Constraint(self.time, rule=_dpdmax, doc='Maximal varation of descharging power constraint')
        self._dpcmax = Constraint(self.time, rule=_dpcmax, doc='Maximal varation of charging power constraint')


class BatteryV1(DynUnit):
    """ Battery with ideal efficiency.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge. For fixing initial and final energy, consider using `AbsBatteryV0`.
    It exposes one power port using source convention.
    """

    def __init__(self, *args, **kwds):
        """
        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p               energy derivative with respect to time
        e               energy in battery
        =============== ===================================================================

        =============== ===================================================================
        Derivative Var  Documentation
        =============== ===================================================================
        de              variation of energy  with respect to time
        dp              variation of the battery power with respect to time
        =============== ===================================================================

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        emin            minimum energy (kWh)
        emax            maximal energy
        socmin          minimum soc
        socmax          maximal soc
        soc0            initial state
        socf            final state
        dpdmax          maximal discharging power
        dpcmax          maximal charging power
        pcmax           maximal charging power
        pdmax           maximal discharging power
        =============== ===================================================================

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _soc_init       None
        _e_balance      Energy balance constraint
        _p_init         Initialize power
        _e_min          Minimal energy constraint
        _e_max          Maximal energy constraint
        _soc_final      Final soc constraint
        _soc_min        Minimal state of charge constraint
        _soc_max        Maximal state of charge constraint
        _pmax           Power bounds constraint
        _dpdmax         Maximal varation of descharging power constraint
        _dpcmax         Maximal varation of charging power constraint
        =============== ===================================================================

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        outlet          output power of the battery (kW), using source convention
        =============== ===================================================================

        =============== ===================================================================
        Expressions     Documentation
        =============== ===================================================================
        soc             Expression of the state of charge
        =============== ===================================================================

        """
        super().__init__(*args, **kwds)

        self.emin = Param(default=0, doc='minimum energy (kWh)', mutable=True, within=NonNegativeReals)
        self.emax = Param(default=UB, doc='maximal energy', mutable=True)
        self.socmin = Param(default=0, doc='minimum soc', mutable=True)
        self.pinit  = Param(default=None, doc='initial output power of the battery (default : None)', mutable=True)
        self.socmax = Param(default=100, doc='maximal soc', mutable=True)
        self.soc0 = Param(default=50, doc='initial state', mutable=True)
        self.socf = Param(default=50, doc='final state', mutable=True)
        self.dpdmax = Param(default=UB, doc='maximal discharging power', mutable=True)
        self.dpcmax = Param(default=UB, doc='maximal charging power', mutable=True)
        self.pcmax = Param(default=UB, doc='maximal charging power', mutable=True, within=NonNegativeReals)
        self.pdmax = Param(default=UB, doc='maximal discharging power', mutable=True, within=NonNegativeReals)

        def _init_e(m, t):
            if m.soc0.value is not None:
                return m.soc0 * m.emax / 100
            else:
                return 50

        self.p = Var(self.time, doc='energy derivative with respect to time', initialize=0)
        self.e = Var(self.time, doc='energy in battery', initialize=_init_e)

        self.de = DerivativeVar(self.e, wrt=self.time, initialize=0, doc='variation of energy  with respect to time')
        self.dp = DerivativeVar(self.p, wrt=self.time, initialize=0,
                                doc='variation of the battery power with respect to time',
                                bounds=lambda m, t: (-m.dpcmax, m.dpdmax))

        self.outlet = Port(initialize={'f': (self.p, Port.Extensive, {'include_splitfrac': False})},
                           doc='output power of the battery (kW), using source convention')

        # initializing pinit should not be done, since it can introduce infeasibility in case of moving horizon
        def _p_init(m, t):
            if m.pinit.value is not None:
                if t == m.time.first():
                    return m.p[t] == m.pinit
            return Constraint.Skip

        def _e_min(m, t):
            if m.emin.value is None:
                return Constraint.Skip
            return m.e[t] >= m.emin

        def _e_max(m, t):
            if m.emax.value is None:
                return Constraint.Skip
            return m.e[t] <= m.emax

        def _pmax(m, t):
            if m.pcmax.value is None:
                return Constraint.Skip
            else:
                return -m.pcmax, m.p[t], m.pdmax

        @self.Constraint(self.time, doc='initial state of charge')
        def _soc_init(m, t):
            if m.soc0.value is None:
                return Constraint.Skip
            else:
                if t == m.time.first():
                    return m.e[t] == m.soc0 * m.emax / 100
                else:
                    return Constraint.Skip

        def _soc_final(m, t):
            if m.socf.value is None:
                return Constraint.Skip
            else:
                if t == m.time.last():
                    return m.e[t] == m.socf * m.emax / 100
                else:
                    return Constraint.Skip

        def _soc_min(m, t):
            if m.socmin.value is None:
                return Constraint.Skip
            return m.e[t] >= m.socmin * m.emax / 100

        def _soc_max(m, t):
            if m.socmax.value is None:
                return Constraint.Skip
            return m.e[t] <= m.emax * m.socmax / 100

        def _dpcmax(m, t):
            if m.dpcmax.value is None:
                return Constraint.Skip
            else:
                return m.dp[t] >= -m.dpcmax

        def _dpdmax(m, t):
            if m.dpdmax.value is None:
                return Constraint.Skip
            else:
                return m.dp[t] <= m.dpdmax

        def _energy_balance(m, t):
            return m.de[t] == 1 / 3600 * m.p[t]

        self._e_balance = Constraint(self.time, rule=_energy_balance, doc='Energy balance constraint')
        self._p_init = Constraint(self.time, rule=_p_init, doc='Initialize power')
        self._e_min = Constraint(self.time, rule=_e_min, doc='Minimal energy constraint')
        self._e_max = Constraint(self.time, rule=_e_max, doc='Maximal energy constraint')
        self._soc_final = Constraint(self.time, rule=_soc_final, doc='Final soc constraint')
        self._soc_min = Constraint(self.time, rule=_soc_min, doc='Minimal state of charge constraint')
        self._soc_max = Constraint(self.time, rule=_soc_max, doc='Maximal state of charge constraint')
        self._pmax = Constraint(self.time, rule=_pmax, doc='Power bounds constraint')
        self._dpdmax = Constraint(self.time, rule=_dpdmax, doc='Maximal varation of descharging power constraint')
        self._dpcmax = Constraint(self.time, rule=_dpcmax, doc='Maximal varation of charging power constraint')

        self.soc = Expression(self.time, rule=lambda m, t: 100 * m.e[t] / m.emax,
                              doc='Expression of the state of charge')


class BatteryV2(BatteryV1):
    """
    Bilinear battery Model.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge.
    Efficiency for charge and discharge are considered.
    It exposes one power port using source convention.
    """

    def __init__(self, *args, **kwargs):
        """
        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p               energy derivative with respect to time
        e               energy in battery
        pd              discharging power
        pc              charging power
        u               binary variable
        =============== ===================================================================

        =============== ===================================================================
        Derivative Var  Documentation
        =============== ===================================================================
        de              variation of energy  with respect to time
        dp              variation of the battery power with respect to time
        =============== ===================================================================

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        emin            minimum energy (kWh)
        emax            maximal energy
        socmin          minimum soc
        socmax          maximal soc
        soc0            initial state
        socf            final state
        dpdmax          maximal discharging power
        dpcmax          maximal charging power
        pcmax           maximal charging power
        pdmax           maximal discharging power
        etac            charging efficiency
        etad            discharging efficiency
        =============== ===================================================================

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _soc_init       None
        _p_init         Initialize power
        _e_min          Minimal energy constraint
        _e_max          Maximal energy constraint
        _soc_final      Final soc constraint
        _soc_min        Minimal state of charge constraint
        _soc_max        Maximal state of charge constraint
        _dpdmax         Maximal varation of descharging power constraint
        _dpcmax         Maximal varation of charging power constraint
        _pdmax          Discharging power bound
        _pcmax          Charging power bound
        _p_balance      Power balance constraint
        _e_balance      Energy balance constraint
        =============== ===================================================================

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        outlet          output power of the battery (kW), using source convention
        =============== ===================================================================

        =============== ===================================================================
        Expressions     Documentation
        =============== ===================================================================
        soc             Expression of the state of charge
        =============== ===================================================================

        """

        super().__init__(*args, **kwargs)

        self.pd = Var(self.time, doc='discharging power', within=NonNegativeReals, initialize=0)
        self.pc = Var(self.time, doc='charging power', within=NonNegativeReals, initialize=0)
        self.u = Var(self.time, doc='binary variable', within=Binary, initialize=0)

        self.etac = Param(default=1.0, doc='charging efficiency', mutable=True)
        self.etad = Param(default=1.0, doc='discharging efficiency', mutable=True)

        self.del_component('_e_balance')
        self.del_component('_pmax')

        def _e_balance(m, t):
            if not (m.etac.value and m.etad.value == 1.):
                return m.de[t] == 1 / 3600 * (m.pc[t] * m.etac - m.pd[t] / m.etad)
            else:
                return m.de[t] == 1 / 3600 * (m.pc[t] - m.pd[t])

        def _p_balance(b, t):
            return b.p[t] - b.pd[t] + b.pc[t] == 0

        def _pdmax(b, t):
            if b.pdmax.value is None:
                return Constraint.Skip
            return b.pd[t] - b.u[t] * b.pdmax <= 0

        def _pcmax(b, t):
            if b.pcmax.value is None:
                return Constraint.Skip
            return b.pc[t] + b.u[t] * b.pcmax <= b.pcmax

        self._pdmax = Constraint(self.time, rule=_pdmax, doc='Discharging power bound')
        self._pcmax = Constraint(self.time, rule=_pcmax, doc='Charging power bound')
        self._p_balance = Constraint(self.time, rule=_p_balance, doc='Power balance constraint')
        self._e_balance = Constraint(self.time, rule=_e_balance, doc='Energy balance constraint')


class BatteryV3(BatteryV2):
    """
    Bilinear battery Model.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge.
    Efficiency for charge and discharge are considered.
    It exposes one power port using source convention.
    """

    def __init__(self, *args, **kwargs):
        """
        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p               energy derivative with respect to time
        e               energy in battery
        pd              discharging power
        pc              charging power
        u               binary variable
        =============== ===================================================================

        =============== ===================================================================
        Derivative Var  Documentation
        =============== ===================================================================
        de              variation of energy  with respect to time
        dp              variation of the battery power with respect to time
        =============== ===================================================================

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        emin            minimum energy (kWh)
        emax            maximal energy
        socmin          minimum soc
        socmax          maximal soc
        soc0            initial state
        socf            final state
        dpdmax          maximal discharging power
        dpcmax          maximal charging power
        pcmax           maximal charging power
        pdmax           maximal discharging power
        etac            charging efficiency
        etad            discharging efficiency
        =============== ===================================================================

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _soc_init       None
        _p_init         Initialize power
        _e_min          Minimal energy constraint
        _e_max          Maximal energy constraint
        _soc_final      Final soc constraint
        _soc_min        Minimal state of charge constraint
        _soc_max        Maximal state of charge constraint
        _dpdmax         Maximal varation of descharging power constraint
        _dpcmax         Maximal varation of charging power constraint
        _pdmax          Discharging power bound
        _pcmax          Charging power bound
        _p_balance      Power balance constraint
        _e_balance      Energy balance constraint
        =============== ===================================================================

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        outlet          output power of the battery (kW), using source convention
        =============== ===================================================================

        =============== ===================================================================
        Expressions     Documentation
        =============== ===================================================================
        soc             Expression of the state of charge
        =============== ===================================================================

        """

        super().__init__(*args, **kwargs)

        # # TODO : rainflow counting method

        self.nbrcycles = Integral(self.time, wrt=self.time, rule=lambda m, t: 1/(m.emax)*(m.etac*m.pc[t] + m.pd[t]/m.etad)/3600)

        @self.Expression(self.time)
        def cycles(m, t):

            return 1 / m.emax / 3600 / 2 * sum([(m.etac * m.pc[m.time[idx + 1]] + m.pd[m.time[idx + 1]] / m.etad
                + m.etac * m.pc[m.time[idx + 2]] + m.pd[m.time[idx + 2]] / m.etad) * (m.time[idx + 2] - m.time[idx + 1])
                                                for (idx, tmp) in enumerate(m.time) if tmp < t if idx + 1 >= 0])

        add_phase(self, prefix='2', name='absorption phase')
        add_phase(self, prefix='3', name='float phase')

        self.add_component(f'mut3', Param(initialize=2, doc=f'minimal duration of the up time for float phase (h)'))
        self.add_component(f'mdt3', Param(initialize=2, doc=f'minimal duration of the down time for float phase (h)'))

        self.u1 = Var(self.time, within=Binary)

        @self.Constraint(self.time, doc='charging phase is during bulk, absorption or floating phases')
        def _bulk_pahse(m, t):
            return m.u1[t] + m.u2[t] + m.u3[t], 1 - m.u[t]

        # @self.Constraint(self.time)
        # def _absorption_phase(m, t):
        #     return 0, m.u[t] + m.u2[t], 1
        #
        # @self.Constraint(self.time)
        # def _float_phase(m, t):
        #     return 0, m.u[t] + m.u3[t], 1

        # redefining the constraint _soc_max such that when u1 = 1, 0 < soc < 100 and when u1 = 0, 0 < soc < socmax
        del self._soc_max
        del self._soc_min

        @self.Constraint(self.time, doc='maximal soc constraint')
        def _soc_max(m, t):
            return m.e[t]*100/m.emax <= 90*m.u1[t] + 100*(m.u3[t] + m.u2[t] + m.u[t])

        @self.Constraint(self.time, doc='minimal soc constraint')
        def _soc_min(m, t):
            return m.e[t]*100/m.emax >= 100*m.u3[t] + 90*m.u2[t] + 40*m.u[t]

        # case where floating phase is not every time followed by a floating phase:
        @self.Constraint(self.time, doc='')
        def _sequence_2_3(m, t):
            return m.sd2[t] >= m.su3[t]  # equality constraint if always floating phase

        from numpy import arange

        # @self.Constraint(self.time, doc='minimal time for the full recharging sequence (h)')
        # def _min_t_up2(m, t):
        #     for (i, tmp) in enumerate(sorted(m.time)):
        #         if t == tmp:
        #             idx = i + 1
        #             if idx <= 1 or tmp == m.time.last():
        #                 return Constraint.Skip
        #             else:
        #                 return sum([m.su2[m.time[idx - i]] for i in arange(len(m.time) + 1)
        #                             if idx - i >= 1 if m.time[idx - i] >= m.time[idx] - m.mut2 * 3600])
        #                             <= m.u2[m.time[idx]]

        @self.Constraint(self.time, doc='minimal time for the full recharging sequence (h)')
        def _min_t_up3(m, t):
            if m.mut3.value is None:
                return Constraint.Skip
            else:
                for (i, tmp) in enumerate(sorted(m.time)):
                    if t == tmp:
                        idx = i + 1
                        if idx <= 1 or tmp == m.time.last():
                            return Constraint.Skip
                        else:
                            return sum([m.su3[m.time[idx - i]] for i in arange(len(m.time) + 1)
                                        if idx - i >= 1 if m.time[idx - i] >= m.time[idx] - m.mut3 * 3600]) \
                                   <= m.u3[m.time[idx]]

        @self.BuildAction(doc='Hack for the last index of the expression using index and time.')
        def _build_action(m):
            del (m._start1_3[m.time.last()])
            del (m._stop3_3[m.time.last()])
            del (m._start4_3[m.time.last()])
            del (m._start1_2[m.time.last()])
            del (m._stop3_2[m.time.last()])
            del (m._start4_2[m.time.last()])
            del (m.cycles[m.time.last()])
        #
        # Controlling the number of float_phases
        # TODO find a way to properly update the passed state of the variables cycle_passed, u1, sd1, su1
        self.cycle_passed = Param(initialize=0, doc='passed cycles of the battery')
        self.max_cycles = Param(initialize=10, doc='maximal number of cycle between two full charge sequence')

        # @self.Constraint(self.time, doc='Imposes a full recharge at least every 25 cycles')
        # def _nbr_charge_complete2(m, t):
        #     if t == m.time.last():
        #         return Constraint.Skip
        #     return m.cycles[t] + m.cycle_passed <= m.max_cycles*(1 + sum([m.sd3[i] for i in m.time if i <= t if i > m.time.first()]))

        @self.Constraint(self.time, doc='Imposes a full recharge at least every 25 days')
        def _nbr_charge_complete3(m, t):
            if t == m.time.last():
                return Constraint.Skip
            else:
                return t/3600/24, m.max_cycles*(1 + sum([m.su3[i] for i in m.time if i <= t if i > m.time.first()]))\
                       - m.cycle_passed, None


        #
        # if 0:
        #
        #     from pyomo.environ import Piecewise
        #
        #     self.voc = Var(self.time, within=NonNegativeReals, bounds=(35, 53))
        #     del self.soc
        #     self.soc = Var(self.time, within=NonNegativeReals, bounds=(0, 100))
        #
        #     @self.Constraint(self.time)
        #     def _s(m, t):
        #         return m.soc[t] == 100 * m.e[t] / m.emax
        #
        #     self.SOC = Set(initialize=[0, 10, 40, 50, 75, 80, 85, 90, 95, 100])
        #
        #     self._voc_soc = Piecewise(self.time, self.voc, self.soc,
        #                               pw_pts=[0, 40, 90, 100],
        #                               pw_repn='SOS2',
        #                               pw_constr_type='EQ',
        #                               f_rule=lambda m, t, x: vod_soc_lead_acid_gel(x))


def add_phase(self, prefix='1', name='new phase', start_up=True, shut_down=True):

    self.add_component(f'u{prefix}',   Var(self.time, within=Binary, doc=f'{name} is running'))
    self.add_component(f'su{prefix}',  Var(self.time, within=Binary, doc=f'starting of {name}'))
    self.add_component(f'sd{prefix}',  Var(self.time, within=Binary, doc=f'stoping of {name}'))
    self.add_component(f'mu{prefix}',  Var(self.time, within=Binary, doc=f'intermediary binary variable for the '
                                                                         f'starting-up of {name}.'))
    self.add_component(f'md{prefix}',  Var(self.time, within=Binary, doc=f'intermediary binary variable for the'
                                                                         f' shutting down of {name}.'))

    def _start1(m, t):
        u  = m.find_component(f'u{prefix}')
        su = m.find_component(f'su{prefix}')

        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return u[m.time[idx]] - u[m.time[idx - 1]] <= su[m.time[idx]]
        else:
            return Constraint.Skip
    self.add_component(f'_start1_{prefix}',
                       Constraint(self.time, rule=_start1, doc=f'start up constraint 1 for {name}'))

    def _start2(m, t):
        su = m.find_component(f'su{prefix}')
        mu = m.find_component(f'mu{prefix}')
        return su[t] <= mu[t]

    self.add_component(f'_start2_{prefix}',
                       Constraint(self.time, rule=_start2, doc=f'start up constraint 2 for {name}'))

    def _start3(m, t):
        mu = m.find_component(f'mu{prefix}')
        u  = m.find_component(f'u{prefix}')
        return mu[t] <= u[t]

    self.add_component(f'_start3_{prefix}',
                       Constraint(self.time, rule=_start3, doc=f'start up constraint 3 for {name}'))

    def _start4(m, t):
        mu = m.find_component(f'mu{prefix}')
        u  = m.find_component(f'u{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return mu[m.time[idx]] <= 1 - u[m.time[idx - 1]]

    self.add_component(f'_start4_{prefix}',
                       Constraint(self.time, rule=_start4, doc=f'start up constraint 4 for {name}'))

    def _stop1(m, t):
        u  = m.find_component(f'u{prefix}')
        sd = m.find_component(f'sd{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return u[m.time[idx - 1]] - u[m.time[idx]] <= sd[m.time[idx]]
        else:
            return Constraint.Skip

    self.add_component(f'_stop1_{prefix}',
                       Constraint(self.time, rule=_stop1, doc=f'shutting down constraint 1 for  {name}'))

    def _stop2(m, t):
        md = m.find_component(f'md{prefix}')
        sd = m.find_component(f'sd{prefix}')
        return sd[t] <= md[t]

    self.add_component(f'_stop2_{prefix}',
                       Constraint(self.time, rule=_stop2, doc=f'shutting down constraint 2 for {name}'))

    def _stop3(m, t):
        md = m.find_component(f'md{prefix}')
        u  = m.find_component(f'u{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return md[t] <= u[m.time[idx - 1]]

    self.add_component(f'_stop3_{prefix}',
                       Constraint(self.time, rule=_stop3, doc=f'shutting down constraint 3 for {name}'))

    def _stop4(m, t):
        md = m.find_component(f'md{prefix}')
        u  = m.find_component(f'u{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return md[m.time[idx]] <= 1 - u[m.time[idx]]

    self.add_component(f'_stop4_{prefix}',
                       Constraint(self.time, rule=_stop4, doc=f'shutting down constraint 4 for {name}'))


def vod_soc_lead_acid_gel(soc):
    from numpy import exp
    return 50 - 0.08*(100-soc) + 3*exp(-(100-soc)/4) - exp(((100-soc) - 85)/5)


class NLBattery(DynUnit):
    """
    Non linear Battery model in development

    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.u = Var(self.time, doc='voltage', initialize=0)
        self.i = Var(self.time, doc='current', initialize=0)
        self.ind_ocv = Set(initialize=[0, 50, 100], doc='index for ocv vector')
        self.ocv = Param(self.time, )  # todo here
        self.e = Var(self.time, doc='energy in battery', initialize=0)

        # TODO : model and tests
        # self.emin   = Param(default=0,       doc='minimum energy (kWh)',       mutable=True, within=NonNegativeReals)
        # self.emax   = Param(default=UB,      doc='maximal energy',             mutable=True)
        # self.e0     = Param(default=None,    doc='initial state',              mutable=True)
        # self.ef     = Param(default=None,    doc='final state',                mutable=True)
        # self.etac   = Param(default=1.0,     doc='charging efficiency',        mutable=True)
        # self.etad   = Param(default=1.0,     doc='discharging efficiency',     mutable=True)
        # self.dpdmax = Param(default=UB,      doc='maximal discharging power',  mutable=True)
        # self.dpcmax = Param(default=UB,      doc='maximal charging power',     mutable=True)
        #
        # self.pcmax  = Param(default=UB,      doc='maximal charging power',     mutable=True, within=PositiveReals)
        # self.pdmax  = Param(default=UB,      doc='maximal discharging power',  mutable=True, within=PositiveReals)
        #
        # self.de     = DerivativeVar(self.e, wrt=self.time, initialize=0,
        #                             doc='variation of energy  with respect to time')
        # self.dp     = DerivativeVar(self.p, wrt=self.time, initialize=0,
        #                             doc='variation of the battery power with respect to time',
        #                             bounds=lambda m, t: (-m.dpcmax, m.dpdmax))
        #
        # self.outlet = Port(initialize={'f': (self.p, Port.Conservative)})
