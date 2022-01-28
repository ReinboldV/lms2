from pyomo.core import Param, Var
from pyomo.core.base.units_container import units as u
from pyomo.dae import ContinuousSet, DerivativeVar
from pyomo.core.base.set import Reals, NonNegativeReals

def hot_water_tank(hwt, **kwargs):
    """
    Hot Water TankBlock

    The HW block model the tank as an adiabatic thermal storage.

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    T_HW            HW storage temperature
    =============== ===================================================================
    =============== ===================================================================
    Derivative Var  Documentation
    =============== ===================================================================
    dT_HW           HW temperature derivative
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    T_HW_0          Initial temperature
    T_CW            Temperature of cold water
    T_HW_d          Temperature of demanded hot water
    V               HW storage tank Volume
    c_w             Specific heat capacity of water
    T_HW_LB         HW storage temperature LB
    T_HW_UB         HW storage temperature UB
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    bounds          HW temperature bounds
    init            HW initial temperature
    =============== ===================================================================

    :param hwt:
    :param kwargs:
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))

    hwt.T_HW_0  = Param(default=55, doc='Initial temperature ', within=Reals, units=u.deg)
    hwt.T_HW    = Var(time, initialize=55, units=u.deg, bounds=(0, 100), doc="HW storage temperature")
    hwt.T_CW    = Param(default=10, doc='Temperature of cold water', within=Reals, units=u.deg)
    hwt.T_HW_d  = Param(default=42, doc='Temperature of demanded hot water', within=Reals, units=u.deg)
    hwt.V       = Param(default=200, doc='HW storage tank Volume', within=Reals, units=u.kg)
    hwt.c_w     = Param(default=4186*0.997, doc='Volumic specific heat capacity of water [J/(L.K)', within=Reals)
    hwt.T_HW_LB = Param(default=42, doc='HW storage temperature LB', within=Reals, units=u.deg)
    hwt.T_HW_UB = Param(default=56, doc='HW storage temperature UB', within=Reals, units=u.deg)

    hwt.dT_HW = DerivativeVar(hwt.T_HW, wrt=time, doc="HW temperature derivative",  units=u.deg / u.s)

    @hwt.Constraint(time, doc = 'HW temperature bounds')
    def bounds(b, t):
        return b.T_HW_LB, b.T_HW[t], b.T_HW_UB

    @hwt.Constraint(doc = 'HW initial temperature')
    def init(b):
        return b.T_HW[0] == b.T_HW_0


def heat_pump(hp, **kwargs):
    """
    Heat pump Block

    The HP is modelled by tree heat control variable (day_zone, night_zone and HW tank). The total electrical power is
    calculated is the COP parameter.

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    Q_heat_N        Heat pump flow Night zone
    Q_heat_D        Heat pump flow Day zone
    Q_heat_HW       Heat pump flow HW tank
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    Q_heat_D_max    Maximal heat production in the day-zone
    Q_heat_N_max    Maximal heat production in the night-zone
    Q_HW_max        Maximal heat production in the HW storage tank
    COP             Coefficient of performance
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    limits          heat_pumps heating bounds
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    p_elec_D        Electrical power in the day zone
    p_elec_N        Electrical power in the night zone
    p_elec_HW       Electrical power for DHW
    =============== ===================================================================

    :param hp: Heat pump block
    :param kwargs: kwargs for the block construction (time set and occupancy block)
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))
    occ   = kwargs.pop('occ', None)

    hp.Q_heat_D_max = Param(default=10000, doc='Maximal heat production in the day-zone')
    hp.Q_heat_N_max = Param(default=10000, doc='Maximal heat production in the night-zone')
    hp.Q_HW_max     = Param(default=2000,  doc='Maximal heat production in the HW storage tank')

    hp.Q_heat_N  = Var(time, initialize=0, doc='Heat pump flow Night zone', units=u.watt, bounds=(0, hp.Q_heat_N_max.value))
    hp.Q_heat_D  = Var(time, initialize=0, doc='Heat pump flow Day zone', units=u.watt, bounds=(0, hp.Q_heat_D_max.value))
    hp.Q_heat_HW = Var(time, initialize=0, doc='Heat pump flow HW tank', units=u.watt, bounds=(0, hp.Q_HW_max.value))

    hp.COP = Param(default=3, domain=NonNegativeReals, doc='Coefficient of performance')

    @hp.Expression(time, doc='Electrical power in the day zone')
    def p_elec_D(b, t):
        return b.Q_heat_D[t] / b.COP

    @hp.Expression(time, doc='Electrical power in the night zone')
    def p_elec_N(b, t):
        return b.Q_heat_N[t] / b.COP

    @hp.Expression(time, doc='Electrical power for DHW')
    def p_elec_HW(b, t):
        return b.Q_heat_HW[t] / b.COP

    @hp.Constraint(time, doc='heat_pumps heating bounds')
    def limits(b, t):
        return 0, b.Q_heat_N[t], occ.u_N[t] * b.Q_heat_N_max