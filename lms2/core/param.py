"""
Parameter class.

Definition of some additional attributes to the pyomo Param Class.
"""

from pyomo.core.base.param import Param


@property
def port_type(self):
    """getter method for the 'port_type' argument. """
    if not hasattr(self, '_port_type'):
        self._port_type = None
    return self._port_type


@port_type.setter
def port_type(self, type):
    """setter method for the port_type.
    'flow' or 'effort' types are supported. """
    assert type in ['flow', 'effort'], f'Argument port_type should be either "flow" or "effort", but received {type}.'
    self._port_type = type


def is_flow(self):
    """ Test is the variable is an flow quantity.
        return True or False"""
    return self.port_type == 'flow'


def is_effort(self):
    """ Test is the variable is an effort quantity.
        return True or False"""
    return self.port_type == 'effort'


@property
def sens(self):
    """ getter method for argument 'sens' of the variable object.
    This value is just a convention but it is used for connection
    purpose between optimisation variable."""
    if not hasattr(self, '_sens'):
        self._sens = None
    return self._sens


@sens.setter
def sens(self, sens):
    """ setter method for argument 'sens' of the variable object.
    Argument 'sens' should be either "in" or "out".
    This value is just a convention but it is used for connection
    purpose between optimisation variable.
    """
    if sens in ['in', 'out']:
        self._sens = sens
    else:
        msg = f'Argument "sens" should be either "in" or "out", but received {sens}.'
    return


Param.port_type = port_type
Param.sens = sens
Param.is_effort = is_effort
Param.is_flow = is_flow
