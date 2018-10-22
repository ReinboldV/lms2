"""
Time class.
"""
from pyomo.core.base.block import SimpleBlock


class Time(object):
    """Class that defines the time of a unit or model

    Examples::

        Create a Time instance::

            >>> th = Time(start=0, end=24, freq = '30Min')
            >>> th.dt
            1800.0

        or ::

            >>> th = Time('2017-01-01', '2017-01-02', freq = '2H')
            >>> th.dt
            7200.0

    .. _tab_tag_freq:

    .. table:: Freq available tags in Pandas

        ====== ==============================================
        Tag     Description
        ====== ==============================================
        B       business day frequency
        C       custom business day frequency (experimental)
        D       calendar day frequency
        W       weekly frequency
        M       month end frequency
        BM      business month end frequency
        CBM     custom business month end frequency
        MS      month start frequency
        BMS     business month start frequency
        CBMS    custom business month start frequency
        Q       quarter end frequency
        BQ      business quarter endfrequency
        QS      quarter start frequency
        BQS     business quarter start frequency
        A       year end frequency
        BA      business year end frequency
        AS      year start frequency
        BAS     business year start frequency
        BH      business hour frequency
        H       hourly frequency
        T, min  minutely frequency
        S       secondly frequency
        L, ms   milliseonds
        U, us   microseconds
        N       nanoseconds
        ====== ==============================================
    """

    def __init__(self, start=None, end=None, freq=None, *args, **kwds):
        """

        :param args:
        :param kwds:
        :param start: starting value, datetime-like
        :param end: end time, datetime-like
        :param freq: string or pandas offset object
        """
        super().__init__(*args, **kwds)
        import pandas as pd
        from numpy import linspace
        from pandas.tseries.frequencies import to_offset

        if freq is None:
            freq = 'H'
            self.freq = freq

        if isinstance(start, str) and isinstance(end, str):
            try:
                self.start = pd.Timestamp(start)
                self.end = pd.Timestamp(end)
            except ValueError as e:
                raise e
            try:
                self.freq = to_offset(freq)
            except Exception as e:
                raise e

            self.datetime = pd.DatetimeIndex(freq=freq, start=start, end=end)
            self.delta = (self.end - self.start).delta / 1e9  # period in seconds
            self.dt = self.datetime.freq.delta.value / 1e9  # time step in seconds
            self.timeSteps = linspace(0, self.delta, num=len(self.datetime))  # time steps in seconds
            self.map = pd.Series(self.datetime, index=self.timeSteps)
            self.index = self.map.index

        elif isinstance(start, int) and isinstance(end, int):
            self.end = end
            self.start = start
            try:
                self.freq = to_offset(freq)
            except Exception as e:
                raise e
            self.dt = self.freq.delta.value / 1e9  # period in seconds
            self.timeSteps = linspace(start, end, num=end / self.dt + 1)
            self.delta = end - start
            self.map = None
            self.index = None
        else:
            pass

        self.len = len(self.timeSteps)

        from pyomo.dae.contset import ContinuousSet
        # self.time_set = OrderedSimpleSet(initialize=self.index*self.dt)   # ordered set for pyomo use in seconds
        self.time_contSet = ContinuousSet(bounds=(0, self.delta))         # continuous set for pyomo in seconds


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
