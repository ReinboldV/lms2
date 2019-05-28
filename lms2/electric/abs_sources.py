# -*- coding: utf-8 -*-
"""
Contains classical electrical sources and loads.
"""

from lms2 import AbsFlowSource, AbsFixedFlowSource, AbsFlowLoad, AbsFixedFlowLoad
from pyomo.environ import Var, PositiveReals, Constraint
from pyomo.network import Port

__all__ = ['AbsPowerSource',        'AbsFixedPowerSource',      'AbsScalablePowerSource',
           'AbsPowerLoad',          'AbsFixedPowerLoad',        'AbsScalablePowerLoad',      'AbsDebugSource']

#TODO unittest
class AbsPowerSource(AbsFlowSource):
    """ Simple Power Source.

    Exposes a power output port.
    """
    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)

#TODO unittest
class AbsFixedPowerSource(AbsFixedFlowSource):
    """
    Abstract Fixed Power Source Unit.

    Abstract Power Source Unit who's power output is fixed using a given index set and indexed profile.
    """
    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)

#TODO unittest
class AbsScalablePowerSource(AbsFixedPowerSource):
    """ Scalable Power Source

    May be used for sizing sources, such as PV panel, wind turbines, etc."""

    def __init__(self, *args, flow_name='p', **kwds):

        super().__init__(*args, flow_name=flow_name, **kwds)

        scaled_flow_name = flow_name+'_scaled'

        self.scale_fact = Var(initialize=1, within=PositiveReals, doc='scaling factor within Positve reals')
        self.add_component(scaled_flow_name, Var(self.time, doc='Scaled source flow'))

        def _flow_scaling(m, t):
            return m.find_component(scaled_flow_name)[t] == m.scale_fact*m.find_component(flow_name)[t]

        def _debug_flow_scaling(m, t):
            return -0.000001, \
                   m.find_component(scaled_flow_name)[t] - m.scale_fact * m.find_component(flow_name)[t],\
                   0.000001

        self.flow_scaling       = Constraint(self.time, rule=_flow_scaling,
                                             doc='Constraint equality for flow scaling')
        self.debug_flow_scaling = Constraint(self.time, rule=_debug_flow_scaling,
                                             doc='Constraint equality for flow scaling')


        self.outlet = Port(initialize={'f': (self.component(scaled_flow_name), Port.Conservative)})

#TODO unittest
class AbsPowerLoad(AbsFlowLoad):
    """ Simple Power Load."""

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param args:
        :param time: Continuous Time set
        :param Series profile: Serie of power input (kW)
        :param str flow_name: Name of the new flow variable
        :param kwds:
        """
        super().__init__(*args, flow_name=flow_name, **kwds)


#TODO unittest
class AbsFixedPowerLoad(AbsFixedFlowLoad):
    """
    Abstract Fixed Power Source Unit.

    Abstract Power Source Unit who's power output is fixed using a given index set and indexed profile.
    """
    def __init__(self, *args, flow_name='p', **kwds):
        super().__init__(*args, flow_name=flow_name, **kwds)



# class AbsWindTurbine(AbsPowerSource):
#     """  Simple wind turbine with fixed power profile"""
#     # TODO create WindTurbine class
#     pass
#
#
# class AbsPvPanelsWSurface(AbsPowerSource):
#     """ PV panels with parametric surface """
#     # TODO create PvPanelsWSurface
#     pass


#TODO unittest
class AbsScalablePowerLoad(AbsFixedPowerLoad):
    """ Scalable Power Load

    May be used for sizing load."""

    def __init__(self, *args, flow_name='p', **kwds):

        super().__init__(*args, flow_name=flow_name, **kwds)

        scaled_flow_name = flow_name+'_scaled'

        self.scale_fact = Var(initialize=1, within=PositiveReals, doc='scaling factor within Positve reals')
        self.add_component(scaled_flow_name, Var(self.time, doc='Scaled source flow'))

        def _flow_scaling(m, t):
            return m.scale_fact*m.find_component(scaled_flow_name)[t] == m.find_component(flow_name)[t]

        def _debug_flow_scaling(m, t):
            return -0.000001, \
                   m.scale_fact * m.find_component(scaled_flow_name)[t] - m.find_component(flow_name)[t],\
                   0.000001

        self.flow_scaling       = Constraint(self.time, rule=_flow_scaling,
                                             doc='Constraint equality for flow scaling')
        self.debug_flow_scaling = Constraint(self.time, rule=_debug_flow_scaling,
                                             doc='Constraint equality for flow scaling')

        # self.flow_scaling.deactivate()

        self.scaled_inlet = Port(initialize={'f': (self.component(scaled_flow_name), Port.Conservative)})


class AbsDebugSource(AbsPowerSource):
    """
    Debug Power source.

    Consist of an unbounded power source to force convergence.
    It is associated to an expensive (positive) cost function.
    """

    def __init__(self, *args, flow_name='p', **kwds):
        """

        :param str flow_name: name of the variable to be weighted
        """
        super().__init__(*args, flow_name=flow_name, **kwds)

        from lms2 import def_simple_cost

        self.inst_cost = def_simple_cost(self, var_name='p')