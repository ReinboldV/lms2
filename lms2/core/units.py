# -*- coding: utf-8 -*-
"""
Unit Class.

Basic block for linear Modeling.
"""
from lms2.core.models import LModel

from pyomo.environ import Objective, Var, NonNegativeReals
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.base.PyomoModel import Model as PyomoModel
from pyomo.core.base.block import SimpleBlock, Block

from networkx import Graph
import logging

__all__ = ['Unit', 'DynUnit', 'DynUnitTest']
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

    def __setattr__(self, key, value):

        super().__setattr__(key, value)
        logger.debug(f'adding the attribute : {key} = {value}')


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
        self.doc = self.__doc__

    def get_constraints_values(self):
        return

    def get_duals(self):
        return


class DynUnitTest(DynUnit):
    """ Dynamic Test Unit """

    def __init__(self, *args, time=None, **kwds):
        super().__init__(*args, time=time, doc=self.__doc__, **kwds)

        self.e = Var(time, within=NonNegativeReals)
        self.p = DerivativeVar(self.e, wrt=time)


Unit.compute_statistics = PyomoModel.compute_statistics


if __name__ == '__main__':
    pass





