# -*- coding: utf-8 -*-

"""
CO2 concentration in a room
"""

class ModelCO2():
    """  Model of a CO2 concentration in a given volume.

    .. math::
        a+b &= c \\\\
        A-B &= C
    """
    pass
    # TODO create ModelCO2

    # def __init__(b, time_horizon, name='CO2', description='CO2 concentration model', n_occ=None, co2min=0., co2max=1000., ymin=120., ymax=500., n=4):
    #
    #     """
    #
    #     :param time_horizon:
    #     :param name:
    #     :param description:
    #     :param n_occ:
    #     :param co2min:
    #     :param co2max:
    #     :param ymin:
    #     :param ymax:
    #     :param n:
    #     """
    #     super(ModelCO2, b).__init__(time_horizon, name, description)
    #
    #     import numpy as np
    #
    #     amin = (co2min / co2max + ymin / ymax) / 2.
    #     amax = 1.
    #
    #     bmin = (co2min / co2max - 1.) / 2.
    #     bmax = (1. - ymin / ymax) / 2.
    #
    #     A = np.linspace(amin, amax, n)
    #     B = np.linspace(bmin, bmax, n)
    #     A2 = np.array(A)**2
    #     B2 = np.array(B)**2
    #
    #     iAB = range(len(A))
    #
    #     ua = np.zeros((time_horizon.len, n - 1))
    #     ub = np.zeros((time_horizon.len, n - 1))
    #     wa = np.zeros((time_horizon.len, n))
    #     wb = np.zeros((time_horizon.len, n))
    #
    #     b.addquantity(name='iAB', value=iAB, opt=False)
    #     b.addquantity(name='n', value=n, opt=False)
    #     b.addquantity(name='A', value=A, opt=False)
    #     b.addquantity(name='B', value=B, opt=False)
    #     b.addquantity(name='A2', value=A2, opt=False)
    #     b.addquantity(name='B2', value=B2, opt=False)
    #     b.addquantity(name='co2max', value=co2max, opt=False)
    #     b.addquantity(name='ymax', value=ymax, opt=False)
    #     b.addquantity(name='y', unit='', index=time_horizon.index, opt=True, lb=ymin, ub=ymax)
    #     b.addquantity(name='co2', pl={-1: 999}, index=time_horizon.index, opt=True, lb=co2min, ub=co2max)
    #     b.addquantity(name='pv', description='ventillation pression', unit='bar', opt=False, index=time_horizon.index,
    #                     value=np.ones(time_horizon.len))
    #     b.addquantity(name='yp', index=time_horizon.index, opt=True, lb=ymin / ymax, ub=1.)
    #     b.addquantity(name='co2p', pl={-1: 999. / co2max}, index=time_horizon.index, opt=True, lb=co2min / co2max, ub=1.,  parent=b)
    #     b.addquantity(name='a', index=time_horizon.index, opt=True, lb=amin, ub=amax)
    #     b.addquantity(name='b', index=time_horizon.index, opt=True, lb=bmin, ub=bmax)
    #     b.addquantity(name='zp', index=time_horizon.index, lb=-GRB.INFINITY, opt=True)
    #     b.addquantity(name='ua', vtype=GRB.BINARY, opt=True, value=ua)
    #     b.addquantity(name='ub', vtype=GRB.BINARY, opt=True, value=ub)
    #     b.addquantity(name='wa', opt=True, value=wa,lb=0, ub=1)
    #     b.addquantity(name='wb', opt=True, value=wb, lb=0, ub=1)
    #     b.addquantity(name='n_occ', opt=False, index=time_horizon.index, value=n_occ)
    #
    #     exp = """
    #     wa[t,i] + wa[t,i+1] >= ua[t,i] for i in iAB[:-1] for t in T
    #     wb[t,j] + wb[t,j+1] >= ub[t,j] for j in iAB[:-1] for t in T
    #     quicksum([ua[t,i] for i in iAB[:-1]]) == 1 for t in T
    #     quicksum([ub[t,j] for j in iAB[:-1]]) == 1 for t in T
    #     quicksum([wa[t,i]*A[i] for i in iAB]) == a[t] for t in T
    #     quicksum([wb[t,j]*B[j] for j in iAB]) == b[t] for t in T
    #     quicksum([wa[t,i] for i in iAB]) == 1 for t in T
    #     quicksum([wb[t,j] for j in iAB]) == 1 for t in T
    #     a[t] == (0.5*co2p[t-1] + 0.5*yp[t]) for t in T
    #     b[t] == (0.5*co2p[t-1] - 0.5*yp[t]) for t in T
    #     quicksum([wa[t,i]*A2[i] - wb[t,i]*B2[i] for i in iAB]) == zp[t] for t in T
    #     co2[t] == co2[t-1] + (n_occ[t]*1.2*40000.-zp[t]*co2max*ymax+y[t]*390.)*dt/650.45 for t in T
    #     co2p[t]*co2max == co2[t]   for t in T'
    #     yp[t]*ymax == y[t]  for t in T"""
    #
    #     b.addconst(name='cst1', exp=exp)
    #
    #     b.poles = {'1': Vpole('1', b.quantities['pv'], b.quantities['y'], 'out')}


