# -*- coding: utf-8 -*-
"""
Contains classical electrical sources and loads.
"""

from lms2 import FlowSource, FlowLoad, ScalableFlowSource, Param, Expression


class PowerSource(FlowSource):
    """ Simple Power Source."""
    def __init__(self, *args, time=None, profile=None, flow_name='p', **kwds):
        """

        :param args:
        :param time: Continuous Time set
        :param Series profile: Serie of power input (kW)
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, time=time, profile=profile, flow_name=flow_name, **kwds)


class ScalablePowerSource(ScalableFlowSource):
    """ Scalable power source

    May be used for sizing sources, such as PV panel, wind turbines, etc."""

    def __init__(self, *args, time=None, profile=None, flow_name='p', c_use=None, **kwds):

        """
        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series profile: Series that describes the input profile
        :param str flow_name: name of the flow parameter
        :param float c_c_use : cost of use (euros/kWh)
        :param kwargs:
        """
        super().__init__(*args, time=time, flow=profile, flow_name=flow_name, **kwds)

        if c_use is not None:
            assert isinstance(c_use, float), f'Error : c_use must be an instance of Float, recieved {type(c_use)}'
            self.c_use = Param(initialize=c_use, doc='cost of use (euro/kWh)', mutable=True)

            def _instant_cost(m, t):
                return -m.p[t] * m.c_use / 3600

            self.instant_cost = Expression(time, rule=_instant_cost)
            self.instant_cost.tag = 'COST'


class PowerLoad(FlowLoad):
    """ Simple Power Load."""

    def __init__(self, *args, time=None, profile=None, flow_name='p', **kwds):
        """

        :param args:
        :param time: Continuous Time set
        :param Series profile: Serie of power input (kW)
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, time=time, flow=profile, flow_name=flow_name, **kwds)


class WindTurbine(PowerSource):
    """  Simple wind turbine with fixed power profile"""
    # TODO create WindTurbine class
    pass


class PvPanelsWSurface(PowerSource):
    """ PV panels with parametric surface """
    # TODO create PvPanelsWSurface
    pass
