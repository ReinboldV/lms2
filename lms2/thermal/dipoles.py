# -*- coding: utf-8 -*-
"""
Thermal dipole models
"""
from lms2.base.base_units import DynUnit

## DEPRECIATED

class TDipole(DynUnit):
    pass

    # def __init__(self, time_horizon, name='TD0', description='', t1=None, t2=None, q12=None):
    #     # type: (Time, str, str, object, object, object) -> TDipole
    #     """
    #     General class of a thermal dipole.
    #     By convention, q12 is the energy flow from pole 1 to pole 2.
    #     One can fix q12 or t1 or t2 or any other combination (eg. t1 & t2, )
    #
    #     :param time_horizon:
    #     :param name: the name
    #     :param description:
    #     :param t1: temperature of pole 1
    #     :param t2: temperature of pole 2
    #     :param q12: the heat flow
    #
    #
    #     Create a new thermal dipole with fixed temperature on pole 1::
    #
    #      >>> import numpy as np
    #      >>> from llmse.core.timehorizon import Time
    #      >>> from llmse.thermal.tdipole import TDipole
    #      >>> time_horizon = Time(0, 24, 'H')
    #      >>> t1 = np.ones(time_horizon.len)
    #      >>> tdip = TDipole(time_horizon, name = 'tdip', t1 = t1)
    #
    #     """
    #     super(TDipole, self).__init__(time_horizon, name, description)
    #
    #     if q12 is None:
    #         self.addquantity(name='q12', opt=True, index=time_horizon.index)
    #     else:
    #         self.addquantity(name='q12', opt=False, value=q12)
    #     if t1 is None:
    #         self.addquantity(name='t1', opt=True, index=time_horizon.index)
    #     else:
    #         self.addquantity(name='t1', opt=False, value=t1)
    #     if t2 is None:
    #         self.addquantity(name='t2', opt=True, index=time_horizon.index)
    #     else:
    #         self.addquantity(name='t2', opt=False, value=t2)
    #
    #     self.addpole(TPole('q12_in', self.quantities['q12'], self.quantities['t1'], 'in'),
    #                  TPole('q12_out', self.quantities['q12'], self.quantities['t2'], 'out'))


class TCondRes(DynUnit):
    pass
    # def __init__(self, time_horizon, name='TCdR0', description='', r=1, t1=None, t2=None, q12=None):
    #     """
    #     Simple thermal resistance.
    #
    #     :rtype: TCondRes
    #     :param time_horizon: (Time) time horizon
    #     :param str name: name
    #     :param str description: thermal resistance for conduction heat transfer
    #     :param float r: thermal resistance
    #     :param t1: temperature 1
    #     :param t2: temperature 2
    #     :param q12: heat flow
    #
    #     Minimize :  0
    #
    #     .. math::
    #
    #         q_{12}(t) = \\frac{1e^{-3}}{r}.(t_1(t)-t_2(t)) \\forall t
    #
    #     """
    #
    #     TDipole.__init__(self, time_horizon, name=name, description=description, t1=t1, t2=t2, q12=q12)
    #     self.addquantity(name='r', value=r, opt=False)
    #     if self.quantities['q12'].opt.all():
    #         exp = 'q12[t] == 1/r*1e-3*(t1[t]-t2[t]) for t in T'
    #     else:
    #         exp = '1/r*1e-3*(t1[t]-t2[t]) == q12[t] for t in T'
    #     self.addconst(name='cond', exp=exp)


class TCond(DynUnit):
    pass

    # def __init__(self, time_horizon, name='TCdR0', description='', r=1, t1=None, t2=None, q12=None):
    #     """
    #     Simple thermal resistance.
    #
    #     :param time_horizon: Time
    #     :param str name: unit name
    #     :param str description: short description
    #     :param r: thermal resistance
    #     :param t1: temperature 1
    #     :param t2: temperature 2
    #     :param q12: heat flow
    #
    #     Model
    #         Minimize :  0
    #
    #     .. math::
    #
    #         q_{12}(t) = \\frac{1e^{-1}}{r}.(t_1(t)-t_2(t)), \\forall t
    #
    #     """
    #
    #     TDipole.__init__(self, time_horizon, name=name, description=description, t1=t1, t2=t2, q12=q12)
    #     self.addquantity(name='r', value=r, opt=False)
    #     if self.quantities['q12'].opt:
    #         exp = 'q12[t] == 1/r*1e-3*(t1[t]-t2[t]) for t in T'
    #     else:
    #         exp = '1/r*1e-3*(t1[t]-t2[t]) == q12[t] for t in T'
    #     self.addconst(name='cond', exp=exp)


