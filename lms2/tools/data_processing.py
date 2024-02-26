"""interpolation, decomposition and processing of input data"""

import logging

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

logger = logging.getLogger('lms2.tools.data_processing')

from pyomo.environ import *


def load_data(horizon, component, data, time_index_position=None):
    """
    Loading of data into the problem.

    :param m: the model
    :param data: vector of data (usually indexed by time)
    :param component: name of the parameter in the model
    :param index: name of the index in the model
    :return:

    See this example_.

    .. _example: ../examples/microgrid_1.html#Chargement-des-données

    """
    # Cannot actually test this, because components_slices does not have index_set method.
    # if data.index.name != component.index_set().name:
    #     logger.warning('data index and variable index does not have the same name. This could be a source of error...')

    if isinstance(component, pyomo.core.base.param.IndexedParam):
        for i, v in component.items():
            try:
                # we set the value of the parameter v to the value of the dataframe at the index i
                v.set_value(data[horizon.map[i]])
            except ValueError:
                print(f'Cannot set value {data[horizon.map[i]]} for {component.name}')

    # if param is a component slice, we cannt iterate over with the iter fonction
    elif isinstance(component, pyomo.core.base.indexed_component_slice.IndexedComponent_slice):
        if time_index_position is None:
            for v in component:
                index = v.index()[-1]
                v.set_value(data[horizon.map[index]])

        else:
            for v in component:
                index = v.index()[time_index_position]
                v.set_value(data[horizon.map[index]])



    else:
        raise NotImplementedError('Unsupported component type.')


def read_data(horizon, path, usecols=None, index_col=0, tz_data='Europe/Paris',
              fillnan=False, filldict={}, unit='s', method='time', date_parser=None, start_date=None):
    """
    Reading and interpolating data from csv source.

    This function accepts two types of indexed data :

        - data indexed by a date string ex: '2020/01/01 00:00:00'. In this case,
          a date-parser might be needed for pandas to parse the date.
        - data indexed by an integer. In this case, parsing is easier, and the user has to give a start date.

    :param method: interpolation method ('time' for date format index or 'linear' for integer index)
    :param str date_parser: date format parser, ex: "%Y-%m-%d %H:%M:%S"
    :param filldict:
    :param fillnan:
    :param usecols: list of useful colonnes of the file, ex: [0,1,5,8]
    :param horizon: Time horizon
    :param path: csv data file
    :param start_date: starting date (for integer index) ex: '2021-01-01 00:00:00'
    :param tz_data: time zone information ('UTC' or 'Europe/Paris')
    :return: pd.DataFrame

    See this example_.

    .. _example: ../examples/microgrid_1.html#Chargement-des-données

    """
    import os

    os.path.exists(path), f'Could not find the path {path}.'

    import datetime
    mydateparser = None
    if date_parser is not None:
        mydateparser = lambda x: datetime.datetime.strptime(x, date_parser)  # "%Y %m %d %H:%M:%S"

    # reading data file (all of it)
    # if usecols is not None:
    d1 = pd.read_csv(path,
                     index_col=index_col,
                     usecols=usecols,
                     parse_dates=True,
                     dayfirst=True,
                     date_parser=mydateparser)
    # else:
    #     d1 = pd.read_csv(path, index_col=index_col, parse_dates=True, dayfirst=True, date_parser=mydateparser)

    index_type = d1.index.dtype

    if type(d1.index) != pd.DatetimeIndex and start_date is None:
        logger.error('Could not parse index_col as a date. You must define the start_date of the data.')
        raise ValueError('start_time is None')
    if type(d1.index) != pd.DatetimeIndex and start_date is not None:
        try:
            start_date = pd.to_datetime(start_date)
        except:
            logger.error(f'Could not parse the start_date {start_date}')
        date_index = pd.TimedeltaIndex(d1.index) + pd.Timestamp(start_date)
        d1['date'] = pd.TimedeltaIndex(d1.index, unit=unit) + pd.Timestamp(start_date)
        d1[f'time ({unit})'] = d1.index
        d1 = d1.set_index('date')

    # Nan values must be filled before interpolating, the user can use fillnan and filldict to do this
    if fillnan:
        try:
            for d in filldict:
                d1[d] = d1[d].fillna(filldict[d])
        except KeyError as e:
            raise e

    # convert date time index to the correct time zone
    if type(d1.index) == pd.DatetimeIndex:
        if d1.index.tzinfo is None:
            d1.index = d1.index.tz_localize(tz_data, ambiguous=True, nonexistent='shift_forward').tz_convert(
                horizon.tz_info)
        else:
            d1.index = d1.index.tz_convert(horizon.tz_info)
        # be sure that the current horizon is in the data index set
        assert horizon.current[0] >= d1.index[0], \
            f"Start time {horizon.current[0]} is not include in data index : ({d1.index[0], d1.index[-1]})"
        assert horizon.current[-1] <= d1.index[-1], \
            f"End time {horizon.current[-1]} is not include in data index: ({d1.index[0], d1.index[-1]})"
    else:
        logger.warning('Could not parse index_col as a date. The time zone of the data cannot be determined.')

    # Synchronizing / Interpolating data to the current horizon date time index

    import warnings

    # if data are index by datetime index (of the form : '2021:01:01 00:00:00')
    if type(d1.index) == pd.DatetimeIndex:
        dh1 = pd.DataFrame([np.NaN] * len(horizon.current), index=horizon.current, columns=['tmp'])
    # if data are index by  int64 (supposed to be seconds, for instance [0, 600, 800, 1500, ...])
    elif index_type == np.int64:
        dh1 = pd.DataFrame([np.NaN] * len(horizon.current), index=horizon.index, columns=['tmp'])

    with warnings.catch_warnings():
        # Pandas 0.24.1 emits useless warning when sorting tz-aware index
        warnings.simplefilter("ignore")

    if type(d1.index) == pd.DatetimeIndex and method == 'time':
        a = d1.join(dh1, how='outer').interpolate(method=method)
    if method == 'pad':
        a = d1.join(dh1, how='outer').sort_index().fillna(method='pad')
    elif method == 'linear' and index_type == np.int64:
        a = d1.join(dh1, how='outer').interpolate(method='linear')

    del a['tmp']
    # selecting only horizon period
    if type(d1.index) == pd.DatetimeIndex:
        data_horizon = a.loc[horizon.current]
    # if data are index by  int64 (supposed to be seconds, for instance [0, 600, 800, 1500, ...])
    elif index_type == np.int64:
        data_horizon = a.loc[horizon.index]

    return data_horizon


def interpolation(input_data, param, time, dt):
    """
    depreciated, use read_data()

    :param input_data: input data
    :param param: parameter to interpolate
    :param time: time to interpolate
    :param dt:
    :return:
    """

    columns_list = ['Time'] + param
    data = pd.DataFrame(columns=columns_list)
    time_temp = np.array(time)
    data['Time'] = list(time)
    for p in param:
        input_data_time = list(range(0, len(input_data[p]) * dt, dt))
        f = interp1d(input_data_time, list(input_data[p].values()))
        data[p] = list(f(time_temp))

    return data


if __name__ == "__main__":
    from lms2.core.horizon import SimpleHorizon

    path = '/home/admin/Documents/02-Recherche/02-Python/Matnik/data/base_loads.csv'
    horizon = SimpleHorizon(tstart='2021-01-01 00:00:00', tend='2021-01-08 00:00:00', time_step='15 min')

    d = read_data(horizon, path, usecols=[0, 1, 2, 3], method='time')

    print(d.head(10))
