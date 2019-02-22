# -*- coding: utf-8 -*-
from lms2 import LModel, Battery, MainGrid, ScalablePowerSource, PowerLoad

from pyomo.dae.contset import ContinuousSet


class DrahixMicrogridV2(LModel):
    """
    Build the microgrid of the DrahiX problem
    """
    def __init__(self, dataframe, name='DrahiX_MicroGrid'):
        """

        :param str name: Name of the model
        :param pandas.DataFrame dataframe: dataframe for input profils
        """

        from pyomo.environ import Suffix

        super().__init__(name=name)

        needed_series = ['P_pv', 'P_load']
        for s in needed_series:
            assert s in dataframe, f'No key named {s}'

        self.t = ContinuousSet(bounds=(dataframe.index[0], dataframe.index[-1]))
        self.bat1 = Battery(time=self.t, e0=100.0, ef=100, emin=5.0, emax=500, etac=0.96, etad=0.96, pcmax=20, pdmax=20)
        self.mg = MainGrid(time=self.t, cin=0.08, cout=0.15, pmax=500, pmin=500, mixco2=70)
        self.ps = ScalablePowerSource(time=self.t, profile=dataframe['P_pv'], c_use=0.01)
        self.pl = PowerLoad(time=self.t, profile=dataframe['P_load'], flow_name='p')
        self.connect_flux(self.bat1.p, self.ps.p, self.mg.p, self.pl.p)
        self.dual = Suffix(direction=Suffix.IMPORT)


def to_seconds(timedelta):
    return timedelta.days*24*3600 + timedelta.seconds + timedelta.microseconds/1e6

