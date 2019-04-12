# -*- coding: utf-8 -*-
"""
Batteries' Module.

Contains electrical batteries linear models.
"""

from lms2 import AbsDynUnit

from pyomo.environ import Constraint, Var, Param, Expression, Piecewise, value
from pyomo.network import Port
from pyomo.dae.diffvar import DerivativeVar
from pyomo.dae import ContinuousSet
from pyomo.core.kernel.set_types import NonNegativeReals, Binary

__all__ = ['AbsBattery']
UB = 10e6

data = dict(
    time    = {None: (0,1)},
    socmin  = {None: 0    },
    socmax  = {None: 100  },
    dpcmax  = {None: None },
    dpcmin  = {None: None },
    emin    = {None: 0    },
    emax    = {None: None },
    pcmax   = {None: UB   },
    pdmax   = {None: UB   },
    e0      = {None: None },
    ef      = {None: None },
    etac    = {None: 1.0  },
    etad    = {None: 1.0  }
)

class AbsBattery(AbsDynUnit):
    """ Simple Battery """

    def __init__(self, *args, socmin=0, socmax=100, soc0=None, socf=None, emin=0, emax=UB, dpcmax=None, dpdmax=None,
                 pcmax=UB, pdmax=UB, e0=None, ef=None, etac=1, etad=1, **kwds):
        """

        :param time   : Continuous timeSet
        :param socmin : Minimal state of charge (%)
        :param socmax : Maximal state of charge (%)
        :param soc0   : Initial state of charge (%)
        :param socf   : Final state of charge (%)
        :param dpcmax : Maximum variation of power (kW/s) >0
        :param dpcmin : Minimal variation of power (kW/s) >0
        :param emin   : Minimum stored energy (kWh)
        :param emax   : Maximum stored energy (kWh)
        :param pcmax  : Maximum charging power (kW)
        :param pdmax  : Maximum descharging power (kW)
        :param e0     : Initial stored energy (default = 0)
        :param ef     : Final stored energy (default = None, i.e. no final constraint)
        :param etac   : Charging efficiency (\in [0, 1])
        :param etad   : Descharging efficiency (\in [0, 1])
        :param args:
        :param kwds:
        """

        super().__init__(*args, **kwds)

        self.p  = Var(self.time, doc='energy derivative with respect to time',  initialize=0, bounds = (-pcmax, pdmax))
        self.e  = Var(self.time, doc='energy in battery',                       initialize=0, within = NonNegativeReals)

        self.emin   = Param(default=emin,       doc='minimum energy (kWh)',       mutable=True, within=NonNegativeReals)
        self.emax   = Param(default=emax,       doc='maximal energy',             mutable=True)
        self.e0     = Param(default=e0,         doc='initial state',              mutable=True)
        self.ef     = Param(default=ef,         doc='final state',                mutable=True)
        self.etac   = Param(default=etac,       doc='charging efficiency',        mutable=True)
        self.etad   = Param(default=etad,       doc='discharging efficiency',     mutable=True)
        self.socmin = Param(default=socmin,     doc='minimum soc',                mutable=True)
        self.socmax = Param(default=socmax,     doc='maximal soc',                mutable=True)
        self.soc0   = Param(default=soc0,       doc='initial state',              mutable=True)
        self.socf   = Param(default=socf,       doc='final state',                mutable=True)
        self.dpdmax = Param(default=dpdmax,     doc='maximal discharging power',  mutable=True)
        self.dpcmax = Param(default=dpcmax,     doc='maximal charging power',     mutable=True)
        self.pcmax  = Param(default=pcmax,      doc='maximal charging power',     mutable=True, within=PositiveReals)
        self.pdmax  = Param(default=pdmax,      doc='maximal discharging power',  mutable=True, within=PositiveReals)

        self.de = DerivativeVar(self.e, wrt=self.time, initialize=0, doc='variation of energy  with respect to time')
        self.dp = DerivativeVar(self.p, wrt=self.time, initialize=0,
                                doc='variation of the battery power with respect to time',
                                bounds=lambda m,t : (-m.dpcmax, m.dpdmax))

        self.outlet = Port(initialize={'f': (self.p, Port.Conservative)})

        if etac is not None:
            assert etac <= 1, 'charging efficiency should be smaller than 1'
            assert etac > 0, 'charging efficiency should be strictly higher than 0'

        if etad is not None:
            assert etad <= 1, 'discharging efficiency should be smaller than 1'
            assert etad > 0, 'discharging efficiency should be strictly higher than 0'

        if ef is not None:
            assert ef <= emax, 'final energy state should be smaller than emax'
            assert ef >= emin, 'final energy state should be bigger than emin'

        def _p_init(m, t):
            if t == m.time.bounds()[0]:
                return m.p[t] == 0
            return Constraint.Skip

        def _e_initial(m, t):
            if m.e0.value is not None:
                if t == 0:
                    return m.e[t] == m.e0
            return Constraint.Skip

        def _e_final(m, t):
            if m.ef.value is None:
                return Constraint.Skip
            if t == m.time.last():
                return m.e[t] == m.ef
            else:
                return Constraint.Skip

        def _e_min(m, t):
            if m.emin.value is None:
                return Constraint.Skip
            return m.e[t] >= m.emin

        def _e_max(m, t):
            if m.emax.value is None:
                return Constraint.Skip
            return m.e[t] <= m.emax

        def _soc_init(m, t):
            if m.soc0.value is not None:
                if t == m.time.first():
                    return m.e[t] == m.soc0*m.emax*100
            return Constraint.Skip

        def _soc_final(m, t):
            if m.socf.value is None:
                return Constraint.Skip
            if t == m.time.last():
                return m.e[t] == m.socf*m.emax*100
            else:
                return Constraint.Skip

        def _soc_min(m, t):
            if m.socmin.value is None:
                return Constraint.Skip
            return m.e[t] >= m.socmin * m.emax / 100

        def _soc_max(m, t):
            if m.socmax.value is None:
                return Constraint.Skip
            return m.e[t] <= m.emax * m.socmax / 100

        def _dpcmax(m, t):
            if m.dpcmax.value is None:
                return Constraint.Skip
            else:
                return m.dp[t] >= -m.dpcmax

        def _dpdmax(m, t):
            if m.dpdmax.value is None:
                return Constraint.Skip
            else:
                return m.dp[t] <= m.dpdmax

        self._p_init    = Constraint(self.time, rule=_p_init,    doc='Initialize power')
        self._e_initial = Constraint(self.time, rule=_e_initial, doc='Initial energy constraint')
        self._e_final   = Constraint(self.time, rule=_e_final,   doc='Final stored energy constraint')
        self._e_min     = Constraint(self.time, rule=_e_min,     doc='Minimal energy constraint')
        self._e_max     = Constraint(self.time, rule=_e_max,     doc='Maximal energy constraint')
        self._soc_init  = Constraint(self.time, rule=_soc_init,  doc='Initial soc constraint')
        self._soc_final = Constraint(self.time, rule=_soc_final, doc='Final soc constraint')
        self._soc_min   = Constraint(self.time, rule=_soc_min,   doc='Minimal state of charge constraint')
        self._soc_max   = Constraint(self.time, rule=_soc_max,   doc='Maximal state of charge constraint')
        self._dpcmax    = Constraint(self.time, rule=_dpcmax,    doc='Maximal varation of charging power constraint')
        self._dpdmax    = Constraint(self.time, rule=_dpdmax,    doc='Maximal varation of descharging power constraint')

        self.soc = Expression(self.time, rule= lambda m, t : 100*m.e[t]/m.emax)

        def pw_rule(m, t, x):
            if x == 0:
                return 0
            elif x<0 :
                return x*m.etac/3600
            else:
                return x/m.etad/3600

        self.breakpoints = Set(initialize=[-pcmax, 0, pdmax])

        self.e_balance = Piecewise(self.time, self.de, self.p,
                                   pw_pts=[-pcmax, 0, pdmax], pw_repn='SOS2',
                                   pw_constr_type='EQ',
                                   f_rule=pw_rule)


        # TODO  : add different model of ageing.
        #  do bibliography and add model from D. TENFEN


    def simplify_piecewise(self):
        """
        Method used to simplify the Piecewise constraint
         on the energy balance in the case : etac = etad = 1.0.
         this cannot be easily done in the __init__ method when using a Abstract model.
        :return: 0
        """
        if self.is_constructed():
            if (self.etac.value == 1) & (self.etad.value == 1):
                self.del_component('e_balance')
                def _e_balance(m, t):
                    return m.de[t] == 1/3600*m.p[t]
                self.add_component('e_balance', Constraint(self.time, rule=_e_balance))



if __name__ == '__main__':

    from pyomo.environ import *
    from pyomo.dae import *

    m = AbstractModel()
    m.time = ContinuousSet(bounds=(0, 1))
    m.batt = AbsBattery()

    data_batt = dict(
        time    = {None: [0, 15]},
        socmin  = {None: 0      },
        socmax  = {None: 100    },
        soc0    = {None: 50     },
        socf    = {None: 50     },
        dpcmax  = {None: 10     },
        dpdmax  = {None: 10     },
        emin    = {None: 0      },
        emax    = {None: 500    },
        pcmax   = {None: UB     },
        pdmax   = {None: UB     },
        e0      = {None: 0      },
        ef      = {None: 50     },
        etac    = {None: 1.0    },
        etad    = {None: 1.0    })


    data = \
        {None:
            {
                'time'  : {None: [0, 10]},
                'batt'  : data_batt
            }
        }

    print('instantiation')
    inst = m.create_instance(data)
    TransformationFactory('dae.finite_difference').apply_to(inst, nfe=4)

    inst.batt.e_balance.pprint()
    inst.batt.simplify_piecewise()
    inst.batt.e_balance.pprint()

    inst.pprint()
