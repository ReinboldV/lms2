# -*- coding: utf-8 -*-
"""
Unit Class.

Basic block for linear Modeling.
"""
from lms2.core.models import LModel

from pyomo.environ import Objective, Param, Var, NonNegativeReals, Constraint, Expression, Block, Set
from pyomo.network import Port
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.base.PyomoModel import Model as PyomoModel
from pyomo.core.base.block import SimpleBlock, Block

from networkx import Graph
import logging

__all__ = ['Unit']
logger = logging.getLogger('lms2.units')


class Unit(SimpleBlock):
    """
    redefinition of SimpleBlock
    """

    def __init__(self, *args, **kwds):
        """

        :param args:
        :param kwds:
        """
        super().__init__(*args, **kwds)
        logger.info(f'Initiation of {self.name} {self.__class__}')

    def _construct_objective(self):
        """
        Construction of the objectives.

        When using Continuous Set, the implicit expression such as sum(x[t] for t in Time)
        must be created after time discrimination. Otherwise, the expression will only consider
        existing timeSteps.
        To overcome this behaviour, this method allows to automatically redefine objectives after time discretization.

        TODO : should be used in some rare cases. Normally, the Integral object should be able to do the trick.
        """

        for block in self.component_map(active=True, ctype=Block):
            try:
                block.construct_objective()
            except OSError as err:
                raise err

        for obj in self.component_map(active=True, ctype=Objective):
            rule = self.component(obj).rule
            self.del_component(obj)
            self.add_component(obj, Objective(rule=rule))

    def fix_binary(self):
        """
        Fix binary variables to their values

        :return:
        """
        for u in self.component_objects(Var):
            if u.is_indexed():
                for ui in u.itervalues():
                    if ui.is_binary():
                        ui.fix(ui.value)
            else:
                if u.is_binary():
                    u.fix(u.value)

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

    def get_doc(self):
        """
        dev function to print documentation

        :return: doc
        """

        doc = ""

        blocks  = self.component_objects(ctype=Block)
        sets    = self.component_objects(ctype=Set)
        vars    = self.component_objects(ctype=Var)
        dvars   = self.component_objects(ctype=DerivativeVar)
        params  = self.component_objects(ctype=Param)
        cst     = self.component_objects(ctype=Constraint)
        ports   = self.component_objects(ctype=Port)
        exp     = self.component_objects(ctype=Expression)

        doc += '\n\n' + 'Blocks: \n----------\n\n'
        for k in blocks:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + 'Sets: \n------\n\n'
        for k in sets:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n'+'Variables: \n----------\n\n'
        for k in vars:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n'+'DerivativeVar: \n---------------\n\n'
        for k in dvars:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n'+'Param: \n------\n\n'
        for k in params:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + 'Constraints: \n-----------\n\n'
        for k in cst:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + 'Ports: \n------\n\n'
        for k in ports:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + 'Expressions: \n---------\n\n'
        for k in exp:
            doc += '{:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'

        return doc

    def __setattr__(self, key, value):

        super().__setattr__(key, value)
        logger.debug(f'adding the attribute : {key} = {value}')

Unit.compute_statistics = PyomoModel.compute_statistics

if __name__ == '__main__':
    pass