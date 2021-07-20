import pandas as pd
import numpy as np


class SimpleHorizon(object):
    """
    Simple horizon description

    The horizon is defined by a starting and ending time stamp, time_step and time zone information.
    Time stamps and time delta may be strings (using default pandas format) or `pandas.Timestamp` and
    `pandas.Timedelta` instances.

    """
    def __init__(self,
                 tstart='2018-01-01 00:00:00',
                 tend='2019-01-01 00:00:00',
                 time_step='15 minutes',
                 tz="Europe/Paris"):
        """

        :param tstart: start time stamp (default format : '2018-01-01 00:00:00')
        :param tend: end time stamp (default format : '2018-01-01 00:00:00')
        :param time_step: time step, used for discretization (default : '15 minutes')
        :param tz: time zone (default : "Europe/Paris")
        """

        self.tz_info  = tz
        self._current = None

        try:
            self.TSTART     = pd.Timestamp(tstart).tz_localize(self.tz_info)
            self.TEND       = pd.Timestamp(tend).tz_localize(self.tz_info)
            self.time_step  = pd.Timedelta(time_step)
        except ValueError as e:
            raise e

        self._current = pd.date_range(start=self.TSTART, freq=self.time_step, end=self.TEND)
        self.horizon = self.TEND - self.TSTART
        self.status = 'INIT'

        assert self.horizon % self.time_step == pd.Timedelta('0s'), \
            "Parameter 'horizon' should be divisible by the chosen 'time_step'. " \
            "Otherwise, tend will not be present in the current horizon."

        assert 2 * self.time_step.total_seconds() <= self.horizon.total_seconds(), \
            "duration of the current horizon must contain at least 2 timestamps"

        self.index = np.linspace(0, self.horizon.total_seconds(), num=len(self._current))  # time steps in seconds
        self.map = pd.Series(self._current, index=self.index)
        self.nfe = len(self.index) - 1  # number of finite element for discretisation

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, t):
        raise NotImplementedError('NotImplemented, user can not set the current horizon him or herself.')
