# -*- coding: utf-8 -*-
"""
Contains hysteresis model.
"""
from pyomo.core import Var, Binary, Constraint

__all__ = ['add_phase']


class Hysteresis(object):
    """ Linear hysteresis model

    Attributes
    
        - u : logical output
        - x : continuous input
        - xref : reference input value
        - dx : windows size
        - a : logical intermediate variable
        - b : logical intermediate variable
        - c : logical intermediate variable
    """

    pass

    # def __init__(b, time_horizon, name='hys0', description='logical hysteresis', xr=None, dxm=1, dxM=1, xM=100, xm=100, init_x=0):
    #
    #     """
    #
    #     :param time_horizon: time
    #     :param name: unit name
    #     :param description: short description
    #     :param xr: reference input value
    #     :param dxm:
    #     :param dxM:
    #     :param xM: upper bound of x
    #     :param xm: lower bound of x
    #     """
    #     import numpy as np
    #
    #     if xr is None:
    #         xr = np.zeros(time_horizon.len)
    #
    #     TUnit.__init__(b, time_horizon, name=name, description=description)
    #
    #     b.addquantity(name='u', pl={-1: init_x}, opt=True, vtype='B', vlen=time_horizon.len)
    #     b.addquantity(name='a', opt=True, vtype='B', vlen=time_horizon.len)
    #     b.addquantity(name='b', opt=True, vtype='B', vlen=time_horizon.len)
    #     b.addquantity(name='x', opt=True, vlen=time_horizon.len)
    #     b.addquantity(name='dxm', value=dxm, opt=False)
    #     b.addquantity(name='dxM', value=dxM, opt=False)
    #     b.addquantity(name='xr', value=xr, opt=False)
    #     b.addquantity(name='xM', value=xM, opt=False)
    #     b.addquantity(name='xm', value=xm, opt=False)
    #
    #     exp = """
    #     (xr[t]-dxm) + (xM - xr[t] + dxm)*a[t]   >= x[t]  for t in T
    #     xm + (xr[t] - dxm - xm)*a[t]            <= x[t]  for t in T
    #     (xr[t] + dxM) + (xM - xr[t] - dxM)*b[t] >= x[t]  for t in T
    #     xm + (xr[t] + dxM - xm)*b[t]            <= x[t]  for t in T
    #     u[t] + a[t]                             >= 1 for t in T
    #     1 - u[t]                                >=  b[t] for t in T
    #     u[t]                                    >= a[t] - b[t] + u[t-1] - 1  for t in T
    #     1 - u[t]                                >= a[t] - b[t] - u[t-1] for t in T """
    #
    #     b.addconst(name='cst', exp=exp)


def add_phase(self, prefix='1', name='new phase', start_up=True, shut_down=True):

    """
    Method to introduce a phase to a block.

    This function declare a binary variable indexed by the time.
    It also declare binary variables for starting up, called `su` and shutting down, called `sd`.
    This is used for example in battery charging phases and imposing minimal up-time,
    minimal down-time or number of starting up and shutting down.

    :param self: Parent block
    :param str prefix: Prefix to be added to the created variables (e.g.:  with prefix = '1',
    the created variabled will be called u_1)
    :param str name: Name to be display in the documentation
    :param start_up: Not used for now
    :param shut_down: Not used for now
    :return:
    """

    self.add_component(f'u{prefix}',   Var(self.time, within=Binary, doc=f'{name} is running'))
    self.add_component(f'su{prefix}',  Var(self.time, within=Binary, doc=f'starting of {name}'))
    self.add_component(f'sd{prefix}',  Var(self.time, within=Binary, doc=f'stoping of {name}'))
    self.add_component(f'mu{prefix}',  Var(self.time, within=Binary, doc=f'intermediary binary variable for the '
                                                                         f'starting-up of {name}.'))
    self.add_component(f'md{prefix}',  Var(self.time, within=Binary, doc=f'intermediary binary variable for the'
                                                                         f' shutting down of {name}.'))

    def _start1(m, t):
        u  = m.find_component(f'u{prefix}')
        su = m.find_component(f'su{prefix}')

        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return u[m.time[idx]] - u[m.time[idx - 1]] <= su[m.time[idx]]
        else:
            return Constraint.Skip
    self.add_component(f'_start1_{prefix}',
                       Constraint(self.time, rule=_start1, doc=f'start up constraint 1 for {name}'))

    def _start2(m, t):
        su = m.find_component(f'su{prefix}')
        mu = m.find_component(f'mu{prefix}')
        return su[t] <= mu[t]

    self.add_component(f'_start2_{prefix}',
                       Constraint(self.time, rule=_start2, doc=f'start up constraint 2 for {name}'))

    def _start3(m, t):
        mu = m.find_component(f'mu{prefix}')
        u  = m.find_component(f'u{prefix}')
        return mu[t] <= u[t]

    self.add_component(f'_start3_{prefix}',
                       Constraint(self.time, rule=_start3, doc=f'start up constraint 3 for {name}'))

    def _start4(m, t):
        mu = m.find_component(f'mu{prefix}')
        u  = m.find_component(f'u{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return mu[m.time[idx]] <= 1 - u[m.time[idx - 1]]

    self.add_component(f'_start4_{prefix}',
                       Constraint(self.time, rule=_start4, doc=f'start up constraint 4 for {name}'))

    def _stop1(m, t):
        u  = m.find_component(f'u{prefix}')
        sd = m.find_component(f'sd{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return u[m.time[idx - 1]] - u[m.time[idx]] <= sd[m.time[idx]]
        else:
            return Constraint.Skip

    self.add_component(f'_stop1_{prefix}',
                       Constraint(self.time, rule=_stop1, doc=f'shutting down constraint 1 for  {name}'))

    def _stop2(m, t):
        md = m.find_component(f'md{prefix}')
        sd = m.find_component(f'sd{prefix}')
        return sd[t] <= md[t]

    self.add_component(f'_stop2_{prefix}',
                       Constraint(self.time, rule=_stop2, doc=f'shutting down constraint 2 for {name}'))

    def _stop3(m, t):
        md = m.find_component(f'md{prefix}')
        u  = m.find_component(f'u{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return md[t] <= u[m.time[idx - 1]]

    self.add_component(f'_stop3_{prefix}',
                       Constraint(self.time, rule=_stop3, doc=f'shutting down constraint 3 for {name}'))

    def _stop4(m, t):
        md = m.find_component(f'md{prefix}')
        u  = m.find_component(f'u{prefix}')
        for (i, tmp) in enumerate(sorted(m.time)):
            if t == tmp:
                idx = i + 1
                if idx == 1:
                    return Constraint.Skip
                else:
                    return md[m.time[idx]] <= 1 - u[m.time[idx]]

    self.add_component(f'_stop4_{prefix}',
                       Constraint(self.time, rule=_stop4, doc=f'shutting down constraint 4 for {name}'))