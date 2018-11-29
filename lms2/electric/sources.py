"""
Contains classical electrical sources and loads.
"""

from lms2.base.base_units import FlowSource, FlowLoad

import unittest


class PowerSource(FlowSource):
    """ Simple Power Source."""
    def __init__(self, *args, time=None, profile=None, flow_name='p', **kwds):
        """

        :param args:
        :param time: Continuous Time set
        :param Series profile: Serie of power input in kW
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, time=time, profile=profile, flow_name=flow_name, **kwds)
        # self.doc = self.__doc__


class PowerLoad(FlowLoad):
    """ Simple Power Load."""

    def __init__(self, *args, time=None, profile=None, flow_name='p', **kwds):
        """

        :param args:
        :param time: Continuous Time set
        :param Series profile: Serie of power input in kW
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