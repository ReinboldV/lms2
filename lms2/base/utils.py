# -*- coding: utf-8 -*-

"""
Utils and tool for linearization and plots
"""

from pandas import Series


def _pplot(variable, index=None, fig=None, ax=None, **kwarg):
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
        >>> from lms2.core.var import Var

        >>> time = Time(start='00:00:00', end='01:00:00', freq='5Min')
        >>> m = LModel('test_utils')
        >>> m.v = Var(time.datetime, initialize=10)
        >>> m.w = Var(time.datetime, initialize=5)
        >>> m.z = Var(time.datetime, initialize=3)

        >>> lines = pplot(m.v, m.z, m.w, title='test', Marker='x')
    """

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
            ld = Series(variable.get_values()).sort_index().plot(label=variable.name, fig=fig, ax=ax, **kwarg)
        else:
            s = Series(variable.get_values()).sort_index()
            s.index = index
            ld = s.plot(label=variable.name, fig=fig, ax=ax, **kwarg)

    elif isinstance(variable, Param):
        if index is None:
            ld = Series(variable.extract_values()).sort_index().plot(label=variable.name, fig=fig, ax=ax, **kwarg)
        else:
            s = Series(variable.extract_values()).sort_index()
            s.index = index
            ld = s.plot(label=variable.name, fig=fig, ax=ax, **kwarg)
    else:
        raise(NotImplementedError(f'Argument "variable" must be of type Param or Var, but is actually'
                                  f'{variable, type(variable)}'))

    return ld, ax, fig


def pplot(*args, ax=None, fig=None, legend=True, title=None, grid=True, **kargs):

    lines = []
    ld, ax, fig = _pplot(args[0], ax=ax, fig=fig, **kargs)
    lines.append(ld)
    for var in args[1:]:
        ld, ax, fig = _pplot(var, ax=ax, fig=fig, **kargs)
        lines.append(ld)

    if legend:
        ax.legend()
    if title is not None:
        ax.set_title(title)
    if grid:
        ax.grid(True)

    return lines, ax, fig


if __name__ == '__main__':

    from lms2.core.models import LModel
    from lms2.core.time import Time
    from lms2.core.var import Var

    from pyomo.environ import *
    import matplotlib.pyplot as plt

    time = Time(start='00:00:00', end='01:00:00', freq='5Min')
    m = LModel('test_utils')
    m.v = Var(time.datetime, initialize=10)
    m.w = Var(time.datetime, initialize=5)
    m.z = Var(time.datetime, initialize=3)

    l, a, f = pplot(m.v, m.z, m.w, title='test', Marker='x')
    plt.show()
