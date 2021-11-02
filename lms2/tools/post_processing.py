"""plotting and saving of optimisation results"""

from pandas import Series


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
            ld = Series({i: v() for i, v in variable.items()}).sort_index().plot(
                label=variable.name.replace('_', '\_'),
                fig=fig, ax=ax, **kwarg)
        else:
            s = Series({i: v() for i, v in variable.items()}).sort_index()
            s.index = index
            ld = s.plot(label=variable.name.replace('_', '\_'), fig=fig, ax=ax, **kwarg)

    elif isinstance(variable, Constraint):
        if index is None:
            ld = Series({i: v() for i, v in variable.items()}).sort_index().plot(
                label=variable.name.replace('_', '\_'),
                fig=fig,
                ax=ax,
                **kwarg)

            up = Series({i: v.uslack() for i, v in variable.items()}).sort_index().plot(
                label=variable.name.replace('_', '\_')+'_uslack',
                fig=fig,
                color = ld.lines[-1].get_color(),
                lineStyle = '--',
                ax=ax,
                **kwarg)

            low = Series({i: v.lslack() for i, v in variable.items()}).sort_index().plot(
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


def pplot(*args, ax=None, fig=None, legend=True, title=None, grid=True, **kwargs):
    """
    Function that plots pyomo Variable or Parameter

    :param var: Var or Param to be plotted
    :param index: New index for plotting purpose (optional)
    :param fig: figure handle (optional)
    :param ax: axes handle (optional)
    :param kwarg: any Series.plot keyword argument
    :return:
        - arg1 the matplotlib.pyplot.Figure handle object
        - arg2 the matplotlib.pyplot.Axes handle object
        - arg3 the matplotlib.pyplot.Line2D handle object

    Key word arguments :
        - ncol : number of columns for legend
        - loc : location of legend (see matplotlib.pyplot)
        - bbox_to_anchor
        - mode :


    Example:
        >>> from pyomo.environ import ConcreteModel
        >>> from pyomo.dae import ContinuousSet
        >>> from lms2.core.horizon import SimpleHorizon
        >>> from pyomo.environ import Var

        >>> m = ConcreteModel('test_utils')
        >>> horizon = SimpleHorizon(tstart='00:00:00', tend='01:00:00', time_step='5 Min')
        >>> m.time = ContinuousSet(initialize=[0, horizon.horizon.total_seconds()])
        >>> m.v = Var(m.time, initialize=lambda b, x: x%60)
        >>> m.w = Var(m.time, initialize=lambda b, x: x//60)
        >>> m.z = Var(m.time, initialize=lambda b, x: x//(60*60))

        >>> lines = pplot(m.v, m.z, m.w, title='test', Marker='x')
    """

    ncol = kwargs.pop('ncol', 1)
    loc = kwargs.pop('loc', 'lower center')
    bbox_to_anchor = kwargs.pop('bbox_to_anchor', None)
    mode = kwargs.pop('mode', None)

    lines = []
    ld, up, low, ax, fig = _pplot(args[0], ax=ax, fig=fig, **kwargs)
    if up is not None:
        lines.append(up)
    if low is not None:
        lines.append(low)

    lines.append(ld)

    for var in args[1:]:
        ld, up, low, ax, fig = _pplot(var, ax=ax, fig=fig, **kwargs)
        lines.append(ld)
        if up is not None:
            lines.append(up)
        if low is not None:
            lines.append(low)

    if legend:
        ax.legend(bbox_to_anchor=bbox_to_anchor, loc=loc,
                  mode=mode, borderaxespad=0.4, ncol=ncol)
    if title is not None:
        ax.set_title(title)
    if grid:
        ax.grid(True)

    return lines, ax, fig