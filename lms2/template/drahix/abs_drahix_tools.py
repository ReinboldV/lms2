import matplotlib as mpl
import numpy as np
import pandas as pd

from lms2 import Time

def figsize(scale, nplots = 1):
    fig_width_pt = 390.0                            # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0/72.27                       # Convert pt to inch
    golden_mean = (np.sqrt(5.0)-1.0)/2.0            # Aesthetic ratio (you could change this)
    fig_width = fig_width_pt*inches_per_pt*scale    # width in inches
    fig_height = nplots*fig_width*golden_mean       # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size

pgf_with_latex = {                          # setup matplotlib to use latex for output
    "pgf.texsystem"     : "xelatex",        # change this if using xelatex or laulatex
    "text.usetex"       : True,             # use LaTeX to write all text
    "font.family"       : "serif",
    "font.serif"        : [],               # blank entries should cause plots to inherit fonts from the document
    "font.sans-serif"   : [],
    "font.monospace"    : [],
    "axes.labelsize"    : 10,               # LaTeX default is 10pt font.
    "font.size"         : 10,
    "legend.fontsize"   : 8,                # Make the legend/label fonts a little smaller
    "xtick.labelsize"   : 8,
    "ytick.labelsize"   : 8,
    "figure.figsize"    : figsize(1.0),     # default fig size of 0.9 textwidth
    'figure.subplot.bottom' : 0.145,
    'figure.subplot.hspace' : 0.2,
    'figure.subplot.left'   : 0.064,
    'figure.subplot.right'  : 0.97,
    'figure.subplot.top'    : 0.92,
    'figure.subplot.wspace' : 0.2,
    "pgf.preamble": [
        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)
        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble
        ]
    }

mpl.rcParams.update(pgf_with_latex)


def get_drahix_data(t_start='2018-06-01 00:00:00', t_end='2018-06-08 00:00:00', freq='15Min', **kwargs):

    usecols = ['Date and time (UTC)', 'T1', 'Pmax']
    df = pd.read_csv('/home/admin/Documents/02-Recherche/02-Python/lms2/lms2/template/drahix/abs_drahix_data.csv',
                     usecols=usecols, index_col=0, parse_dates=True, dayfirst=True)

    time = Time(t_start, t_end, freq=freq)
    df   = df[t_start:t_end]

    df.index    = to_seconds(df.index - df.index[0])
    df['Pmax']  = df['Pmax'].fillna(0) / 1000
    df.rename(columns={'Pmax': 'P_pv', 'T1': 'P_load'}, inplace=True)
    df = df.apply(lambda x: round(x, 5))

    return df, time


def to_seconds(timedelta):
    return timedelta.days * 24 * 3600 + timedelta.seconds + timedelta.microseconds / 1e6
