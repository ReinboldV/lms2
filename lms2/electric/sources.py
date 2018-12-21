# -*- coding: utf-8 -*-
"""
Contains classical electrical sources and loads.
"""

from ..base.base_units import FlowSource, FlowLoad, ScalableFlowSource


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

    def __init__(self, *args, time=None, profile=None, flow_name='p', **kwds):

        """
        :param args:
        :param Set time: Set or ContinuousSet for time integration
        :param pandas.Series flow: Series that describes the input profile
        :param str kind: kind of interpolation see scipy.interpolate.interpolate.interp1d
        :param str fill_value: see scipy.interpolate.interpolate.interp1d
        :param kwargs:
        """

        super().__init__(*args, time=time, flow=profile, flow_name=flow_name, **kwds)


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