class ModelCO2_bis():
    """
    Model of a CO2 concentration in a given volume.


    CO2(t)  = CO2(t-1) + (n_occ(t).Qp.CO2p - Qv(t).(CO2(t) - CO2a)).dt/V
            = CO2(t-1) + n_occ(t).Qp.CO2p.dt/V - Qv(t).CO2(t).dt/V + Qv(t).CO2a.dt/V

    """

    pass
    # TODO create ModelCO2_bis

    # def __init__(b, time_horizon, name='CO2', description='CO2 concentration model', n_occ=None, co2min=0., co2max=1000., ymin=120., ymax=500., n=4):
    #
    #     """
    #
    #     :param time_horizon:
    #     :param name:
    #     :param description:
    #     :param n_occ:
    #     :param co2min:
    #     :param co2max:
    #     :param ymin:
    #     :param ymax:
    #     :param n:
    #     """
    #     super(ModelCO2_bis, b).__init__(time_horizon, name, description)
    #     import numpy as np
    #
    #     amin = (co2min / co2max + ymin / ymax) / 2.
    #     amax = 1.
    #
    #     bmin = (co2min / co2max - 1.) / 2.
    #     bmax = (1. - ymin / ymax) / 2.
    #
    #     A = np.linspace(amin, amax, n)  # [0., 117., 235., 470.]#
    #     B = np.linspace(bmin, bmax, n)  # [-450., -235., -127.5, 20.]#
    #     A2 = np.array(A)**2
    #     B2 = np.array(B)**2
    #
    #     iAB = range(len(A))
    #
    #     ua = np.zeros((time_horizon.len, n - 1))
    #     ub = np.zeros((time_horizon.len, n - 1))
    #     wa = np.zeros((time_horizon.len, n))
    #     wb = np.zeros((time_horizon.len, n))
    #
    #     b.addquantity(name='iAB', value=iAB, opt=False)
    #
    #     b.addquantity(name='n', value=n, opt=False)
    #     b.addquantity(name='A', value=A, opt=False)
    #     b.addquantity(name='B', value=B, opt=False)
    #     b.addquantity(name='A2', value=A2, opt=False)
    #     b.addquantity(name='B2', value=B2, opt=False)
    #
    #     b.addquantity(name='co2max', value=co2max, opt=False)
    #     b.addquantity(name='ymax', value=ymax, opt=False)
    #
    #     b.addquantity(name='y', unit='', index=time_horizon.index, opt=True, lb=ymin, ub=ymax)
    #     b.addquantity(name='co2', pl={-1: 999}, index=time_horizon.index, opt=True, lb=co2min, ub=co2max)
    #
    #     b.addquantity(name='pv', description='ventillation pression', unit='bar', opt=False, index=time_horizon.index)
    #     b.addquantity(name='yp', index=time_horizon.index, opt=True, lb=ymin / ymax, ub=1.)
    #     b.addquantity(name='co2p', pl={-1: 999. / co2max}, index=time_horizon.index, opt=True, lb=co2min / co2max, ub=1.)
    #
    #     b.addquantity(name='a', index=time_horizon.index, opt=True,lb=amin, ub=amax)
    #     b.addquantity(name='b', index=time_horizon.index, opt=True,lb=bmin, ub=bmax)
    #     b.addquantity(name='zp', index=time_horizon.index, lb=-GRB.INFINITY, opt=True)
    #     b.addquantity(name='ua', vtype=GRB.BINARY, opt=True, value=ua)
    #     b.addquantity(name='ub', vtype=GRB.BINARY, opt=True, value=ub)
    #     b.addquantity(name='wa', opt=True, value=wa, lb=0, ub=1)
    #     b.addquantity(name='wb', opt=True, value=wb, lb=0, ub=1)
    #     b.addquantity(name='n_occ', opt=False, index=time_horizon.index, value=n_occ)
    #
    #     exp = '''wa[t,i] + wa[t,i+1] >= ua[t,i] for i in iAB[:-1] for t in T
    #     wb[t,j] + wb[t,j+1] >= ub[t,j] for j in iAB[:-1] for t in T
    #     quicksum([ua[t,i] for i in iAB[:-1]]) == 1 for t in T
    #     quicksum([ub[t,j] for j in iAB[:-1]]) == 1 for t in T
    #     quicksum([wa[t,i]*A[i] for i in iAB]) == a[t] for t in T
    #     quicksum([wb[t,j]*B[j] for j in iAB]) == b[t] for t in T
    #     quicksum([wa[t,i] for i in iAB]) == 1 for t in T
    #     quicksum([wb[t,j] for j in iAB]) == 1 for t in T
    #     a[t] == (0.5*co2p[t-1] + 0.5*yp[t]) for t in T
    #     b[t] == (0.5*co2p[t-1] - 0.5*yp[t]) for t in T
    #     quicksum([wa[t,i]*A2[i] - wb[t,i]*B2[i] for i in iAB]) == zp[t] for t in T
    #     co2[t] == co2[t-1] + (n_occ[t]*1.2*40000.-zp[t]*co2max*ymax+y[t]*390.)*dt/650.45 for t in T
    #     co2p[t]*co2max == co2[t]   for t in T
    #     yp[t]*ymax == y[t]  for t in T'''
    #
    #     b.addconst(exp, name='cst')
    #     b.poles = {'1': Vpole('1', b.quantities['pv'], b.quantities['y'], 'out')}
