# -*- coding: utf-8 -*-
"""
Definition of Linear Model class.
"""

from lms2.core.var import Var

from pyomo.environ import ConcreteModel, Block, Constraint, Objective
from pyomo.core.base.var import IndexedVar
import logging

logging.basicConfig(filename='/home/admin/Documents/02-Recherche/02-Python/lms2/lms2.log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running LMS2 Logging...")

__all__ = ['LModel']
logger = logging.getLogger('lms2.models')


class LModel(ConcreteModel):
    """ Redefinition of ConcreteModel for the lms2 package"""

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

        :param Graph g: Grpah of the Unit
        :return: None
        """
        from networkx import Graph
        assert isinstance(g, Graph), f'graph attribute must be an instance of networkx.Graph, ' \
            f'but received {type(g)} instead.'

    def update_graph(self):
        """
        Update the graph of the model.

        iterates on all the active components of the unit.
        """
        from networkx import Graph
        self._graph = Graph()

        for data in self.component_map(active=True, ctype=Var).itervalues():
            self._graph.add_node(data.name, ctype=data.__class__, color='blue')
        for data in self.component_map(active=True, ctype=Block).itervalues():
            self._graph.add_node(data.name, ctype=data.__class__, color='red')
        for data in self.component_map(active=True, ctype=Constraint).itervalues():
            self._graph.add_node(data.name, ctype=data.__class__, color='yellow')
        for data in self.component_map(active=True, ctype=Objective).itervalues():
            self._graph.add_node(data.name, ctype=data.__class__, color='black', label=data.name)

    def connect_flux(self, *args):
        """
        Generate a pyomo constraints for a connection of flow variables.

        :param args: Variable
        :return:
        """
        # TODO docstring example and comments

        import operator
        exp = ''
        for arg in args:
            assert isinstance(arg, IndexedVar), f'{arg} should be an instance of IndexedVar.'
            assert hasattr(arg, 'sens'), f'{arg} should have attribute "sens"'
            assert hasattr(arg, 'port_type'), f'{arg} should have attribute "port_type"'
            assert getattr(arg, 'port_type') == 'flow', f'{arg}.port_type should be "flow"'
            if arg.sens == 'in':
                exp += '+ m.' + arg.name + '[t]'
            elif arg.sens == 'out':
                exp += '- m.' + arg.name + '[t]'
            else:
                raise NotImplementedError('')
        exp += ' == 0'
        f = lambda m, t: eval(exp)

        name = '_flux_cst_' + '&'.join([i.name.replace('.', '_') for i in args])
        self.add_component(name, Constraint(arg._index, rule=f))

        # from itertools import combinations
        # edges = combinations(args, 2)
        # self.graph.add_edges_from(edges)
        return

    def connect_effort(self, var1, var2, name=None):
        """
        Generate the pyomo constraint for the connection of two variables
        of the type effort.

        :param Var var1: name of the Variable 1
        :param Var var2: name of the Variable 2
        :param str name: name of the future constraint
        :return:
        """

        from pyomo.core.base.var import IndexedVar
        # create the constraint function f(m) or f(m,t):

        try:
            if not (var1.is_effort() and var2.is_effort()):
                raise TypeError('var1 must be names of existing Variables, and these '
                                'variables should be of type effort. '
                                'You may set attribute by using var.type_port = "effort"')
            assert isinstance(var1, IndexedVar) and isinstance(var2, IndexedVar),\
                f'The two variable to be connected should be instances of IndexedVar' \
                f'But are actually {type(var1)} and {type(var2)}'
            assert var1._index == var2._index, 'The two variable to be connected should share the same index.'
        except EOFError as err:
            raise err
        # f = lambda m, t: eval('m.' + v1 + '[t] == ' + 'm.' + v2 + '[t]')

        def f(m, t):
            return eval('m.' + var1.name + '[t] == ' + 'm.' + var2.name + '[t]')

        if name is None:
            name = '_effort_cst_' + var1.name.replace('.', '_') + '&' + var2.name.replace('.', '_')

        self.add_component(name, Constraint(var1._index, rule=f))

        self.graph.add_edge(var1, var2)

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
                    {cst.getname(fully_qualified=True)+'_'+dual_name: {i: self.component(dual_name)[c]
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
                df_c = DataFrame({c.getname(fully_qualified=True).replace('.', '_')+'_ls': s1, c.getname()+'_us': s2})
                df = concat([df, df_c], axis=1)
        return df

    # TODO : Not sure it is the way to go
    def construct_objective_from_tagged_expression(self, ptags=[]):
        """
        Definition of a method for pyomo class block. It sum-up all the expression the same tag

        :param Block self: A given block
        :param ptags: list of strings which refers to protected tags
        :return: ListObjectif
        """
        from lms2 import Expression, Objective
        from pyomo.environ import ObjectiveList
        from pyomo.dae import Integral

        _tags = []

        for e in self.component_objects(Expression, active=True):
            if hasattr(e, 'tag'):
                if e.tag not in _tags:
                    _tags.append(e.tag)
                    self.add_component(e.tag, ObjectiveList())

                new_int = e.parent_block().name+'_int'+e.getname(fully_qualified=False)
                self._logger.info(f'Integrating a tagged expression "{e.tag}" to the model : {new_int}')
                self.add_component(new_int, Integral(e.index_set(), wrt=e.index_set(),
                                   rule=lambda model, index: e[index]))
                self.find_component(e.tag).add(expr=self.find_component(new_int))

        for objlist in self.component_objects(Objective):
            if objlist.getname(fully_qualified=False) not in ptags:
                if objlist.getname() in _tags:
                    objlist.deactivate()

    def construct_objective_from_expression_list(self, wrt, *args):
        """
        Consruct objective from list of expression to be integrated with respect to wrt.

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

        self.new_int = Integral(wrt, wrt=wrt, rule=lambda model, index: sum([a[index] for a in args]))

        return Objective(expr=self.new_int)

    # def construct_integrals(self):
    #     """
    #     Construct Integral expression for all the Blocks of a given Model.
    #
    #     :return:
    #     """
    #     for b in self.component_objects(Block, active=True):
    #         b._construct_integrals_from_tagged_expression()
