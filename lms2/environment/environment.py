from pyomo.core import Param
from pyomo.core.base.units_container import units as u
from pyomo.dae import ContinuousSet
from pyomo.core import Reals


def solar_inputs(sol, **options):
    """
    todo : Not implemented yet !
    Block responsible for the calculation of heat gain, with respect to the environment (lat, long, time),
    and building geometry windows surface etc.
    """

    time = options.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))
    pass


def environment(env, **options):
    """
    Environment Block

    Gather environment parameter such as temperatures, (irradiation, humidity, weather could be loaded here)

    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    Te              External temperature
    Tg              Ground temperature
    =============== ===================================================================

    :param env:
    :param kwargs:
    :return:
    """
    env._unit_support = True

    time  = options.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))

    env.Te  = Param(time, default=0, doc='External temperature', within=Reals, units=u.deg)
    env.Tg  = Param(time, default=10, doc='Ground temperature', within=Reals, units=u.deg)
