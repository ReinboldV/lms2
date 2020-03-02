# -*- coding: utf-8 -*-

"""
Utils and tool for linearization and plots
"""

from pandas import Series

__all__ = ['pplot', 'get_slack', 'get_doc_2', 'get_duals']


def _pplot(variable, index=None, fig=None, ax=None, **kwarg):
    """
    Function that plots pyomo Variable, Parameter, Expression and Constraint

    For Constraint, the function returns the value of the constraint's expression, the upper slack variable,
    and the lower slack variable (if not None)

        :param var: Var or Param to be plotted
        :param index: New index for plotting purpose (optional)
        :param fig: figure handle (optional)
        :param ax: axes handle (optional)
        :param kwarg: any Series.plot keyword argument
        :return:  line handle, (upper line), (lower line), axe handle, figure handle

    **Returns**
        - arg1 the matplotlib.pyplot.Figure handle object
        - arg2 the matplotlib.pyplot.Axes handle object
        - arg3 the matplotlib.pyplot.Line2D handle object

    Example::
        >>> from lms2.core.models import LModel
        >>> from lms2.core.time import Time
        >>> from pyomo.environ import Var

        >>> time = Time(start='00:00:00', end='01:00:00', freq='5Min')
        >>> m = LModel('test_utils')
        >>> m.v = Var(time.datetime, initialize=10)
        >>> m.w = Var(time.datetime, initialize=5)
        >>> m.z = Var(time.datetime, initialize=3)

        >>> lines = pplot(m.v, m.z, m.w, title='test', Marker='x')
    """
    import matplotlib.pyplot as plt
    from pyomo.environ import Var, Param, Expression, Constraint

    up = None
    low = None

    if fig is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    elif isinstance(fig, plt.Figure):
        if ax is None:
            ax = fig.add_subplot(111)
        elif not isinstance(ax, plt.Axes):
            raise ValueError(
                'ax should be either None or matplotlib.pyplot.Axes')
    else:
        raise ValueError('fig should be either None or a Figure.')

    if isinstance(variable, Var):
        if index is None:
            ld = Series(variable.get_values()).sort_index().plot(label=variable.name.replace('_', '\_'), fig=fig,
                                                                 ax=ax, **kwarg)
        else:
            s = Series(variable.get_values()).sort_index()
            s.index = index
            ld = s.plot(label=variable.name.replace('_', '\_'), fig=fig, ax=ax, **kwarg)

    elif isinstance(variable, Param):
        if index is None:
            ld = Series(variable.extract_values()).sort_index().plot(label=variable.name.replace('_', '\_'), fig=fig,
                                                                     ax=ax, **kwarg)
        else:
            s = Series(variable.extract_values()).sort_index()
            s.index = index
            ld = s.plot(label=variable.name.replace('_', '\_'), fig=fig, ax=ax, **kwarg)

    elif isinstance(variable, Expression):
        if index is None:
            ld = Series({i: v() for i, v in variable.iteritems()}).sort_index().plot(
                label=variable.name.replace('_', '\_'),
                fig=fig, ax=ax, **kwarg)
        else:
            s = Series({i: v() for i, v in variable.iteritems()}).sort_index()
            s.index = index
            ld = s.plot(label=variable.name.replace('_', '\_'), fig=fig, ax=ax, **kwarg)

    elif isinstance(variable, Constraint):
        if index is None:
            ld = Series({i: v() for i, v in variable.iteritems()}).sort_index().plot(
                label=variable.name.replace('_', '\_'),
                fig=fig,
                ax=ax,
                **kwarg)

            up = Series({i: v.uslack() for i, v in variable.iteritems()}).sort_index().plot(
                label=variable.name.replace('_', '\_')+'_uslack',
                fig=fig,
                color = ld.lines[-1].get_color(),
                lineStyle = '--',
                ax=ax,
                **kwarg)

            low = Series({i: v.lslack() for i, v in variable.iteritems()}).sort_index().plot(
                label=variable.name.replace('_', '\_') + '_lslack',
                fig=fig,
                color=ld.lines[-1].get_color(),
                lineStyle='-.',
                ax=ax,
                **kwarg)

        else:
            s = Series([v() for v in variable.values()])
            s.index = index
            ld = s.plot(label=variable.name.replace('_', '\_'), fig=fig, ax=ax, **kwarg)

    else:
        raise (NotImplementedError(f'Argument "variable" must be of type Param or Var, but is actually'
                                   f'{variable, type(variable)}'))

    return ld, up, low, ax, fig


