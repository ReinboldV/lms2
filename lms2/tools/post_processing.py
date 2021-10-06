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