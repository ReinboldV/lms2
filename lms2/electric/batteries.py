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

__all__ = ['BatteryV0', 'BatteryV1', 'AbsBatteryV2']

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


    **Variables:**

    - p           energy derivative with respect to time
    - e           energy in battery

    **DerivativeVar:**

    - de          variation of energy  with respect to time
    - dp          variation of the battery power with respect to time

    **Param:**

    - emin        minimum energy (kWh)
    - emax        maximal energy
    - e0          initial state
    - ef          final state
    - etac        charging efficiency
    - etad        discharging efficiency
    - dpdmax      maximal discharging power
    - dpcmax      maximal charging power
    - pcmax       maximal charging power
    - pdmax       maximal discharging power

    **Constraints:**

    - _e_balance  Energy balance constraint
    - _p_init     Initialize power
    - _e_initial  Initial energy constraint
    - _e_final    Final stored energy constraint
    - _e_min      Minimal energy constraint
    - _e_max      Maximal energy constraint
    - _pmax       Power bounds constraint
    - _dpdmax     Maximal varation of descharging power constraint
    - _dpcmax     Maximal varation of charging power constraint

    **Ports:**

    - outlet

    """

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)

        self.p = Var(self.time, doc='energy derivative with respect to time', initialize=0)
        self.e = Var(self.time, doc='energy in battery', initialize=0)

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

        self.outlet = Port(initialize={'f': (self.p, Port.Conservative)})

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

    Variables:

        - p           energy derivative with respect to time
        - e           energy in battery

    DerivativeVar:

        - de          variation of energy  with respect to time
        - dp          variation of the battery power with respect to time

    Param:

        - emin        minimum energy (kWh)
        - emax        maximal energy
        - socmin      minimum soc
        - socmax      maximal soc
        - soc0        initial state
        - socf        final state
        - dpdmax      maximal discharging power
        - dpcmax      maximal charging power
        - pcmax       maximal charging power
        - pdmax       maximal discharging power

    Constraints:

        - _e_balance  Energy balance constraint
        - _p_init     Initialize power
        - _e_min      Minimal energy constraint
        - _e_max      Maximal energy constraint
        - _soc_init   Initial soc constraint
        - _soc_final  Final soc constraint
        - _soc_min    Minimal state of charge constraint
        - _soc_max    Maximal state of charge constraint
        - _pmax       Power bounds constraint
        - _dpdmax     Maximal varation of descharging power constraint
        - _dpcmax     Maximal varation of charging power constraint

    Ports:

    - outlet

    Expressions:

    - soc         Expression of the state of charge


    """

    def __init__(self, *args, **kwds):
        """
        **Blocks:**

        Sets:

        **Variables:**
            - p                energy derivative with respect to time
            - e                energy in battery
            - pd               discharging power
            - pc               charging power
            - u                binary variable

        **DerivativeVar:**

            - de               variation of energy  with respect to time
            - dp               variation of the battery power with respect to time

        **Param:**

            - emin             minimum energy (kWh)
            - emax             maximal energy
            - socmin           minimum soc
            - socmax           maximal soc
            - soc0             initial state
            - socf             final state
            - dpdmax           maximal discharging power
            - dpcmax           maximal charging power
            - pcmax            maximal charging power
            - pdmax            maximal discharging power
            - etac             charging efficiency
            - etad             discharging efficiency

        **Constraints:**
            - _soc_init        None
            - _p_init          Initialize power
            - _e_min           Minimal energy constraint
            - _e_max           Maximal energy constraint
            - _soc_final       Final soc constraint
            - _soc_min         Minimal state of charge constraint
            - _soc_max         Maximal state of charge constraint
            - _dpdmax          Maximal varation of descharging power constraint
            - _dpcmax          Maximal varation of charging power constraint
            - _pdmax           Discharging power bound
            - _pcmax           Charging power bound
            - _p_balance       Power balance constraint
            - _e_balance       Energy balance constraint

        **Ports:**

            - outlet           output power of the battery (kW), using source convention

        **Expressions:**

            - soc              Expression of the state of charge


        :param args:
        :param kwds:
        """
        super().__init__(*args, **kwds)

        self.emin = Param(default=0, doc='minimum energy (kWh)', mutable=True, within=NonNegativeReals)
        self.emax = Param(default=UB, doc='maximal energy', mutable=True)
        self.socmin = Param(default=0, doc='minimum soc', mutable=True)
        self.socmax = Param(default=100, doc='maximal soc', mutable=True)
        self.soc0 = Param(default=50, doc='initial state', mutable=True)
        self.socf = Param(default=None, doc='final state', mutable=True)
        self.dpdmax = Param(default=UB, doc='maximal discharging power', mutable=True)
        self.dpcmax = Param(default=UB, doc='maximal charging power', mutable=True)
        self.pcmax = Param(default=UB, doc='maximal charging power', mutable=True, within=PositiveReals)
        self.pdmax = Param(default=UB, doc='maximal discharging power', mutable=True, within=PositiveReals)

        def _init_e(m, t):
            return m.soc0 * m.emax / 100

        self.p = Var(self.time, doc='energy derivative with respect to time', initialize=0)
        self.e = Var(self.time, doc='energy in battery', initialize=_init_e)

        self.de = DerivativeVar(self.e, wrt=self.time, initialize=0, doc='variation of energy  with respect to time')
        self.dp = DerivativeVar(self.p, wrt=self.time, initialize=0,
                                doc='variation of the battery power with respect to time',
                                bounds=lambda m, t: (-m.dpcmax, m.dpdmax))

        self.outlet = Port(initialize={'f': (self.p, Port.Conservative)}, doc='output power of the battery (kW), '
                                                                              'using source convention')

        def _p_init(m, t):
            if t == m.time.bounds()[0]:
                return m.p[t] == 0
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

        @self.Constraint(self.time)
        def _soc_init(m, t):
            if m.soc0.value is not None:
                if t == m.time.first():
                    return m.e[t] == m.soc0 * m.emax / 100
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


class AbsBatteryV2(BatteryV1):
    """
    Bilinear battery Model.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge.
    Efficiency for charge and discharge are considered.
    It exposes one power port using source convention.
    """

    def __init__(self, *args, **kwargs):

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


class NLBattery(DynUnit):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.u = Var(self.time, doc='voltage', initialize=0)
        self.i = Var(self.time, doc='current', initialize=0)
        self.ind_ocv = Set(initialize=[0, 50, 100], doc='index for ocv vector')
        self.ocv = Param(self.time, )  # todo here
        self.e = Var(self.time, doc='energy in battery', initialize=0)

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
