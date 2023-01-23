from pyomo.core import Param
from pyomo.core.base.units_container import units as u
from pyomo.dae import ContinuousSet
from pyomo.core.base import Reals, NonNegativeReals


def occupancy(occ, **kwargs):
    """
    Occupancy block

    The occupancy block gathers all the dynamic paramters related to occupancy, such as hot water flow, internal
    heat gains, temperature set point and comfort coefficient  for night and day zone.
    This block defines the inputs received from the occupants. For the time being, the solar inputs from
    the weather data are also included in this block. This will change in the future,
    with a separate ‘solar inputs’ block. see :py:meth:`lms2.environment.environment.solar_inputs`.

    .. table::
        :width: 100%

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        Q_sol_N         Northern component solar radiation
        Q_sol_S         Southern component solar radiation
        Q_sol_E         Eastern component solar radiation
        Q_sol_W         Western component solar radiation
        Q_int_D         Day zone Internal heat gains
        Q_int_N         Night zone Internal heat gains
        Tset_d          Day zone set temperature
        Tset_n          Night zone Set temperature
        Flow_HW         HW demand of the occupants
        u_N             comfort coefficient for night zone
        u_D             comfort coefficient for day zone
        =============== ===================================================================

    :param occ: occupancy block
    :param kwargs: kwargs for the block construction (time set)
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))

    # solar gains are included here because it is treated as a heat gain in the graph description
    occ.Q_sol_N = Param(time, default=0, doc='Northern component solar radiation', within=Reals, units=u.watt)
    occ.Q_sol_S = Param(time, default=0, doc='Southern component solar radiation', within=Reals, units=u.watt)
    occ.Q_sol_E = Param(time, default=0, doc='Eastern component solar radiation', within=Reals, units=u.watt)
    occ.Q_sol_W = Param(time, default=0, doc='Western component solar radiation', within=Reals, units=u.watt)
    occ.Q_int_D = Param(time, default=0, doc='Day zone Internal heat gains', within=Reals, units=u.watt)
    occ.Q_int_N = Param(time, default=0, doc='Night zone Internal heat gains', within=Reals, units=u.watt)

    occ.Tset_d  = Param(time, default=15, doc='Day zone set temperature', within=Reals, units=u.deg)
    occ.Tset_n  = Param(time, default=15, doc='Night zone Set temperature', within=Reals, units=u.deg)
    occ.Flow_HW = Param(time, default=0, doc='HW demand of the occupants', within=Reals, units=u.watt)
    occ.u_N     = Param(time, default=1, mutable=True, within=NonNegativeReals, doc='comfort coefficient for night zone')
    occ.u_D     = Param(time, default=1, mutable=True, within=NonNegativeReals, doc='comfort coefficient for day zone')