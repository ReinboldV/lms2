# -*- coding: utf-8 -*-
"""
Batteries' Module.

Contains electrical batteries linear models.
"""

from pyomo.core import NonNegativeReals, Binary, PositiveReals, Reals, Any
from pyomo.dae import DerivativeVar, ContinuousSet
from pyomo.environ import Constraint, Var, Param, Expression, Set
from pyomo.network import Port

import logging

logger = logging.getLogger('lms2.batteries')

__all__ = ['battery_V0', 'battery_v1', 'battery_v2']

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


#   TODO  : model of ageing.

def battery_V0(bat, **options):
    """
    Battery with ideal efficiency.

    This battery is limited in power, variation of power and energy. One can fix initial and final stored energy.
    For fixing initial en final state of charge, consider using `AbsBatteryV1`.
    It exposes one power port using source convention.


    .. table::
        :width: 100%

        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p               energy derivative with respect to time
        e               energy in battery
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Derivative Var  Documentation
        =============== ===================================================================
        de              variation of energy  with respect to time
        dp              variation of the battery power with respect to time
        =============== ===================================================================

    .. table::
        :width: 100%

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

    .. table::
        :width: 100%

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

    .. table::
        :width: 100%

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        outlet          None
        =============== ===================================================================

    """
    time = options.pop('time', ContinuousSet(bounds=(0, 1)))

    bat.p = Var(time, doc='Output power of the battery (kW)', initialize=0)  #: initial value: par1
    bat.e = Var(time, doc='Energy in battery (kWh)', initialize=0)

    bat.emin = Param(default=0, doc='minimum energy (kWh)', mutable=True, within=NonNegativeReals)
    bat.emax = Param(default=UB, doc='maximal energy', mutable=True, within=Reals)
    bat.e0 = Param(default=None, doc='initial state', mutable=True, within=Any)
    bat.ef = Param(default=None, doc='final state', mutable=True, within=Any)
    bat.etac = Param(default=1.0, doc='charging efficiency', mutable=False, within=Reals)
    bat.etad = Param(default=1.0, doc='discharging efficiency', mutable=False, within=Reals)
    bat.dpdmax = Param(default=UB, doc='maximal discharging power', mutable=True, within=Reals)
    bat.dpcmax = Param(default=UB, doc='maximal charging power', mutable=True, within=Reals)
    bat.pcmax = Param(default=UB, doc='maximal charging power', mutable=True, within=PositiveReals)
    bat.pdmax = Param(default=UB, doc='maximal discharging power', mutable=True, within=PositiveReals)

    bat.de = DerivativeVar(bat.e, wrt=bat.time, initialize=0,
                           doc='variation of energy  with respect to time')
    bat.dp = DerivativeVar(bat.p, wrt=bat.time, initialize=0,
                           doc='variation of the battery power with respect to time',
                           bounds=lambda m, t: (-m.dpcmax, m.dpdmax))

    bat.outlet = Port(initialize={'f': (bat.p, Port.Extensive, {'include_splitfrac': False})})

    def _p_init(m, t):
        if t == time.bounds()[0]:
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
        if t == time.last():
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

    bat._e_balance = Constraint(time, rule=_energy_balance, doc='Energy balance constraint')
    bat._p_init = Constraint(time, rule=_p_init, doc='Initialize power')
    bat._e_initial = Constraint(time, rule=_e_initial, doc='Initial energy constraint')
    bat._e_final = Constraint(time, rule=_e_final, doc='Final stored energy constraint')
    bat._e_min = Constraint(time, rule=_e_min, doc='Minimal energy constraint')
    bat._e_max = Constraint(time, rule=_e_max, doc='Maximal energy constraint')
    bat._pmax = Constraint(time, rule=_pmax, doc='Power bounds constraint')
    bat._dpdmax = Constraint(time, rule=_dpdmax, doc='Maximal varation of descharging power constraint')
    bat._dpcmax = Constraint(time, rule=_dpcmax, doc='Maximal varation of charging power constraint')

    return bat


