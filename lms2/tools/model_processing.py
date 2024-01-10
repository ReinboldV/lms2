"""transformation and processing of models or blocks"""

from pyomo.environ import *


def fix_binary(model):
    """
    Fix binary variables to their values

    :return:
    """

    from pyomo.environ import RealSet

    for u in model.component_objects(Var):
        if u.is_indexed():
            for ui in u.itervalues():
                if ui.is_binary():
                    ui.fix(ui.value)
                    ui.domain = RealSet([0, 1])
        else:
            if u.is_binary():
                u.fix(u.value)
                u.domain = RealSet([0, 1])


def unfix_binary(model):
    """
    Unfix binary variables

    :return:
    """
    for u in model.component_objects(Var):
        if u.is_indexed():
            for ui in u.itervalues():
                if ui.is_binary():
                    ui.unfix()
        else:
            if u.is_binary():
                u.unfix()


def get_duals(model, dual_name='dual'):
    """
    Return dual coefficient of LP abstract model.

    :param str dual_name: name of the Suffix

    :return : Dual coefficient (DataFrame)
    """
    from pandas import DataFrame, concat
    from pyomo.environ import Constraint
    df = DataFrame()

    assert hasattr(model, dual_name), f'"{model.name}" does not have attribute named "{dual_name}".'

    for cst in model.component_objects(Constraint, active=True):
        if cst.is_indexed():
            s = DataFrame(
                {cst.getname(fully_qualified=True) + '_' + dual_name: {i: model.component(dual_name)[c]
                                                                       for (i, c) in cst.iteritems()}})
            df = concat([df, s], axis=1)
        else:
            Warning('Trying to get dual coefficient from a non-index variable. Not Implemented Yet')
    return df


def get_slack(model):
    """
    Return slack variables values for all
    the active constraints of a abstract model.

    :return: DataFrame
    """

    from pandas import DataFrame, Series, concat

    df = DataFrame()
    for c in model.component_objects(Constraint, active=True):
        if c.is_indexed():
            s1 = Series({i: c[i].lslack() for i in c.__iter__()})
            s2 = Series({i: c[i].uslack() for i in c.__iter__()})
            df_c = DataFrame(
                {c.getname(fully_qualified=True).replace('.', '_') + '_ls': s1, c.getname() + '_us': s2})
            df = concat([df, df_c], axis=1)
    return df


def get_doc(bloc):
    """
    Function that create automatic documentation of a Pyomo block, based on variables, parametres, constraint, etc.

    :return: Docstring tabular
    """
    from pyomo.environ import Set, Block, Var, Param, Constraint, Expression
    from pyomo.dae import DerivativeVar
    from pyomo.network import Port

    doc = ""
    table_directive = f'.. table:: \n' \
                      f'    :width: 100% \n\n'

    if len(list(bloc.component_objects(ctype=Set))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tSets            Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Set):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Block))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tBlocks          Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Block):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Var))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tVariables       Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Var):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=DerivativeVar))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tDerivative Var  Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=DerivativeVar):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Param))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tParameters      Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Param):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Constraint))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tConstraints     Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Constraint):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Port))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tPorts           Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Port):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Expression))) != 0:
        doc += table_directive
        doc += '\t=============== ===================================================================\n'
        doc += '\tExpressions     Documentation                                                      \n'
        doc += '\t=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Expression):
            doc += '\t{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '\t=============== ===================================================================\n\n'

    return doc


def construct_objective(self):
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