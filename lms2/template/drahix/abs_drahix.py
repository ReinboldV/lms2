from lms2 import AbsLModel, AbsBatteryV2, AbsMainGridV1, AbsScalablePowerSource, AbsFixedPowerLoad
from pyomo.dae import ContinuousSet
from pyomo.environ import Suffix
from pyomo.network import Arc

__all__ = ['AbsDrahiX']

class AbsDrahiX(AbsLModel):

    def __init__(self, name='DrahiX'):

        super().__init__(name=name)

        self.time   = ContinuousSet()
        self.batt   = AbsBatteryV2(doc='Battery')
        self.mg     = AbsMainGridV1(doc='Main Grid')
        self.ps     = AbsScalablePowerSource(doc='Scalable Power Source')
        self.pl     = AbsFixedPowerLoad(doc='Fixed Power Load')
        self.arc3   = Arc(source=self.ps.outlet,    dest=self.pl.inlet)
        self.arc1   = Arc(source=self.mg.outlet,    dest=self.pl.inlet)
        self.arc2   = Arc(source=self.batt.outlet,  dest=self.pl.inlet)
        self.dual   = Suffix(direction=Suffix.IMPORT)