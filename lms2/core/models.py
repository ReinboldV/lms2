# -*- coding: utf-8 -*-
"""
Definition of Linear Model class.
"""
from ..core.expressions import Cost, Prosumtion, Energy, CO2

from pyomo.core.base.var import IndexedVar
from pyomo.environ import Var, Param, Objective, Constraint, ConcreteModel, Expression, Block


OBJ_SELECTION = {'cost': Cost,
                 'prosumtion': Prosumtion,
                 'energy' : Energy,
                 'co2': CO2}


class LModel(ConcreteModel):
    """
    Redefinition of ConcreteModel
    """

    def __init__(self, name='model', *args):
        """

        :param str name: Name of the model
        :param args:
        """
        super().__init__(name=name, *args)

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
        assert isinstance(g, Graph), f'graph attribute must be an instance of networkx.Graph, but received {type(g)} instead.'

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
            # v = operator.attrgetter(arg)(self)
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

        # TODO regler beug ici

        name = '_flux_cst_' + '&'.join([i.name.replace('.', '_') for i in args])
        self.add_component(name, Constraint(arg._index, rule=f))
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

    def construct_objective(self, select='all'):
        """
        NOT WORKING YET

        Construction of the global objective.

        This function is scanning all the structure of the model, looking for active objectives. If selected and active,
        objectives are constructed and summed to create a unique global objective (compulsory for Linear Programming).

        :param str select: 'all' (default), 'cost', 'prosumtion', 'energy' or 'co2' to select and sum objectives of
        sub-components.
        :return:
        """

        assert select in OBJ_SELECTION.keys(), f'select argument is not recognized. ' \
                                               f'It should be in {OBJ_SELECTION.keys()}, but is actually {select}'

        obj_f = Expression(expr=0)
        for obj in self.component_objects(active=True, ctype=Expression):
            obj.pprint()
            obj.reconstruct()
            if hasattr(obj,'expression_type'):
                if obj.expression_type == select:
                    obj_f = Objective(expr=obj_f+obj, sens=OBJ_SELECTION[select].sens)

        return obj_f.to_string()