class TResNL(DynUnit):
    """ Non linear thermal resistance for forced heat convection modelling """
    pass

    # def __init__(self, time_horizon, name='TRNL0', description='', relax=False, rho=1., e=None, ne=None,
    #              emax=0.8, qa=None, nqa=None, qamin=0, qamax=0.5, cp=1004, t1=None, t2=None, q12=None):
    #     """
    #
    #
    #     :param time_horizon:
    #     :param name:
    #     :param description:
    #     :param relax:
    #     :param rho:
    #     :param e:
    #     :param ne:
    #     :param emax:
    #     :param qa:
    #     :param nqa:
    #     :param qamin:
    #     :param qamax:
    #     :param cp:
    #     :param t1:
    #     :param t2:
    #     :param q12:
    #
    #     """
    #     TDipole.__init__(self, time_horizon, name=name,
    #                      description=description, t1=t1, t2=t2, q12=q12)
    #
    #     if not relax:
    #         self.addquantity(name='cp', description='capacite thermique massique du gaz', value=cp, unit='J/(kg.k)', opt=False)
    #         self.addquantity(name='rho', description='masse volume du gaz', value=rho, unit='kg.m^3', opt=False)
    #
    #         if qa is None:
    #             if relax:
    #                 print("not implemented yet")
    #             else:
    #                 self.addquantity(name='qa', description='air flow', index=time_horizon.index, lb=qamin, ub=qamax, unit='m^3/s', opt=True)
    #         else:
    #             self.addquantity(name='qa', description='air flow', value=qa, unit='m^3/s', opt=False)
    #         if e is None:
    #             if relax:
    #                 print("not implemented yet")
    #             else:
    #                 self.addquantity(name='e', description='thermal exchanger efficiency (%)',
    #                                  lb=0, ub=emax, index=time_horizon.index, unit='m^3/s', opt=True)
    #         else:
    #             self.addquantity(name='e', description='thermal exchanger efficiency (%)', value=e, unit='m^3/s', opt=False)
    #
    #     if all(self.quantities['q12'].opt.values()):
    #         exp  = 'q12[t]*1e3 >= 0.99*rho*qa[t]*(1-e[t])*(t1[t]-t2[t]) for t in T'
    #         exp2 = 'q12[t]*1e3 <= 1.05*rho*qa[t]*(1-e[t])*(t1[t]-t2[t]) for t in T'
    #         self.addconst(name='cond2', exp=exp2)
    #         self.addconst(name='cond', exp=exp)


class TConvRes(DynUnit):
    """ Thermal resistance for convective heat transfer """
    pass

    # TODO create

    # def __init__(self, time_horizon, name='TCvR0', description='', h=1, s=1, t1=None, t2=None, q12=None):
    #     """
    #
    #     :param time_horizon: time horizon
    #     :param (str) name: name
    #     :param (str) description: thermal resistance for convection heat transfer
    #     :param (float) h: heat transfer coefficient
    #     :param (float) s: surface
    #     :param (float) t1: temperature on the 1st surface
    #     :param (float) t2: temperature on the second surface
    #     :param (float) q12: heat flow rate
    #     """
    #
    #     TDipole.__init__(self, time_horizon, name=name, description=description, t1=t1, t2=t2, q12=q12)
    #     self.addquantity(name='s', value=s, opt=False)
    #     self.addquantity(name='h', value=h, opt=False)
    #     exp = 'q12[t] == h*s*(t1[t]-t2[t])  for t in T'
    #     self.addconst(name='conv', exp=exp)


class TStorage(DynUnit):
    """ Thermal storage/capacity.   
     
    Model : 
    
    Minimize 0
         
    s.t.
 
    .. math::
        q_c(t) == 2.7778e^{-7}.m.c.\\frac{t_s(t - t_s(t-1)}{\\delta t} \\forall t
         
         
    """
    pass

    # def __init__(self, time_horizon, name='TSt0', description="Thermal storage connected to the ground, Euler's scheme",
    #              c=1, m=1, ts=None, ps_t=None, qc=None):
    #     """
    #
    #
    #     :param time_horizon: time horizon
    #     :param (str) name: name
    #     :param description: Termal storage
    #     :param c: thermal capacity
    #     :param m: mass
    #     :param ts: temperature of the thermal mass
    #     :param ps_t: initial temperature at t=0
    #     :param qc: heat flow
    #     """
    #     TUnit.__init__(self, time_horizon, name=name, description=description)
    #     if ps_t is None:
    #         ps_t = {-1: 0}
    #
    #     if qc is None:
    #         self.addquantity(name='qc', opt=True, index=time_horizon.index)
    #     else:
    #         self.addquantity(name='qc', opt=False, value=qc)
    #     if ts is None:
    #         self.addquantity(name='ts', pl=ps_t, lb=0, opt=True, index=time_horizon.index)
    #     else:
    #         self.addquantity(name='ts', pl=ps_t, lb=0, opt=False, value=ts)
    #
    #     self.addquantity(name='c', value=c, opt=False)
    #     self.addquantity(name='m', value=m, opt=False)
    #     exp = 'qc[t] == c*2.7778e-7*m*(ts[t] - ts[t-1])/dt for t in T'
    #     self.addconst(name='cst', exp=exp)
    #     self.addpole(TPole('tp', self.quantities['qc'], self.quantities['ts'], 'in'))


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)