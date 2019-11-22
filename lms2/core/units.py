# -*- coding: utf-8 -*-
"""
Unit Class.

Basic block for modeling components.
"""

from pyomo.environ import Objective, Param, Var, Constraint, Expression, Set
from pyomo.network import Port
from pyomo.dae.diffvar import DerivativeVar
from pyomo.core.base.PyomoModel import Model as PyomoModel
from pyomo.core.base.block import SimpleBlock, Block

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
        logger.info(f'Initiation of {self.name}...')

    def _construct_objective(self):
        """
        Construction of the objectives.

        When using Continuous Set, the implicit expression such as sum(x[t] for t in Time)
        must be created after time discrimination. Otherwise, the expression will only consider
        existing timeSteps.
        To overcome this behaviour, this method allows to automatically redefine objectives after time discretization.

        ..note: should be used in some rare cases. Normally, the Integral object should be able to do the trick.
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

    def get_doc_2(self):
        """
        dev function to print documentation v2

        :return: doc
        """

        doc = ""

        if len(list(self.component_objects(ctype=Set))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Sets            Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Set):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=Block))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Blocks          Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Block):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=Var))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Variables       Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Var):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=DerivativeVar))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Derivative Var  Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=DerivativeVar):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=Param))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Parameters      Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Param):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=Constraint))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Constraints     Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Constraint):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=Port))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Ports           Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Port):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        if len(list(self.component_objects(ctype=Expression))) != 0:
            doc += '=============== ===================================================================\n'
            doc += 'Expressions     Documentation                                                      \n'
            doc += '=============== ===================================================================\n'
            for k in self.component_objects(ctype=Expression):
                doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
            doc += '=============== ===================================================================\n\n'

        return doc

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

        doc += '\n\n' + '**Blocks:** \n\n'
        for k in blocks:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + 'Sets: \n\n'
        for k in sets:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n'+'**Variables:** \n\n'
        for k in vars:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n'+'**DerivativeVar:** \n\n'
        for k in dvars:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n'+'**Param:** \n\n'
        for k in params:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + '**Constraints:** \n\n'
        for k in cst:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + '**Ports:** \n\n'
        for k in ports:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\n\n' + '**Expressions:** \n\n'
        for k in exp:
            doc += '- {:<15}  {:<50}'.format(k.getname(), str(k.doc)) + '\n'

        return doc

    def sync_first_step(inst, horizon, old_sol):

        from drahix.strategy.tools import _STATUS

        print('start:', horizon.tstart, 't end:', horizon.tend)

        for b in inst.component_objects(ctype=Block, descend_into=True):
            for v in b.component_objects(ctype=Var):
                if horizon._status == _STATUS[0]:

                    ## initializz using initial_rule or initial value in the variable definition,
                    # if not defined : does nothing and throw a warning

                    if v.is_indexed():  # could be nice if could be sure it is indexed by the time !
                        if v._value_init_value is not None:
                            value = v[0]._value_init_value
                            v[0].fix(value)
                            logger.debug(f'{v.name} has been fixed to value : {value} '
                                         f'for indice 0, iteration {horizon.iter},'
                                         f' corsponding to time stamp {horizon.current[0]}')
                        elif v._value_init_rule is not None:
                            value = v[0]._value_init_rule(inst, 0)
                            v[0].fix(value)
                            logger.debug(f'{v.name} has been fixed to value : {value} '
                                         f'for indice 0, iteration {horizon.iter},'
                                         f' corsponding to time stamp {horizon.current[0]}')
                        else:
                            Warning(
                                f'Has no effect : There are no initial_value or initial_rule to initialize '
                                f'the variable {v.name}.')
                    else:
                        pass

                # Initialize using former solution.
                # For the new horizon, all variables are fixed to the solution found earlier.
                # For indexed variable, only index = 0 is fixed, for not indexed variable, it is fixed.

                elif horizon._status in [_STATUS[1], _STATUS[2]]:
                    if v.is_indexed():  # could be nice if could be sure it is indexed by the time !
                        tstamp = horizon.current[0]
                        value = old_sol[v.name].loc[tstamp]
                        v[0].fix(value)
                        logger.debug(f'{v.name} has been fixed to value : {value} '
                                     f'for indice 0, iteration {horizon.iter},'
                                     f' corsponding to time stamp {horizon.current[0]}')
                    else:
                        v.fix(old_sol[v.name])
                        logger.debug(f'{v.name} has been fixed to value : {value}')


    def __setattr__(self, key, value):

        super().__setattr__(key, value)
        logger.debug(f'adding the attribute : {key} = {value}')

Unit.compute_statistics = PyomoModel.compute_statistics

if __name__ == '__main__':
    pass