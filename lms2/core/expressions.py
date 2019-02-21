# -*- coding: utf-8 -*-
"""
Different types of objectives

In order to automatically recognize different type of objectives or cost from different part of the system.
We define several property for the pyomo Expression class.
Such as tag, unit, sens, etc.
"""

from pyomo.core.base import minimize, maximize
from pyomo.environ import Expression

_tags = ['COST', 'PROSUMTION', 'CO2', 'ENERGY', None]
_units = ['euros', 'W.h', 'kg_eq', 'W.h', None]
_conv = [minimize, maximize, None]


# @property
def tag(self):
    return self._tag


# @tag.setter
def settag(self, tag):
    if tag in _tags:
        self._tag = tag
    else:
        print('test')
        raise Warning(f'{tag} is not a valide tag. By default available tags are : "{_tags}".')


# @tag.getter
def gettag(self):
    return self._tag


# @tag.deleter
def deltag(self):
    if hasattr(self, '_tag'):
        del self._tag


doc_tag = 'tag argument is used to group the expression and helps to construct meta-expression. ' \
          'For instance, it can be used for summing all the Expression tagged with the same tag "COST".'


Expression.tag = property(gettag, settag, deltag, doc_tag)
exp = Expression()


def sens(self):
    return self._sens


def setsens(self, sens):
    if sens in _conv:
        self._sens = sens
    else:
        raise Warning(f'{sens} is not a valide sens. By default, available sens are {_conv}.')


def getsens(self):
    return self._sens


def delsens(self):
    if hasattr(self, '_sens'):
        del self._sens


doc_sens = 'sens is used to group the expression and helps to reconstruct meta-expression.' \
           'For instance it can be used to add expression to be minimized or maximized.'

Expression.sens = property(getsens, setsens, delsens, doc_sens)


def unit(self):
    return self._unit


def setunit(self, unit):
    if unit in _units:
        self._unit = unit
    else:
        raise Warning(f'{unit} is not a valide unit. By default, available sens are {_units}.')


def getsens(self):
    return self._sens


def delsens(self):
    if hasattr(self, '_sens'):
        del self._sens


doc_sens = 'sens is used to group the expression and helps to reconstruct meta-expression.' \
           'For instance it can be used to add expression to be minimized or maximized.'

Expression.sens = property(getsens, setsens, delsens, doc_sens)


if __name__ == '__main__':
    pass
