import pandas as pd
import numpy as np


def date_generator(start, end, n, freq='D'):
    """
    Random date generator

    :param start: start time stamp (default format : '2018-01-01 00:00:00')
    :param end: end time stamp (default format : '2018-01-01 00:00:00')
    :param freq: time step (default : '1 day')
    :param n: number of generated dates
    :return:
    """
    dr = pd.date_range(start, end, freq=freq)
    return pd.to_datetime(np.sort(np.random.choice(dr, n, replace=False)))


class SimpleHorizon(object):

    def __init__(self,
                 tstart='2018-01-01 00:00:00',
                 tend='2019-01-01 00:00:00',
                 time_step='15 minutes',
                 tz="Europe/Paris"):
        """
         Simple horizon description

        The horizon is defined by a starting and ending time stamp, time_step and time zone information.
        Time stamps and time delta may be strings (using default pandas format) or `pandas.Timestamp` and
        `pandas.Timedelta` instances.

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

    def __repr__(self):
        return f'SimpleHorizon(tstart={self.TSTART}, tend={self.TEND}, time_step={self.time_step}, nfe={self.nfe})'


    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, t):
        raise NotImplementedError('NotImplemented, user can not set the current horizon him or herself.')


class MultipleHorizon(list):
    """
    Multiple horizon description

    The horizon is defined by a starting and ending time stamp, time_step and time zone information.
    Time stamps and time delta may be strings (using default pandas format) or `pandas.Timestamp` and
    `pandas.Timedelta` instances.

    """
    def __init__(self, duration, mode='deterministic', num=None, tstart='2018-01-01 00:00:00',
                 tend='2019-01-01 00:00:00', time_step='15 minutes', tz="Europe/Paris"):
        """

        :param tstart: start time stamp (default format : '2018-01-01 00:00:00')
        :param tend: end time stamp (default format : '2018-01-01 00:00:00')
        :param time_step: time step, used for discretization (default : '15 minutes')
        :param tz: time zone (default : "Europe/Paris")
        """
        super().__init__()

        assert mode in ['deterministic', 'stochastic'], 'Unknown mode...'

        if num is None and mode == 'deterministic':
            num = (pd.Timestamp(tend) - pd.Timestamp(tstart)) // pd.Timedelta(duration)
            assert num >= 2, 'Horizon is not long enough to create multiple horizon. Consider change Tend, ' \
                             'Tstart or duration of sub-horizon.'

        elif num is None:
            assert mode != 'stochastic', 'Stochastic mode needs the number of sub-horizon.'

        if mode == 'deterministic':
            start = pd.Timestamp(tstart)
            for i in np.arange(num):
                start += i*pd.Timedelta(duration)
                end = start + pd.Timedelta(duration)
                self.append(SimpleHorizon(tstart=start, tend=end, tz=tz, time_step=time_step))

        if mode == 'stochastic':
            starts = date_generator(start=pd.Timestamp(tstart), end=pd.Timestamp(tend)-pd.Timedelta(duration), n=num)
            ends = starts + pd.Timedelta(duration)
            for i in np.arange(num):
                self.append(SimpleHorizon(tstart=starts[i], tend=ends[i], tz=tz, time_step=time_step))