def battery_v1(bat, **options):
    """
    Battery with ideal efficiency.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge. It exposes one power port using source convention.

    Instanciation options:
        - c_bat :       battery capacity (kWh)
        - c_bat_max :   battery maximal capacity, default : +inf (only if c_bat is None)
        - c_bat_min :   battery minimal capacity, default : 0 (only if c_bat is None)
        - p_max :       maximal charging power, default : +inf (>0)
        - p_min :       maximal descharging power, default : +inf (>0)
        - soc_min :     minimal soc, default : 0 (>0)
        - soc_max :     maximal soc, default : 100 (>0)
        - soc0 :        initial SOC, default: 50 (0<soc0<100)
        - socf :        final SOC, defalut: 50 (0<socf<100)

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               energy derivative with respect to time
    e               energy in battery
    emax            maximal energy (kWh), i.e. battery capacity.
                    Variable only if c_bat is not fixed in the options
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
    emax            maximal energy (kWh), it is a Parameter only if c_bat is given
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
    _soc_init       Initial State Of Charge
    _e_balance      Energy balance constraint
    _p_init         Initialize power
    _e_min          Minimal energy constraint
    _e_max          Maximal energy constraint
    _soc_final      Final soc constraint
    _soc_min        Minimal state of charge constraint
    _soc_max        Maximal state of charge constraint
    _pmax           Power bounds constraint
    _dpdmax         Maximal variation of descharging power constraint
    _dpcmax         Maximal variation of charging power constraint
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
    time = options.get('time', ContinuousSet(bounds=(0, 1)))

    c_bat       = options.pop('c_bat', None)
    c_bat_max   = options.pop('c_bat_max', UB)
    c_bat_min   = options.pop('c_bat_min', 0)
    p_max       = options.get('p_max', UB)
    p_min       = options.get('p_min', UB)
    soc_min     = options.pop('soc_min', 0)
    soc_max     = options.pop('soc_max', 100)
    soc0        = options.pop('soc0', 50)
    socf        = options.pop('socf', 50)

    if c_bat is None:
        assert c_bat_max is not None, 'User should either set c_bat or (c_bat_min and c_bat_max)'
        assert c_bat_min is not None, 'User should either set c_bat or (c_bat_min and c_bat_max)'
        assert c_bat_min < c_bat_max, "C'est pas malin..."
        bat.emax = Var(initialize=c_bat_min, doc='maximal energy', bounds=(c_bat_min, c_bat_max))
        bat.emin = Param(default=0, doc='minimum energy (kWh)', mutable=True, within=NonNegativeReals)
    else:
        c_bat_max = c_bat
        c_bat_min = c_bat
        assert c_bat >= 0, 'Battery capacity should not be negative'
        logger.info('options c_bat_min and c_bat_max have no effect since c_bat is fixed.')
        bat.emax = Param(default=c_bat, doc='maximal energy', mutable=True, within=Reals)
        bat.emin = Param(default=0, doc='minimum energy (kWh)', mutable=True, within=NonNegativeReals)

    bat.socmin = Param(default=soc_min, doc='minimum soc', mutable=True, within=Reals)
    bat.pinit  = Param(default=None,
                       doc='initial output power of the battery (default : None)', mutable=True, within=Any)
    bat.socmax = Param(default=soc_max, doc='maximal soc', mutable=True, within=Any)
    bat.soc0 = Param(default=soc0, doc='initial state', mutable=True, within=Any)
    bat.socf = Param(default=socf, doc='final state', mutable=True, within=Any)
    bat.dpdmax = Param(default=UB, doc='maximal discharging power', mutable=True, within=Reals)
    bat.dpcmax = Param(default=UB, doc='maximal charging power', mutable=True, within=Reals)
    bat.pcmax = Param(default=p_min, doc='maximal charging power', mutable=True, within=NonNegativeReals)
    bat.pdmax = Param(default=p_max, doc='maximal discharging power', mutable=True, within=NonNegativeReals)

    def _init_e(m, t):
        if m.soc0.value is not None:
            return m.soc0 * m.emax / 100
        else:
            return 50

    bat.p = Var(time, doc='energy derivative with respect to time', initialize=0)
    bat.e = Var(time, doc='energy in battery', initialize=_init_e, bounds=(0, c_bat_max))

    bat.de = DerivativeVar(bat.e, wrt=time, initialize=0, doc='variation of energy  with respect to time')
    bat.dp = DerivativeVar(bat.p, wrt=time, initialize=0, doc='variation of the battery power with respect to time',
                           bounds=lambda m, t: (-m.dpcmax, m.dpdmax))

    bat.outlet = Port(initialize={'f': (bat.p, Port.Extensive, {'include_splitfrac': False})},
                      doc='output power of the battery (kW), using source convention')

    # initializing pinit should not be done, since it can introduce infeasibility in case of moving horizon
    def _p_init(m, t):
        if m.pinit.value is not None:
            if t == time.first():
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

    @bat.Constraint(time, doc='initial state of charge')
    def _soc_init(m, t):
        if m.soc0.value is None:
            return Constraint.Skip
        else:
            if t == time.first():
                return m.e[t] == m.soc0 * m.emax / 100
            else:
                return Constraint.Skip

    def _soc_final(m, t):
        if m.socf.value is None:
            return Constraint.Skip
        else:
            if t == time.last():
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

    bat._e_balance = Constraint(time, rule=_energy_balance, doc='Energy balance constraint')
    bat._p_init = Constraint(time, rule=_p_init, doc='Initialize power')
    bat._e_min = Constraint(time, rule=_e_min, doc='Minimal energy constraint')
    bat._e_max = Constraint(time, rule=_e_max, doc='Maximal energy constraint')
    bat._soc_final = Constraint(time, rule=_soc_final, doc='Final soc constraint')
    bat._soc_min = Constraint(time, rule=_soc_min, doc='Minimal state of charge constraint')
    bat._soc_max = Constraint(time, rule=_soc_max, doc='Maximal state of charge constraint')
    bat._pmax = Constraint(time, rule=_pmax, doc='Power bounds constraint')
    bat._dpdmax = Constraint(time, rule=_dpdmax, doc='Maximal variation of descharging power constraint')
    bat._dpcmax = Constraint(time, rule=_dpcmax, doc='Maximal variation of charging power constraint')

    bat.soc = Expression(time, rule=lambda m, t: 100 * m.e[t] / m.emax, doc='Expression of the state of charge')

    return bat


def battery_v2(bat, **options):
    """
    Bilinear battery Model.

    This battery is limited in power, variation of power, state of charge and energy. One can fix initial and final
    state of charge.
    Efficiency for charge and discharge are considered.
    It exposes one power port using source convention.

    Instanciation options:
        - c_bat :       battery capacity (kWh)
        - c_bat_max :   battery maximal capacity, default : +inf (only if c_bat is None)
        - c_bat_min :   battery minimal capacity, default : 0 (only if c_bat is None)
        - p_max :       maximal charging power, default : +inf (>0)
        - p_min :       maximal descharging power, default : +inf (>0)
        - soc_min :     minimal soc, default : 0 (>0)
        - soc_max :     maximal soc, default : 100 (>0)
        - soc0 :        initial SOC, default: 50 (0<soc0<100)
        - socf :        final SOC, defalut: 50 (0<socf<100)
        - eta_c :       charging efficiency, default : 1 (<1 and >0)
        - eta_d :       descharging efficiency, default : 1 (<1 and >0)

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
    _soc_init       Initial state of charge
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

    bat = battery_v1(bat, **options)
    time = options.get('time', ContinuousSet(bounds=(0, 1)))

    eta_c = options.pop('eta_c', 1)
    eta_d = options.pop('eta_d', 1)

    assert 1 >= eta_c > 0, 'eta_c should be positif, smaller than 1'
    assert 1 >= eta_d > 0, 'eta_d should be positif, smaller than 1'

    bat.pd = Var(time, doc='discharging power', within=NonNegativeReals, initialize=0)
    bat.pc = Var(time, doc='charging power', within=NonNegativeReals, initialize=0)
    bat.u = Var(time, doc='binary variable', within=Binary, initialize=0)

    bat.etac = Param(default=eta_c, doc='charging efficiency', mutable=True, within=Reals)
    bat.etad = Param(default=eta_d, doc='discharging efficiency', mutable=True, within=Reals)

    bat.del_component('_e_balance')
    bat.del_component('_pmax')

    @bat.Constraint(time, doc='Energy balance constraint')
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

    bat._pdmax = Constraint(time, rule=_pdmax, doc='Discharging power bound')
    bat._pcmax = Constraint(time, rule=_pcmax, doc='Charging power bound')
    bat._p_balance = Constraint(time, rule=_p_balance, doc='Power balance constraint')

    return bat


