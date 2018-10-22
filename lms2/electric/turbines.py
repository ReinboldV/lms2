# -*- coding: utf-8 -*-
"""
This module contains the thermal power plants
"""


class SimpleThermalUnit(object):
    """ Simple thermal power Unit

    .. math:: 
    
        \\text{Find \\quad} & cost = \sum_t c_0.u(t) + c_1.p(t) + c_2.p(t)^2 \\\\
        \\text{Subject to \\quad} & p(t) \leqslant p_{max}.u(t),  \\ forall t  \\\\
        & \sum_t p(t) \leqslant e_{max}


    # Example ::
    #     >>> from llmse.core.timehorizon import Time
    #     >>> from llmse.electric.thermalunits import SimpleThermalUnit
    #     >>> th = Time(start=0, end=20, freq=1)
    #     >>> STU1 = SimpleThermalUnit(th, name='STU1', c=[45, 0.12, 0])
    #
    """
    pass
    # TODO create SimpleThermalUnit

    # def __init__(self, time_horizon, name="STU1", description='Simple Thermical Usine', pmax=1e100, emax=1e100, c=None, unit='kW'):
    #     """
    #     :param time_horizon: time
    #     :param name: unit name
    #     :param description: short description
    #     :param pmax: maximum output power
    #     :param emax: maximum output energy
    #     :param c: list of costs of use
    #     """
    #     TUnit.__init__(self, time_horizon, name=name, description=description)
    #
    #     if c is None:
    #         c = [10, 1, 0.01]
    #
    #     self.addquantity(name="p", lb=0, index=time_horizon.index, ub=1e100, unit=unit, description="instant power of the unit", opt=True)
    #     self.addquantity(name="pmax", value=pmax, unit=unit, opt=False, description='maximal genration power')
    #     self.addquantity(name="emax", value=emax, unit='kW.h', opt=False, description='maximal energy ')
    #     self.addquantity(name="u", vtype='B', index=time_horizon.index, opt=True, description='binary variable 0:shutOff & 1:working')
    #     self.addquantity(name="c", unit='kW.h', vlen=3, value=c, opt=False, description='constant, linear and quadratic instantaneous cost (euro,euro/W,euro/W^2)')
    #
    #     self.addconst(name='energyLimit', exp='quicksum([p[t] for t in T]) <= emax ')
    #     self.addconst(name='powerLimit', exp='p[t] <= pmax*u[t] for t in T')
    #
    #     cost = CostOfUse(name='cou', exp='quicksum([c[0]*u[t] + c[1]*p[t] + c[2]*p[t]*p[t] for t in T])')
    #     self.addobj(cost)
    #
    #     self.addpole(Epole("1", self.quantities["p"], 'out'))


class LimitedThermalUnit(SimpleThermalUnit):
    """ Thermal power Unit with limited variation

    This model, based on SimpleThermalUnit model, implement a output power variation constraint. 
    The cost function is quadratic but can be linearized thanks to the utils.LinQExp function

    Minimize:

     .. math:: cost = \sum_t c_0.u(t) + c_1.p(t) + c_2.p(t)^2

     s.t. :

     .. math::
         0 \leqslant p(t) \leqslant p_{max}.u(t), \\forall t  \\\\
         \\delta_m \leqslant p(t+1)-p(t) \leqslant \\delta_M, \\forall t \in [0,t_{end}-1] \\\\
         \\delta_m \leqslant p(0) \leqslant \\delta_M \\\\
         \sum_{t=0}^{T_{END}} p(t) \leqslant e_{max}

    """
    pass
    # TODO create LimitedThermalUnit

    # def __init__(self, time_horizon, name="LTU1", pmax=1e100, emax=1e100, c=None, deltaM=1e100, deltam=-1e100):
        # """
        #
        # :param time_horizon:
        # :param name:
        # :param pmax: maximal instantaneous power of the unit (W)
        # :param emax: maximal energy limit of the unit (W.h)
        # :param c: [c0, c1, c2]: the constant, linear and quadratic prices (euro, euro/W, euro/W²)
        # :param deltaM: maximal variation power (W/h)
        # :param deltam: minimal variation power (W/h)
        # """
        # SimpleThermalUnit.__init__(
        #     self, time_horizon, name=name, description='Thermical Usine wich power and power variation are limited', pmax=pmax, emax=emax, c=c)
        #
        # if c is None:
        #     c = [45, 10.2, 0.0052]
        #
        # self.addquantity(name='deltam', value=deltam, description='minimal variation of the instantaneous power of the unit',
        #                  unit='W/h', opt=False)
        # self.addquantity(name='deltaM', value=deltaM, description='maximal variation of the instantaneous power of the unit',
        #                  unit='W/h', opt=False)
        #
        # exp1 = 'p[t+1]-p[t] <= deltaM for t in T[:-1]'
        # exp2 = 'p[t+1]-p[t] >= deltam for t in T[:-1]'
        # exp3 = 'p[0] <= deltaM'
        # exp4 = 'p[0] >= deltam'
        #
        # self.addconst(name='powerVar1', exp=exp1)
        # self.addconst(name='powerVar2', exp=exp2)
        # self.addconst(name='powerVar3', exp=exp3)
        # self.addconst(name='powerVar4', exp=exp4)


