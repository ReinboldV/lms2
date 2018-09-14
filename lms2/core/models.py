from pyomo.core.base.PyomoModel import ConcreteModel
from pyomo.core.base.var import IndexedVar
from pyomo.core.base.constraint import Constraint


class LModel(ConcreteModel):
    """
    Redefinition of ConcreteModel
    """

    def __init__(self, name='model', *args):
        super().__init__(name='model', *args)

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
        setter method for the graph attribute

        :param Graph g: Grpah of the Unit
        :return: None
        """
        from networkx import Graph
        assert isinstance(g, Graph), f'graph attribute must be an instance of networkx.Graph, but received {type(g)} instead.'

    def update_graph(self):
        """
        Update the graph of the model. iterates on all the active components of the unit.
        """
        from networkx import Graph
        self._graph = Graph()

        for data in self.component_map(active=True).itervalues():
            self._graph.add_node(data.name, ctype=data.__class__)

    def flux_cst(self, *args, name=None):
        """
        Generate a pyomo constraints for a connection of flow variables.
        """
        # TODO docstring example and comments

        import operator
        exp = ''
        for arg in args:
            v = operator.attrgetter(arg)(self)
            assert isinstance(v, IndexedVar), f'{v} should be an instance of IndexedVar.'
            assert hasattr(v, 'sens'), f'{v} should have attribute "sens"'
            assert hasattr(v, 'port_type'), f'{v} should have attribute "port_type"'
            assert getattr(v, 'port_type') == 'flow', f'{v}.port_type should be "flow"'
            if v.sens == 'in':
                exp += '+ m.' + arg + '[t]'
            elif v.sens == 'out':
                exp += '- m.' + arg + '[t]'
            else:
                raise NotImplementedError('')
        exp += ' == 0'
        f = lambda m, t: eval(exp)

        if name is None:
            name = '_flux_cst_' + '&'.join([i.replace('.', '_') for i in args])
        self.add_component(name, Constraint(v._index, rule=f))
        return

    def effort_cst(self, v1, v2, name=None):
        """
        Generate the pyomo constraint for the connection of two variables
        of the type effort.

        :param str v1: name of the Variable 1
        :param str v2: name of the Variable 2
        :param str name: name of the future constraint
        :return:
        """

        from pyomo.core.base.var import IndexedVar
        # create the constraint function f(m) or f(m,t):
        import operator
        var1 = operator.attrgetter(v1)(self)
        var2 = operator.attrgetter(v2)(self)

        try:
            if not (var1.is_effort() and var2.is_effort()):
                raise TypeError('v1 must be names of existing Variables, and these '
                                'variables should be efforts. '
                                'You may set attribute by using var.type_port = "effort"')
            assert isinstance(var1, IndexedVar) and isinstance(var2, IndexedVar),\
                f'The two variable to be connected should be instances of IndexedVar' \
                f'But are actually {type(var1)} and {type(var2)}'
            assert var1._index == var2._index, 'The two variable to be connected should share the same index.'
        except EOFError as err:
            raise err
        # f = lambda m, t: eval('m.' + v1 + '[t] == ' + 'm.' + v2 + '[t]')

        def f(m, t):
            return eval('m.' + v1 + '[t] == ' + 'm.' + v2 + '[t]')

        if name is None:
            name = '_effort_cst_' + v1.replace('.', '_') + '&' + v2.replace('.', '_')

        self.add_component(name, Constraint(var1._index, rule=f))
        # self.graph.add_edge(v1, v2)
