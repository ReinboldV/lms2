# -*- coding: utf-8 -*-
"""
Different types of objectives

In order to automatically recognize different type of objectives or cost from different part of the system.
We define several classes that heritate from pyomo.core.base.Objective.
Such as Cost (in euro), Energy (in W.h), Prosumtion (in W.h), CO2 emmision (in kg) etc.
"""

from pyomo.core.base import minimize, maximize
from pyomo.core.base.expression import SimpleExpression

expression_type = ['COST', 'PROSUMTION', 'CO2', 'ENERGY']
units = ['euros', 'W.h', 'kg_eq', 'W.h']


class Cost(SimpleExpression):
    """
    Cost Objective (euros)

    Represents the cost of use in euros
    """
    def __init__(self, *arg, **kwargs):
        """

        :param args: rule or expr
        """
        super().__init__(*arg, **kwargs)
        self.unit = 'euros'
        self.expression_type = 'cost'
        self.sens = minimize # sens=1


class Prosumtion(SimpleExpression):
    """
    Prosumtion Objective (W.h)

    Represents the prosumation capacity, i.e. the auto-consumtion in watt-hour
    """
    def __init__(self, *arg, **kwargs):
        """

        :param str name: Name of the model
        :param args:
        """
        super().__init__(*arg, **kwargs)
        self.unit = 'W.h'
        self.expression_type = 'prosumtion'
        self.sens = maximize  # sens=-1


class Energy(SimpleExpression):
    """
    Energy Objective (euros)

    Represent the total use of energy in Watt-hour
    """
    def __init__(self, *arg, **kwargs):
        """

        :param str name: Name of the model
        :param args:
        """
        super().__init__(*arg, **kwargs)
        self.unit = 'W.h'
        self.expression_type = 'energy'
        self.sens = minimize  # sens=1


class CO2(SimpleExpression):
    """
    CO2 Objective (kg_eqco2)

    Represents greenhouse gaz emission in kilograms of equivalent CO2.
    """
    def __init__(self, *arg, **kwargs):
        """

        :param str name: Name of the model
        :param args:
        """
        super().__init__(*arg, **kwargs)
        self.unit = 'kg_eq'
        self.expression_type = 'co2'
        self.sens = minimize  # sens=1
