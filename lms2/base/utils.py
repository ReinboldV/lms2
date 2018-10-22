from lms2.core.var import Var
import matplotlib.pyplot as plt
from pandas import Series
from pandas import DataFrame


def _pplot(var, fig=None, ax=None, **kwarg):
    """
    Function that plots Varibale or Parameter

        :param var: Var or Param to be plotted
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

        >>> from pyomo.environ import *

        >>> time = Time(start='00:00:00', end='01:00:00', freq='5Min')
        >>> m = LModel('test_utils')
        >>> m.v = Var(time.datetime, initialize=10)
        >>> m.w = Var(time.datetime, initialize=5)
        >>> m.z = Var(time.datetime, initialize=3)

        >>> lines = pplot(m.v, m.z, m.w, title='test', Marker='x')


    """
    #    if not isinstance(q, Var) :
    #       raise TypeError('the argument q is not a pyomo Variable !')
    assert isinstance(var, Var) or isinstance(var, Param), f"var should be of type Var" \
                                                           f" o Param, but is actually {type(var)}."

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

    ld = Series(var.get_values()).sort_index().plot(label=var.name, **kwarg)

    return ld, ax, fig


def pplot(*args, ax=None, fig=None, legend=True, title=None, **kargs):

    lines=[]
    ld, ax, fig = _pplot(args[0], ax=ax, fig=fig, **kargs)
    lines.append(ld)
    for var in args[1:]:
        ld, ax, fig = _pplot(var, ax=ax, fig=fig, **kargs)
        lines.append(ld)

    if legend:
        plt.legend()
    if title is not None:
        plt.title(title)

    return lines, ax, fig