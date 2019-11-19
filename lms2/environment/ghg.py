# -*- coding: utf-8 -*-

""" 
Contains units and models for emissions
"""
from lms2 import DynUnit
from pyomo.environ import Var, Expression, Param
from pyomo.network import Port


def def_linear_ghg_cost(m, var_name='p_out', init_cost=0):
    """
    Method for adding a linear GHG cost to a given unit.

    :param m: Block
    :param str var_name: Names of the expensive variable
    :return pyomo.Expression: Expression of instantaneous GHG emission in geqCOS/s
    """

    m.co2 = Param(initialize=init_cost, mutable= True, doc='Green gaz emission factor (gr eqCO2/(kW.h))')

    def _instant_co2(m, t):
        return m.find_component(var_name)[t] * m.mixCO2 / 3600

    return Expression(m.time, rule=_instant_co2, doc='instantaneous GHG emission in geqCO2/s')


class _OnePortGHGUnit(DynUnit):
    """
    Dynamic Unit that is exposing one GHG Port
    """

    def __init__(self, *args, time=None, **kwds):

        super(_OnePortGHGUnit, self).__init__(*args, time=time, **kwds)
        self.ghg = Var(time, doc='Green House Gaz emission eqC02 (g)')
        self.inlet = Port(initialize={'ghg': self.v})


