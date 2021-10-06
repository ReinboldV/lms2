# -*- coding: utf-8 -*-
"""
Definition of Linear Model class.
"""

import logging

from pyomo.environ import ConcreteModel, Constraint, Objective, Var, AbstractModel

__all__ = ['LModel', 'AbsLModel']
logger = logging.getLogger('lms2.models')


class LModel(ConcreteModel):
    """
    Redefinition of ConcreteModel for the lms2 package

    """

    def __init__(self, name='model', *args):
        """

        :param str name: Name of the model
        :param args:

        """

        super().__init__(name=name, *args)
        logger.info(f'Initiation of {name} {self.__class__}')
        self._graph = None

    @property
    def graph(self):
        """
        getter for the graph argument
        """
        self.update_graph()
        return self._graph

    @graph.setter
    def graph(self, g):
        """
        Setter method for the graph attribute

        :param Graph g: Graph of the Unit
        :return: None
        """
        from networkx import Graph
        assert isinstance(g, Graph), f'graph attribute must be an instance of networkx.Graph, ' \
                                     f'but received {type(g)} instead.'

    def __setattr__(self, key, value):

        super().__setattr__(key, value)
        logger.debug(f'adding the attribute : {key} = {value}')

    def fix_binary(self):
        """
        Fix binary variables to their values

        :return:

        """
        from pyomo.environ import RealSet

        for u in self.component_objects(Var):
            if u.is_indexed():
                for ui in u.itervalues():
                    if ui.is_binary():
                        ui.fix(ui.value)
                        ui.domain = RealSet([0, 1])
            else:
                if u.is_binary():
                    u.fix(u.value)
                    u.domain = RealSet([0, 1])

    def unfix_binary(self):
        """
        Unfix binary variables

        :return:
        """

        for u in self.component_objects(Var):
            if u.is_indexed():
                for ui in u.itervalues():
                    if ui.is_binary():
                        ui.unfix()
            else:
                if u.is_binary():
                    u.unfix()

    def get_duals(self, dual_name='dual'):
        """
        Return dual coefficient of LP model.

        :param str dual_name: name of the Suffix
        :return : Dual coefficient (DataFrame)
        """

        from pandas import DataFrame, concat
        from pyomo.environ import Constraint
        df = DataFrame()

        assert hasattr(self, dual_name), f'"{self.name}" does not have attribute named "{dual_name}".'

        for cst in self.component_objects(Constraint, active=True):
            if cst.is_indexed():
                s = DataFrame(
                    {cst.getname(fully_qualified=True) + '_' + dual_name: {i: self.component(dual_name)[c]
                                                                           for (i, c) in cst.iteritems()}})
                df = concat([df, s], axis=1)
            else:
                Warning('Trying to get dual coefficient from a non-index variable. Not Implemented Yet')
        return df

    def get_slack(self):
        """
        Return slack variables values for all
        the active constraints of a model.

        :return: DataFrame
        """

        from pandas import DataFrame, Series, concat

        df = DataFrame()
        for c in self.component_objects(Constraint, active=True):
            if c.is_indexed():
                s1 = Series({i: c[i].lslack() for i in c.__iter__()})
                s2 = Series({i: c[i].uslack() for i in c.__iter__()})
                df_c = DataFrame(
                    {c.getname(fully_qualified=True).replace('.', '_') + '_ls': s1, c.getname() + '_us': s2})
                df = concat([df, df_c], axis=1)
        return df

    def construct_objective_from_expression_list(self, wrt, *args):
        """
        Construct objective from list of expression to be integrated with respect to wrt.

        :param str name: name of the new integral expression (optional)
        :param wrt: Set for the integration of the expressions
        :param args: Expression of instantaneous objectives
        :return: Objective
        """

        from lms2 import Expression
        from pyomo.dae import Integral
        for exp in args:
            assert isinstance(exp, Expression), ValueError(f'args should be a list of pyomo Expression,'
                                                           f' and actually received {exp, type(exp)}')

        self.add_component('obj_expr', Integral(wrt, wrt=wrt, rule=lambda model, index: sum([a[index] for a in args])))

        return Objective(expr=self.component('obj_expr'))


