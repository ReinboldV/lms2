# -*- coding: utf-8 -*-
"""
Water tank and groundwater resources
"""

from pyomo.environ import Var, Constraint, Objective, Param
from pyomo.dae import Integral, ContinuousSet, DerivativeVar

from lms2 import AbsDynUnit

class WaterTank(AbsDynUnit):
    """
    water tank for PV water pumping system modelling

    """
    #TODO : model and tests
    def __inti__(self, *args, **kwargs):
        super().__init__(*args, kwargs=kwargs)
        pass


class WaterGroundResource(AbsDynUnit):
    """
    WaterGround Resource for PV water pumping system modelling

    """

    # TODO : model and tests
    def __inti__(self, *args, **kwargs):
        super().__init__(*args, kwargs=kwargs)
        pass
