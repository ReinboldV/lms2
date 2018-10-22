from pyomo.core.base.block import SimpleBlock
from pyomo.core.base.var import IndexedVar
from pyomo.core.base.constraint import Constraint
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.kernel.set_types import *
from pyomo.core.base.PyomoModel import Model as PyomoModel

from networkx import Graph

from lms2.core.time import Time
from lms2.core.models import LModel
from lms2.core.var import Var


class Unit(SimpleBlock):
    """
    redefinition of SimpleBlock
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self._graph = Graph()


class DynUnit(Unit):
    def __init__(self, *args, time=None, **kwds):
        """
        Dynamic Unit

        Standard unit with a time argument for indexing variables and constraints.

        :param args:
        :param time:
        :param kwds:
        """
        from pyomo.dae.contset import ContinuousSet

        super().__init__(*args, **kwds)
        if not isinstance(time, ContinuousSet):
            msg = f'time key word argument should be an instance of pyomo.dae.contest.ContinuousSet, ' \
                  f'and is actually a {type(time)}.'
            raise AttributeError(msg)

    def flux_cst(self, *args, name=None):
        """ Generate a pyomo constraints for a connection of flow variables."""
        # TODO docstring example and comments

        import operator
        exp = ''
        for arg in args:
            v = operator.attrgetter(arg)(self)
            assert isinstance(v, IndexedVar), f'{v} should be an instance of IndexedVar.'
            assert hasattr(v, 'sens'), f'{v} should have attribute "sens"'
            assert hasattr(v, 'port_type'), f'{v} should have attribute "port_type"'
            assert getattr(v, 'port_type')
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
        """ generate the pyomo constraint for the connection of two variables
        of the type effort.

        :param str v1: name of the Variable 1
        :param str v2: name of the Variable 2
        :param str name: name of the future constraint
        :return: """
        
        # TODO example

        from pyomo.core.base.var import IndexedVar
        # create the constraint function f(m) or f(m,t):
        import operator
        var1 = operator.attrgetter(v1)(self)
        var2 = operator.attrgetter(v2)(self)

        try:
            if not (var1.is_effort() and var2.is_effort()):
                raise TypeError('v1 and v2 must be names of existing Variables, and these '
                                'variables should be efforts. '
                                'You may set attribute by using var.type_port = "effort"')
            assert isinstance(var1, IndexedVar) and isinstance(var2, IndexedVar), \
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
        self.graph.add_edge(v1, v2)

        return


class DynUnitTest(DynUnit):
    """ Dynamic Test Unit """

    def __init__(self, *args, time=None, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.e = Var(time, within=NonNegativeReals)
        self.p = DerivativeVar(self.e, wrt=time)

    # def connect(port1, port2, name='_connect'):
    # # effort connection
    # f = lambda m, t: eval(port1 + '[t] == ' + port2 + '[t]')
    # locals()[name] = f
    # return f


Unit.compute_statistics = PyomoModel.compute_statistics
Unit.graph = LModel.graph
Unit.update_graph = LModel.update_graph
