# -*- coding: utf-8 -*-

""" 
Contains units and models for emissions
"""
from pyomo.environ import Expression, Param

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
