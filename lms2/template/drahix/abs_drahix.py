from lms2 import AbsLModel, AbsBatteryV2, AbsMainGridV1, AbsMainGridV2, AbsScalablePowerSource, AbsFixedPowerLoad
from pyomo.dae import ContinuousSet
from pyomo.environ import Suffix
from pyomo.network import Arc

__all__ = ['AbsDrahiX_v1', 'AbsDrahiX_v2']

class AbsDrahiX_v1(AbsLModel):

    def __init__(self, name='DrahiX'):

        super().__init__(name=name)

        self.time   = ContinuousSet()
        self.batt   = AbsBatteryV2(doc='Battery')
        self.mg     = AbsMainGridV1(doc='Main Grid with bilinear costs')
        self.ps     = AbsScalablePowerSource(doc='Scalable Power Source')
        self.pl     = AbsFixedPowerLoad(doc='Fixed Power Load')
        self.arc3   = Arc(source=self.ps.outlet,    dest=self.pl.inlet)
        self.arc1   = Arc(source=self.mg.outlet,    dest=self.pl.inlet)
        self.arc2   = Arc(source=self.batt.outlet,  dest=self.pl.inlet)
        self.dual   = Suffix(direction=Suffix.IMPORT)


class AbsDrahiX_v2(AbsLModel):

    def __init__(self, name='DrahiX_v2'):

        super().__init__(name=name)

        self.time   = ContinuousSet()
        self.batt   = AbsBatteryV2(doc='Battery')
        self.mg     = AbsMainGridV2(doc='Main Grid with dynamic bilinear costs')
        self.ps     = AbsScalablePowerSource(doc='Scalable Power Source')
        self.pl     = AbsFixedPowerLoad(doc='Fixed Power Load')
        self.arc3   = Arc(source=self.ps.outlet,    dest=self.pl.inlet)
        self.arc1   = Arc(source=self.mg.outlet,    dest=self.pl.inlet)
        self.arc2   = Arc(source=self.batt.outlet,  dest=self.pl.inlet)
        self.dual   = Suffix(direction=Suffix.IMPORT)