class LimitedThermalUnit2(TUnit):
    """ Thermal power Unit with variation and start-up/shut-down constraints

    This model, based on the Unit model, implement a output power variation constraint, 
    and a start-up/shut-down trajectories constraintes. The cost function is linear.

    - Variables :
         * p : instant power of the unit (kW)
         * v : binary variable 1:working, 0:shutoff
         * y : binary variable 1:start-up
         * z : binary variable 1:shut-down
         * sy : binary variable 1:start-up phase
         * sz : binary variable 1:shut-down phase
         * ud : starting-up duration (h)
         * dd : shutting down duration (h)
         * pu : pre-specified power output in startingup period (kW)
         * pd : pre-specified power output in shoutdown period (kW)
         * pmax : maximal instantaneous power of the unit (kW)
         * pmin : minimal instantaneous power of the unit (kW)
         * c = [c0, c1, c2, c3]: the constant, the linear costs, and the start-up and shut down costs (euro/h, euro/(kW.h), euro/h, euro/h)
         * deltaM : maximal variation power (kW/h)
         * deltam : minimal variation power (kW/h)

    **Model**

    Minimize:

     .. math:: \\sum c_0.v(t).\\Delta T + c_1.\\frac{p(t)+p(t-1)}{2}.\\Delta T + c_2.y(t) + c_3.z(t) \ \\forall t

     s.t. :

     .. math::
         y(t) - z(t) &= v(t) - v(t-1)   \\forall t \\\\
         z(t) + y(t) &\leqslant 1   \\forall t \\\\
         sy(t) &=  \sum_{i=0}^{UD} y(t-i) \\forall t \\\\
         sz(t) &=  \sum_{i=0}^{DD} z(t+i+1) \\forall t  \\\\
         v(t) &\geqslant sz(t)  \\forall t  \\\\
         v(t) &\geqslant sy(t)  \\forall t \\\\
         p(t) &\geqslant p_{min}.\\left(v(t) - sz(t) - sy(t)\\right) +  \sum_{i=0}^{UD} pu(i).y(t-i)        \\forall t \\\\
         p(t) &\geqslant p_{min}.\\left(v(t) - sz(t) - sy(t)\\right) +  \sum_{i=0}^{DD} pd(i).z(t+i+1)      \\forall t \\\\
         p(t) &\leqslant p_{max}.\\left(v(t) - sy(t)\\right) +   \sum_{i=0}^{UD} pu(i).y(t-1)               \\forall t \\\\
         p(t) &\leqslant p_{max}.\\left(v(t) - sz(t)\\right) +   \sum_{i=0}^{DD} pd(i).z(t+i+1)             \\forall t \\\\
         \\frac{p(t)-p(t-1)}{\\delta t} &\leqslant p_{max}.sy(t) + \delta M.\\left(v(t) - sy(t)\\right)     \\forall t \\\\
         \\frac{p(t-1)-p(t)}{\\delta t} &\leqslant p_{max}.sz(t-1) + \delta m                               \\forall t \\\\

    """
    # TODO create LimitedThermalUnit2
    pass
    # def __init__(self, time_horizon, name="LTU2", description='', pmin=20., pmax=100., emax=1e100, c=None, deltam=20., deltaM=25., dd=2., ud=3.):
    #
    #     """
    #
    #     :param time_horizon:
    #     :param name:
    #     :param description:
    #     :param pmin:
    #     :param pmax:
    #     :param emax:
    #     :param c:
    #     :param deltam:
    #     :param deltaM:
    #     :param dd:
    #     :param ud:
    #     """
    #     TUnit.__init__(self, time_horizon, name=name, description=description)
    #
    #     if c is None:
    #         c = [100, 38e-3, 850., 56]
    #
    #     dd = np.ceil(dd / time_horizon.dt) * time_horizon.dt
    #     ud = np.ceil(ud / time_horizon.dt) * time_horizon.dt
    #     print('dd has been automatically change to {0}, for discret step time issue'.format(str(dd)))
    #     print('ud has been automatically change to {0}, for discret step time issue'.format(str(ud)))
    #
    #     if ud == 0.0:
    #         pu = []
    #     else:
    #         pu = np.arange(pmin / np.ceil(ud / time_horizon.dt), pmin + pmin /
    #                        np.ceil(ud / time_horizon.dt), pmin / np.ceil(ud / time_horizon.dt))
    #
    #     if dd == 0.0:
    #         pd = []
    #     else:
    #         pd = np.arange(pmin, pmin / np.ceil(dd / time_horizon.dt) - pmin /
    #                        np.ceil(dd / time_horizon.dt), -pmin / np.ceil(dd / time_horizon.dt))
    #         pd = pd[::-1]
    #
    #     ddi = int(dd / time_horizon.dt)
    #     udi = int(ud / time_horizon.dt)
    #
    #     # passed stages needed for the constraints : zero by default
    #     psv = {i: 0 for i in range(-udi - 1, 0)}
    #     psy = {i: 0 for i in range(-udi - 1, 0)}
    #     psz = {i: 0 for i in range(-udi - 1, 0)}
    #     pssz = {i: 0 for i in range(-udi - 1, 0)}
    #     pssy = {i: 0 for i in range(-udi - 1, 0)}
    #     psp = {i: 0 for i in range(-udi - 1, 0)}
    #
    #     self.addquantity(name="p", lb=0, value=psp, ub=pmax, index=time_horizon.index,
    #                      opt=True, description='instant power of the unit (W)')
    #     self.addquantity(name="v", value=psv, vtype='B', index=time_horizon.index, opt=True,
    #                      description='binary variable 0:shutOff & 1:working')
    #     self.addquantity(name="z", value=psy, vtype='B', index=time_horizon.index,
    #                      opt=True, description='binary variable 1:shutting down')
    #     self.addquantity(name="y", value=psz, vtype='B', index=time_horizon.index,
    #                      opt=True, description='binary variable 1:starting up')
    #     self.addquantity(name="sz", value=pssz, vtype='B', index=time_horizon.index,
    #                      opt=True, description='binary variable 1:shutdown phase')
    #     self.addquantity(name="sy", value=pssy, vtype='B', index=time_horizon.index,
    #                      opt=True, description='binary variable 1:startup phase')
    #
    #     self.addquantity(name="pmax", value=pmax, unit='kW', opt=False,
    #                      description='maximal genration power (kW)')
    #     self.addquantity(name='pmin', value=pmin, unit='kW', opt=False,
    #                      description='minimal generation power (kW)')
    #     self.addquantity(name="emax", value=emax, unit='kW.h',
    #                      opt=False, description='maximal energy (kW.h)')
    #     self.addquantity(name="c", unit='W.h', value=c, opt=False,
    #                      description='constant, linear and quadratic instantaneous cost (euro,euro/W,euro/W^2)')
    #     self.addquantity(name='dd', value=dd, unit='h', opt=False,
    #                      description='duration of the shut-down phase')
    #     self.addquantity(name='ddi', value=ddi, unit='h', opt=False,
    #                      description='duration of the shut-down phase')
    #     self.addquantity(name='ud', value=ud, unit='h', opt=False,
    #                      description='duration of the start up phase')
    #     self.addquantity(name='udi', value=udi, unit='h', opt=False,
    #                      description='duration of the start up phase')
    #     self.addquantity(name='pd', value=pd, unit='kW', opt=False,
    #                      description='pre-specified power output in shoutdown period')
    #     self.addquantity(name='pu', value=pu, unit='kW', opt=False,
    #                      description='pre-specified power output in startup period')
    #     self.addquantity(name='deltaM', value=deltaM, unit='kW.h-1', opt=False,
    #                      description='maximal positive variation of the power generation')
    #     self.addquantity(name='deltam', value=deltam, unit='kW.h-1', opt=False,
    #                      description='maximal negative variation of the power generation')
    #
    #     exp1 = 'y[t] - z[t] == v[t] - v[t-1] for t in T'
    #     self.addconst(name='vCst1', exp=exp1)
    #
    #     exp2 = 'sy[t] == quicksum([y[t-i] for i in range(udi)])  for t in T'
    #     self.addconst(name='vCst2', exp=exp2)
    #
    #     exp3 = 'sz[t] == quicksum([z[t+i+1] for i in range(min(ddi, T[-1] - t))])  for t in T'
    #     self.addconst(name='vCst3', exp=exp3)
    #
    #     exp4 = 'v[t] >= sz[t] for t in T'
    #     self.addconst(name='vCst4', exp=exp4)
    #
    #     exp5 = 'v[t] >= sy[t] for t in T'
    #     self.addconst(name='vCst5', exp=exp5)
    #
    #     # minimal power generation constraints for working phase (pmin), shutting down
    #     exp6 = 'p[t] >= pmin*(v[t] - sz[t] - sy[t]) + quicksum([pu[i]*y[t-i] for i in range(udi)]) for t in T'
    #     self.addconst(name='vCst6', exp=exp6)
    #
    #     exp7 = 'p[t] >= pmin*(v[t] - sz[t] - sy[t]) + quicksum([pd[i]*z[t+i+1] for i in range(min(ddi, T[-1] - t))]) for t in T'
    #     self.addconst(name='vCst7', exp=exp7)
    #
    #     exp8 = 'p[t] <= pmax*(v[t] - sy[t]) + quicksum([pu[i]*y[t-i] for i in range(udi)]) for t in T'
    #     self.addconst(name='vCst8', exp=exp8)
    #
    #     exp9 = 'p[t] <= pmax*(v[t] - sz[t]) + quicksum([pd[i]*z[t+i+1] for i in range(min(ddi, T[-1] - t))]) for t in T'
    #     self.addconst(name='vCst9', exp=exp9)
    #
    #     self.addconst(name='test', exp='z[t] + y[t] <= 1 for t in T')
    #
    #     exp11 = '(p[t]-p[t-1])/dt <= pmax*sy[t] + deltaM*(v[t] - sy[t]) for t in T'
    #     self.addconst(name='dpCst1', exp=exp11)
    #
    #     exp12 = '-(p[t]-p[t-1])/dt <= pmax*sz[t-1] + deltam*v[t] for t in T'
    #     self.addconst(name='dpCst2', exp=exp12)
    #
    #     cost = 'quicksum([c[0]*dt*v[t] + c[1]*dt*(p[t]+p[t-1])/2 + c[2]*y[t] + c[3]*z[t] for t in T])'
    #     self.cost = Objective(
    #         name='cost', exp=cost, description='functionning cost, taking into accoun constant, linear cossts and starting-up and shuting down costs')
    #
    #     self.poles = {'1': Epole('1', self.quantities["p"], 'out')}