def pplot(*args, ax=None, fig=None, legend=True, title=None, grid=True, **kargs):
    """
    Function that plots pyomo Variable or Parameter

        :param var: Var or Param to be plotted
        :param index: New index for plotting purpose (optional)
        :param fig: figure handle (optional)
        :param ax: axes handle (optional)
        :param kwarg: any Series.plot keyword argument
        :return:  line handle, axe handle, figure handle

    **Returns**
        - arg1 the matplotlib.pyplot.Figure handle object
        - arg2 the matplotlib.pyplot.Axes handle object
        - arg3 the matplotlib.pyplot.Line2D handle object

    Example::
        >>> from lms2.core.models import LModel
        >>> from lms2.core.time import Time
        >>> from pyomo.environ import Var

        >>> time = Time(start='00:00:00', end='01:00:00', freq='5Min')
        >>> m = LModel('test_utils')
        >>> m.v = Var(time.datetime, initialize=10)
        >>> m.w = Var(time.datetime, initialize=5)
        >>> m.z = Var(time.datetime, initialize=3)

        >>> lines = pplot(m.v, m.z, m.w, title='test', Marker='x')
    """

    ncol = kargs.pop('ncol', 4)
    loc = kargs.pop('loc', 'lower left')
    bbox_to_anchor = kargs.pop('bbox_to_anchor', (0, 1.02, 1, 0.2))
    mode = kargs.pop('mode', "expand")

    lines = []
    ld, up, low, ax, fig = _pplot(args[0], ax=ax, fig=fig, **kargs)
    if up is not None:
        lines.append(up)
    if low is not None:
        lines.append(low)

    lines.append(ld)

    for var in args[1:]:
        ld, up, low, ax, fig = _pplot(var, ax=ax, fig=fig, **kargs)
        lines.append(ld)
        if up is not None:
            lines.append(up)
        if low is not None:
            lines.append(low)

    if legend:
        ax.legend(bbox_to_anchor=bbox_to_anchor, loc=loc,
                  mode=mode, borderaxespad=0, ncol=ncol)
    if title is not None:
        ax.set_title(title)
    if grid:
        ax.grid(True)

    return lines, ax, fig


def get_doc_2(bloc):
    """
    Function that create automatic documentation of a Pyomo block, based on variables, parametres, constraint, etc.

    :return: Docstring tabular
    """
    from pyomo.environ import Set, Block, Var, Param, Constraint, Expression
    from pyomo.dae import DerivativeVar
    from pyomo.network import Port

    doc = ""

    if len(list(bloc.component_objects(ctype=Set))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Sets            Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Set):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Block))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Blocks          Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Block):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Var))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Variables       Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Var):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=DerivativeVar))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Derivative Var  Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=DerivativeVar):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Param))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Parameters      Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Param):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Constraint))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Constraints     Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Constraint):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Port))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Ports           Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Port):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    if len(list(bloc.component_objects(ctype=Expression))) != 0:
        doc += '=============== ===================================================================\n'
        doc += 'Expressions     Documentation                                                      \n'
        doc += '=============== ===================================================================\n'
        for k in bloc.component_objects(ctype=Expression):
            doc += '{:<15} {:<50}'.format(k.getname(), str(k.doc)) + '\n'
        doc += '=============== ===================================================================\n\n'

    return doc


from pyomo.environ import Constraint, Var


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


if __name__ == '__main__':
    from pyomo.environ import AbstractModel
    from lms2.electric.batteries import BatteryV0

    m = AbstractModel()
    m.b = BatteryV0()
    print(get_doc_2(m.b))
