from lms2.base.base_units import FlowSource, FlowLoad

import unittest


class PowerSource(FlowSource):
    """ Simple Power Source."""
    def __init__(self, *args, time=None, profile=None, flow_name='p', **kwds):
        super().__init__(*args, time=time, profile=profile, flow_name=flow_name, **kwds)
        self.doc = __doc__


class PowerLoad(FlowLoad):
    """ Simple Power Load."""

    def __init__(self, *args, time=None, flow=None, flow_name='p', **kwds):
        super().__init__(*args, time=time, flow=flow, flow_name=flow_name, **kwds)
        self.doc = __doc__


class WindTurbine(PowerSource):
    """  Simple wind turbine with fixed power profile"""
    # TODO create WindTurbine class
    pass


class PvPanelsWSurface(PowerSource):
    """ PV panels with parametric surface """
    # TODO create PvPanelsWSurface
    pass