def battery_v3(bat, **options):
    """
    Non-linear battery model for limiting charging power with resect to the state of charge.

    In this formulation, pcmax is a piecewise function of SOC. The user can define break points using pw_x and pw_y
    key-words arguments, default being pw_x : [0, 70, 100] and pw_y : [1, 0.9, 0.1] (means that pcmax will be
    10% of pmin when soc=100 %, 90% when soc is 70%, etc.

    .. warning:: adding numerous break points introduce a binary variable, i.e. more complexity.
        This version only implemets 3 break points.

    The rest of the model is the same than :meth:`lms2.electric.batteries.battery_v2`.

        Instanciation options:
            - c_bat :       battery capacity (kWh)
            - c_bat_max :   battery maximal capacity, default : +inf (only if c_bat is None)
            - c_bat_min :   battery minimal capacity, default : 0 (only if c_bat is None)
            - p_max :       maximal charging power, default : +inf (>0)
            - p_min :       maximal descharging power, default : +inf (>0)
            - soc_min :     minimal soc, default : 0 (>0)
            - soc_max :     maximal soc, default : 100 (>0)
            - soc0 :        initial SOC, default: 50 (0<soc0<100)
            - socf :        final SOC, defalut: 50 (0<socf<100)
            - eta_c :       charging efficiency, default : 1 (<1 and >0)
            - eta_d :       descharging efficiency, default : 1 (<1 and >0)
            - pw_x :        State of charge of the break points, default : [0, 70, 100]
            - pw_y :        Relative charging power limits of th break break points, default :[1, 0.9, 0.1]

    :param bat: Battery block
    :param options: apacity, efficiencies, State of charge, limits, boundary conditions, pw_x, pw_y, etc.
    :return:

    .. table::
        :width: 100%

        =============== ===================================================================
        Sets            Documentation
        =============== ===================================================================
        bp              None
        sos_w_index     None
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p               energy derivative with respect to time
        e               energy in battery
        de              variation of energy  with respect to time
        dp              variation of the battery power with respect to time
        pd              discharging power
        pc              charging power
        u               binary variable
        sos_u           binary variable for SOS2 constraint on pcmax
        sos_pcmax       pcmax relative value for sos2 constraint
        sos_w           weights for SOS2 constraint
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        emax            maximal energy
        emin            minimum energy (kWh)
        socmin          minimum soc
        pinit           initial output power of the battery (default : None)
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

    .. table::
        :width: 100%

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _soc_init       initial state of charge
        _p_init         Initialize power
        _e_min          Minimal energy constraint
        _e_max          Maximal energy constraint
        _soc_final      Final soc constraint
        _soc_min        Minimal state of charge constraint
        _soc_max        Maximal state of charge constraint
        _dpdmax         Maximal variation of descharging power constraint
        _dpcmax         Maximal variation of charging power constraint
        _e_balance      Energy balance constraint
        _pdmax          Discharging power bound
        _pcmax          Charging power bound
        _p_balance      Power balance constraint
        _sos2_pmax      SOS2 Convexity constraint
        _sos2_soc       SOS2 soc reconstitution
        _sos2_u1        SOS2 binary constraint for pb 1
        _sos2_u2        SOS2 binary constraint for pb 2
        _sos2_u3        SOS2 binary constraint for pb 3
        _sos2_u4        SOS2 constraint on the sum of weights
        _pcmax2         pc <= pmin(soc)
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        outlet          output power of the battery (kW), using source convention
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Expressions     Documentation
        =============== ===================================================================
        soc             Expression of the state of charge
        =============== ===================================================================
    """

    from pyomo.core import Piecewise
    import numpy as np

    bat = battery_v2(bat, **options)

    time = options.pop('time', ContinuousSet(bounds=(0, 1)))

    p_min = options.get('p_min')
    assert p_min >= 0, 'pmin should be a positive parameter.'

    pw_soc = options.pop('pw_x', [0.0, 80, 100])
    pw_pcmax = options.pop('pw_y', [1, 0.9, 0.1])

    assert isinstance(pw_soc, list), f"Option pw_x should be an instance of list, but is actually a {type(pw_soc)}."
    assert len(pw_soc) == 3, f"Option pw_x should be a list of length = 3, but his length is actually {len(pw_soc)}."
    assert isinstance(pw_pcmax, list), f"Option pw_y should be an instance of list, but is actually a {type(pw_pcmax)}."
    assert len(pw_pcmax) == 3, f"Option pw_y should be a list of length = 3, but his length is actually {len(pw_pcmax)}."

    # home maid version :
    bat.bp = Set(initialize=[0, 1, 2])

    bat.sos_u = Var(time, within = Binary, doc = 'binary variable for SOS2 constraint on pcmax')
    bat.sos_pcmax = Var(time, initialize=0, within=Reals, bounds = (0, 1),
                        doc = 'pcmax relative value for sos2 constraint')
    bat.sos_w = Var(bat.bp, time, initialize=0, within=Reals, bounds=(0, 1),
                    doc = 'weights for SOS2 constraint')

    @bat.Constraint(time, doc='SOS2 Convexity constraint')
    def _sos2_pmax(m, t):
        return m.sos_pcmax[t] == m.sos_w[0, t]*pw_pcmax[0] + m.sos_w[1, t]*pw_pcmax[1]  + m.sos_w[2, t]*pw_pcmax[2]

    @bat.Constraint(time, doc='SOS2 soc reconstitution')
    def _sos2_soc(m, t):
        return m.soc[t] == m.sos_w[0, t]*pw_soc[0] + m.sos_w[1, t]*pw_soc[1]  + m.sos_w[2, t]*pw_soc[2]

    @bat.Constraint(time, doc='SOS2 binary constraint for pb 1')
    def _sos2_u1(bat, t):
        return bat.sos_w[0, t] <= bat.sos_u[t]

    @bat.Constraint(time, doc='SOS2 binary constraint for pb 2')
    def _sos2_u2(bat, t):
        return bat.sos_w[1, t] <= 1

    @bat.Constraint(time, doc='SOS2 binary constraint for pb 3')
    def _sos2_u3(bat, t):
        return bat.sos_w[2, t] <= 1 - bat.sos_u[t]

    @bat.Constraint(time, doc='SOS2 constraint on the sum of weights')
    def _sos2_u4(bat, t):
        return sum([bat.sos_w[i, t] for i in bat.bp]) == 1

    @bat.Constraint(time, doc='pc <= pmin(soc)')
    def _pcmax2(m, t):
        return m.pc[t] <= m.sos_pcmax[t]*p_min