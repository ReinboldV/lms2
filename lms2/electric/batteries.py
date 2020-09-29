# -*- coding: utf-8 -*-
"""
Batteries' Module.

Contains electrical batteries linear models.
"""

from pyomo.core.kernel.set_types import NonNegativeReals, Binary
from pyomo.dae.diffvar import DerivativeVar
from pyomo.environ import Constraint, Var, Param, Expression, PositiveReals, Set
from pyomo.network import Port

from lms2 import DynUnit
from lms2.logical.sequencial import add_phase

import logging

logger = logging.getLogger('lms2.batteries')

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

        @self.Constraint(self.time, doc='Energy balance constraint')
        def _e_balance(m, t):
            return m.de[t] == 1 / 3600 * (m.pc[t] * m.etac - m.pd[t] / m.etad)

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


class BatteryV3(BatteryV2):
    """
    Bilinear battery Model.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge.
    Efficiency for charge and discharge are considered.
    It exposes one power port using source convention.
    """

    def __init__(self, *args, voc_rule=None, method='constant', **kwargs):
        """
        =============== =============== =====================================================================
        Name            Type            Documentation
        =============== =============== =====================================================================
        abs_dp          Var             Absolute value of variable dp
        e               Var             energy in battery
        md2             Var             intermediary binary variable for the shutting down of absorption phase.
        md3             Var             intermediary binary variable for the shutting down of float phase.
        mu2             Var             intermediary binary variable for the starting-up of absorption phase.
        mu3             Var             intermediary binary variable for the starting-up of float phase.
        p               Var             energy derivative with respect to time
        pc              Var             charging power
        pd              Var             discharging power
        pw_u            Var             Intermediary binary variable for SOS2 modelling of voc/soc/pcmax
        sd2             Var             stoping of absorption phase
        sd3             Var             stoping of float phase
        soc_w           Var             Intermediary weight variable for SOS2 modelling of voc/soc/pcmax
        su2             Var             starting of absorption phase
        su3             Var             starting of float phase
        u               Var             binary variable
        u1              Var             bulk charging phase
        u2              Var             absorption phase is running
        u3              Var             float phase is running
        voc             Var             open circuit voltage (V)
        pw_i            Set             piecewise breakpoint index
        pw_j            Set             piecewise binary index
        pw_u_index      Set             None
        soc_w_index     Set             None
        outlet          Port            output power of the battery (kW), using source convention
        cycle_passed    Param           passed cycles of the battery
        dp_cost         Param           cost associated to the absolute value of dp (euros/kWh)
        dpcmax          Param           maximal charging power
        dpdmax          Param           maximal discharging power
        emax            Param           maximal energy
        emin            Param           minimum energy (kWh)
        etac            Param           charging efficiency
        etad            Param           discharging efficiency
        max_cycles      Param           maximal number of cycle between two full charge sequence
        mdt3            Param           minimal duration of the down time for float phase (h)
        mut3            Param           minimal duration of the up time for float phase (h)
        pcmax           Param           maximal charging power
        pdmax           Param           maximal discharging power
        pfloat          Param           Float Phase, losses (kW)
        pinit           Param           initial output power of the battery (default : None)
        pw_pcmax        Param           Corresponding Pcmax points for SOS2 modelling
        pw_soc          Param           SOC points for SOS2 modelling
        pw_voc          Param           Corresponding VOC points for SOS2 modelling
        soc0            Param           initial state
        socabs          Param           Absorption phase : soc lower limit
        socf            Param           final state
        socmax          Param           maximal soc
        socmin          Param           minimum soc
        cycles          Expression      Number of cycles
        inst_cost       Expression      instantaneous bilinear cost (euros/s), associated with variable dp
        soc             Expression      Expression of the state of charge
        de              DerivativeVar   variation of energy  with respect to time
        dp              DerivativeVar   variation of the battery power with respect to time
        time            ContinuousSet   Time continuous set (s)
        _bound1         Constraint      absolute value constraint 1
        _bound2         Constraint      absolute value constraint 2
        _bulk_phase     Constraint      charging phase is during bulk, absorption or floating phases
        _dpcmax         Constraint      Maximal varation of charging power constraint
        _dpdmax         Constraint      Maximal varation of descharging power constraint
        _e_balance      Constraint      Energy balance constraint
        _e_max          Constraint      Maximal energy constraint
        _e_min          Constraint      Minimal energy constraint
        _min_t_up3      Constraint      minimal time for the full recharging sequence (h)
        _nbr_charge     Constraint      Imposes a full recharge at least every 25 days
        _p_balance      Constraint      Power balance constraint
        _p_init         Constraint      Initialize power
        _pcmax          Constraint      Charging power bound
        _pdmax          Constraint      Discharging power bound
        _sequence_2_3   Constraint      floating phase only after absorption phase
        _soc_final      Constraint      Final soc constraint
        _soc_init       Constraint      initial state of charge
        _soc_max        Constraint      maximal soc constraint
        _soc_min        Constraint      minimal soc constraint
        _sos2_pcm2      Constraint      SOS2 constraint on pcm
        _sos2_voc1      Constraint      SOS2 constraint on voc
        _sos2_voc2      Constraint      SOS2 constraint on voc
        _sos2_voc3      Constraint      SOS2 constraint on voc
        _sos2_voc4      Constraint      SOS2 constraint on voc
        _sos2_voc5      Constraint      SOS2 constraint on voc
        _start1_2       Constraint      start up constraint 1 for absorption phase
        _start1_3       Constraint      start up constraint 1 for float phase
        _start2_2       Constraint      start up constraint 2 for absorption phase
        _start2_3       Constraint      start up constraint 2 for float phase
        _start3_2       Constraint      start up constraint 3 for absorption phase
        _start3_3       Constraint      start up constraint 3 for float phase
        _start4_2       Constraint      start up constraint 4 for absorption phase
        _start4_3       Constraint      start up constraint 4 for float phase
        _stop1_2        Constraint      shutting down constraint 1 for  absorption phase
        _stop1_3        Constraint      shutting down constraint 1 for  float phase
        _stop2_2        Constraint      shutting down constraint 2 for absorption phase
        _stop2_3        Constraint      shutting down constraint 2 for float phase
        _stop3_2        Constraint      shutting down constraint 3 for absorption phase
        _stop3_3        Constraint      shutting down constraint 3 for float phase
        _stop4_2        Constraint      shutting down constraint 4 for absorption phase
        _stop4_3        Constraint      shutting down constraint 4 for float phase
        _build_action   BuildAction     Hack for the last index of the expression using index and time.
        =============== =============== =====================================================================


        :type ocv_rule: Method that return the open circuit voltage with respect to the state of charge.
        This function is used to compute power profile during absorption phase and floating phase.

        """

        super().__init__(*args, **kwargs)

        if method not in ['piecewise', 'constant']:
            raise ValueError(f'method for calculating open circuit voltage should be either '
                             f'`piecewise` or `constant`, but is actually {method}')
        else:
            self.method = method

        add_phase(self, prefix='2', name='absorption phase')
        add_phase(self, prefix='3', name='float phase')

        self.voc_rule = voc_rule

        self.mut3   = Param(initialize=4,       doc=f'minimal duration of the up time for float phase (h)')
        self.mdt3   = Param(initialize=2,       doc=f'minimal duration of the down time for float phase (h)')
        self.socabs = Param(initialize=85,      doc='Absorption phase : soc lower limit')
        self.pfloat = Param(initialize=0.250,   doc='Float Phase, losses (kW)')
        self.u1 = Var(self.time, within=Binary, doc='bulk charging phase')

        # #############################
        # OCV modeling
        # #############################

        if self.method == 'piecewise':
            self.pw_i     = Set(initialize=[1, 2, 3], ordered=True, doc='piecewise breakpoint index')
            self.pw_j     = Set(initialize=[1, 2], ordered=True, doc='piecewise binary index')
            self.voc      = Var(self.time, within=NonNegativeReals, doc='open circuit voltage (V)')
            self.soc_w    = Var(self.pw_i, self.time, bounds=(0, 1),
                                doc='Intermediary weight variable for SOS2 modelling of voc/soc/pcmax')
            self.pw_u     = Var(self.pw_j, self.time, within=Binary,
                                doc='Intermediary binary variable for SOS2 modelling of voc/soc/pcmax')
            self.pw_soc   = Param(self.pw_i, initialize={1: 40, 2: 85, 3: 100}, doc='SOC points for SOS2 modelling')

            pw_voc_default = {1: 49.5, 2: 51, 3: 56}

            def init_pw_voc(m, pw_i):
                if voc_rule is not None and callable(voc_rule):
                    return voc_rule(m.pw_soc[pw_i])
                    logger.info('Using `voc_rule` for open circuit voltage computation. '
                                   'Initial value of pw_voc are not used. ')
                else:
                    return pw_voc_default[pw_i]

            self.pw_voc = Param(self.pw_i, initialize=init_pw_voc,
                                doc='Corresponding VOC points for SOS2 modelling')
            self.pw_pcmax = Param(self.pw_i, initialize={1: 20, 2: 20, 3: 2},
                                  doc='Corresponding Pcmax points for SOS2 modelling')

            @self.Constraint(self.time, doc='SOS2 constraint on voc')
            def _sos2_voc1(m, t):
                return sum([m.soc_w[i, t] for i in m.pw_i]), 1

            @self.Constraint(self.time, doc='SOS2 constraint on pcm')
            def _sos2_pcm2(m, t):
                return sum([m.soc_w[i, t]*m.pw_pcmax[i] for i in m.pw_i]) >= m.pc[t]

            @self.Constraint(self.time, doc='SOS2 constraint on voc')
            def _sos2_voc2(m, t):
                return sum([m.soc_w[i, t]*m.pw_soc[i] for i in m.pw_i]), m.soc[t]

            @self.Constraint(self.time, doc='SOS2 constraint on voc')
            def _sos2_voc3(m, t):
                return sum([m.soc_w[i, t] * m.pw_voc[i] for i in m.pw_i]), m.voc[t]

            @self.Constraint(self.pw_i, self.time, doc='SOS2 constraint on voc')
            def _sos2_voc4(m, i, t):
                if i == m.pw_i.first():
                    return m.soc_w[i, t] <= m.pw_u[i, t]
                elif i == m.pw_i.last():
                    return m.soc_w[i, t] <= m.pw_u[i-1, t]
                else:
                    return m.soc_w[i, t] <= m.pw_u[i-1, t] + m.pw_u[i, t]

            @self.Constraint(self.time, doc='SOS2 constraint on voc')
            def _sos2_voc5(m, t):
                return sum([m.pw_u[j, t] for j in m.pw_j]), 1

        # ################################
        # SOC upper and lower constraint
        # ################################

        # redefining the constraint _soc_max such that when u2 = 1, 0 < soc < 100 and when u1 = 1, 0 < soc < socmax
        del self._soc_max
        del self._soc_min

        @self.Constraint(self.time, doc='maximal soc constraint')
        def _soc_max(m, t):
            return m.soc[t] <= m.socabs*m.u1[t] + m.socmax*(m.u3[t] + m.u2[t] + m.u[t])

        @self.Constraint(self.time, doc='minimal soc constraint')
        def _soc_min(m, t):
            return m.soc[t] >= m.socmax*m.u3[t] + m.socabs*m.u2[t] + m.socmin*(m.u[t]+m.u1[t])

        # #############################
        # Bulk phase modeling
        # #############################

        @self.Constraint(self.time, doc='charging phase is during bulk, absorption or floating phases')
        def _bulk_phase(m, t):
            return m.u1[t] + m.u2[t] + m.u3[t], 1 - m.u[t]

        # #############################
        # Absorption phase modeling
        # #############################
        #  Absorption phase is modelled  by mean of the maximal charging power.
        #  During abs phase, Battery voltage is fixed to a over-voltage Umax.
        #  Thus the battery current is fixed by Umax = VOC - RI <=>  I = (Umax - VOC)/R
        #  And P = Umax²/R - VOC*Umax/R.
        #  Thus, one just have to compute the coordinates of the points pw_soc and pw_pcmax,
        #  so that the behaviour is equivalent to having fixed Umax
        #  note that we are imposing pc < Umax²/R - VOC*Umax/R

        # #############################
        # Floating  phase modeling
        # #############################
        del self._p_balance

        @self.Constraint(self.time, doc='Power balance constraint')
        def _p_balance(b, t):
            return b.p[t] - b.pd[t] + b.pc[t] + b.u3[t] * b.pfloat == 0

        # case where floating phase is not every time followed by a floating phase:
        @self.Constraint(self.time, doc='floating phase only after absorption phase')
        def _sequence_2_3(m, t):
            return m.sd2[t] >= m.su3[t]  # equality constraint if always floating phase

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
                            return sum([m.su3[m.time[idx - i]] for i in range(len(m.time) + 1)
                                        if idx - i >= 1 if m.time[idx - i] >= m.time[idx] - m.mut3 * 3600]) \
                                   <= m.u3[m.time[idx]]

        # #############################
        # Cycling modeling
        # #############################

        # TODO find a way to properly update the passed state of the variables cycle_passed, u1, sd1, su1
        self.cycle_passed = Param(initialize=0, doc='passed cycles of the battery')
        self.max_cycles = Param(initialize=10, doc='maximal number of cycle between two full charge sequence')

        @self.Expression(self.time)
        def cycles(m, t):
            return 1 / m.emax / 3600 / 2 * sum([(m.etac * m.pc[m.time[idx + 1]] + m.pd[m.time[idx + 1]] / m.etad
                                                 + m.etac * m.pc[m.time[idx + 2]] + m.pd[m.time[idx + 2]] / m.etad) * (
                                                            m.time[idx + 2] - m.time[idx + 1])
                                                for (idx, tmp) in enumerate(m.time) if tmp < t if idx + 1 >= 0])

        @self.Constraint(self.time, doc='Imposes a full recharge at least every 25 days')
        def _nbr_charge(m, t):
            if t == m.time.last():
                return Constraint.Skip
            else:
                return t/3600/24, m.max_cycles*(1 + sum([m.su3[i] for i in m.time if i <= t if i > m.time.first()]))\
                       - m.cycle_passed, None

        @self.BuildAction(doc='Hack for the last index of the expression using index and time.')
        def _build_action(m):
            del (m._start1_3[m.time.last()])
            del (m._stop3_3[m.time.last()])
            del (m._start4_3[m.time.last()])
            del (m._start1_2[m.time.last()])
            del (m._stop3_2[m.time.last()])
            del (m._start4_2[m.time.last()])
            del (m.cycles[m.time.last()])


def voc_rule_lead_acid_gel(soc):
    from numpy import exp
    return 50 - 0.08 * (100 - soc) + 1.1 * exp(-(100 - soc) / 10) - exp(((100 - soc) - 85) / 10)


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
