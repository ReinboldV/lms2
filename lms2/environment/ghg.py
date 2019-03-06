# -*- coding: utf-8 -*-

""" 
Contains units and models for emissions
"""
from lms2 import DynUnit, Var, Param

from pyomo.network import Port


class _OnePortGHGUnit(DynUnit):
    """
    Dynamic Unit that is exposing one GHG Port
    """

    def __init__(self, *args, time=None, **kwds):

        super(_OnePortGHGUnit, self).__init__(*args, time=time, **kwds)
        self.ghg = Var(time, doc='Green House Gaz emission eqC02 (g)')
        self.inlet = Port(initialize={'ghg': self.v})


