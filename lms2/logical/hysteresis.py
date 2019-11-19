# -*- coding: utf-8 -*-
"""
Contains hysteresis model.
"""


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

    # def __init__(self, time_horizon, name='hys0', description='logical hysteresis', xr=None, dxm=1, dxM=1, xM=100, xm=100, init_x=0):
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
    #     TUnit.__init__(self, time_horizon, name=name, description=description)
    #
    #     self.addquantity(name='u', pl={-1: init_x}, opt=True, vtype='B', vlen=time_horizon.len)
    #     self.addquantity(name='a', opt=True, vtype='B', vlen=time_horizon.len)
    #     self.addquantity(name='b', opt=True, vtype='B', vlen=time_horizon.len)
    #     self.addquantity(name='x', opt=True, vlen=time_horizon.len)
    #     self.addquantity(name='dxm', value=dxm, opt=False)
    #     self.addquantity(name='dxM', value=dxM, opt=False)
    #     self.addquantity(name='xr', value=xr, opt=False)
    #     self.addquantity(name='xM', value=xM, opt=False)
    #     self.addquantity(name='xm', value=xm, opt=False)
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
    #     self.addconst(name='cst', exp=exp)