class AbsLModel(AbstractModel):
    """ Redefinition of AbstractModel for the lms2 package"""

    def __init__(self, *args, name='model'):
        """

        :param str name: Name of the model
        :param args:

        """

        super().__init__(name=name, *args)
        logger.info(f'Initiation of {name} {self.__class__}')
        self._graph = None

    @property
    def graph(self):
        """
        getter for the graph argument
        """
        return self._graph

    @graph.setter
    def graph(self, g):
        """
        Setter method for the graph attribute

        :param Graph g: Grpah of the Unit
        :return: None
        """
        from networkx import Graph
        assert isinstance(g, Graph), f'graph attribute must be an instance of networkx.Graph, ' \
                                     f'but received {type(g)} instead.'

    def __setattr__(self, key, value):

        super().__setattr__(key, value)
        logger.debug(f'adding the attribute : {key} = {value}')

    def fix_binary(self):
        """
        Fix binary variables to their values

        :return:
        """

        from pyomo.environ import RealSet

        for u in self.component_objects(Var):
            if u.is_indexed():
                for ui in u.itervalues():
                    if ui.is_binary():
                        ui.fix(ui.value)
                        ui.domain = RealSet([0, 1])
            else:
                if u.is_binary():
                    u.fix(u.value)
                    u.domain = RealSet([0, 1])

    def unfix_binary(self):
        """
        Unfix binary variables

        :return:
        """
        for u in self.component_objects(Var):
            if u.is_indexed():
                for ui in u.itervalues():
                    if ui.is_binary():
                        ui.unfix()
            else:
                if u.is_binary():
                    u.unfix()

    def get_duals(self, dual_name='dual'):
        """
        Return dual coefficient of LP abstract model.

        :param str dual_name: name of the Suffix
        :return : Dual coefficient (DataFrame)
        """
        from pandas import DataFrame, concat
        from pyomo.environ import Constraint
        df = DataFrame()

        assert hasattr(self, dual_name), f'"{self.name}" does not have attribute named "{dual_name}".'

        for cst in self.component_objects(Constraint, active=True):
            if cst.is_indexed():
                s = DataFrame(
                    {cst.getname(fully_qualified=True) + '_' + dual_name: {i: self.component(dual_name)[c]
                                                                           for (i, c) in cst.iteritems()}})
                df = concat([df, s], axis=1)
            else:
                Warning('Trying to get dual coefficient from a non-index variable. Not Implemented Yet')
        return df

    def get_slack(self):
        """
        Return slack variables values for all
        the active constraints of a abstract model.

        :return: DataFrame
        """

        from pandas import DataFrame, Series, concat

        df = DataFrame()
        for c in self.component_objects(Constraint, active=True):
            if c.is_indexed():
                s1 = Series({i: c[i].lslack() for i in c.__iter__()})
                s2 = Series({i: c[i].uslack() for i in c.__iter__()})
                df_c = DataFrame(
                    {c.getname(fully_qualified=True).replace('.', '_') + '_ls': s1, c.getname() + '_us': s2})
                df = concat([df, df_c], axis=1)
        return df

    def construct_objective_from_expression_list(self, wrt, *args):
        """
        Construct objective from list of expression to be integrated with respect to wrt.

        :param str name: name of the new integral expression (optional)
        :param wrt: Set for the integration of the expressions
        :param args: Expression of instantaneous objectives
        :return: Objective
        """
        from pyomo.environ import Expression
        from pyomo.dae import Integral
        for exp in args:
            assert isinstance(exp, Expression), ValueError(f'args should be a list of pyomo Expression,'
                                                           f' and actually received {exp, type(exp)}')

        self.new_int = Integral(wrt, wrt=wrt, rule=lambda model, index: sum([a[index] for a in args]))

        return Objective(expr=self.new_int)
