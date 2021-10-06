"""
Electrical sources and loads
"""

from pyomo.environ import *
from pyomo.core.base.set import Reals, PositiveReals, NonNegativeReals, Any
from pyomo.network import Port
from pyomo.dae import ContinuousSet
from pyomo.environ import units as u


__all__ = ['power_source', 'fixed_power_source', 'scalable_power_source',
           'power_load',   'fixed_power_load',   'scalable_power_load',
           'debug_source', 'pv_panel', 'curtailable_load']


# TODO unittest
def power_source(b, **kwargs):
    """ Power Source block

    Rule for defining a power source block. This rule add a variable and creates a output port.
    This block is using source convention, i.e. output power is counted positive.


    :param b: block
    :param kwargs: optional key-word arguments :

        - `time` : for dynamic index
        - `p_max` : maximal power (default : None)
        - `p_min` : minimal power (default : 0)
        - `var_name` : string for setting variable name (default : `p`)
        - `within` : Pyomo Set forvariable definition (default : Reals)
        - `doc` : setting documentation
        - `unit` : unit of the variable (default : kW)
        - `initialize` : set the initialize value of the variable (default : 0)

    :return: pyomo.Block

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               Power output flow (kW)
    =============== ===================================================================

    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    p_outlet        Power output port, using source convention (kW)
    =============== ===================================================================

    """
    unit = kwargs.pop('unit', 'kW')
    p_min = kwargs.pop('p_min', 0)
    p_max = kwargs.pop('p_max', None)
    var_name = kwargs.pop('var_name', 'p')
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.pop('doc', f'power source ({unit})')
    initialize = kwargs.pop('initialize', 0)
    within = kwargs.pop('within', Reals)

    b.add_component(var_name, Var(time, initialize=initialize, within=within, bounds=(p_min, p_max), doc=doc, units=unit))
    outlet_name = var_name+'_outlet'
    b.add_component(outlet_name, Port(initialize={'f': (b.find_component(var_name),
                                                        Port.Extensive, {'include_splitfrac': False})},
                                      doc='Power output port, using source convention (kW)'))
    return b


def power_load(b, **kwargs):
    """Power load block.

    Rule for defining a power load block. This rule add a variable and exposes an input port.

    :param b: block
    :param kwargs:  optional key-word arguments

        - `time` : for dynamic index
        - `var_name` : string for setting variable name (default : `p`)
        - `within` : Pyomo Set forvariable definition (default : Reals)
        - `doc` : setting documentation
        - `unit` : unit of the variable (default : kW)
        - `initialize` : set the initialize value of the variable (default : 0)

    :return: pyomo.Block
    """
    unit = kwargs.pop('unit', 'kW')
    var_name = kwargs.pop('var_name', 'p')
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.pop('doc', f'power load ({unit})')
    initialize = kwargs.pop('initialize', 0)
    within = kwargs.pop('within', Reals)


    b.add_component(var_name, Var(time, initialize=initialize, within=within, doc=doc, units=unit))
    inlet_name = var_name + '_inlet'
    b.add_component(inlet_name, Port(initialize={'f': (b.find_component(var_name),
                                                        Port.Extensive, {'include_splitfrac': False})},
                                      doc='Power output port, using load convention (kW)'))
    return b


# TODO unittest
def fixed_power_source(b, **kwargs):
    """
    Fixed Power Source Block

    Power Source block who's power output is fixed using Parameter.

    :param b: block
    :param kwargs:  optional key-word arguments

        - `time` : for dynamic index
        - `var_name` : string for setting variable name (default : `p`)
        - `within` : Pyomo Set for variable definition (default : Reals)
        - `doc` : setting documentation
        - `unit` : unit of the variable (default : kW)
        - `default` : set the default value of the variable (default : 0)

    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    p               new profile, indexed by time
    =============== ===================================================================

    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    p_outlet        output flow source using source convention
    =============== ===================================================================

    """
    unit = kwargs.pop('unit', 'kW')
    var_name = kwargs.pop('var_name', 'p')
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.pop('doc', f'fixed power source ({unit})')
    default = kwargs.pop('default', 0)
    within = kwargs.pop('within', Reals)

    b.add_component(var_name, Param(time, default=default, within=within, mutable=True, doc=doc, units=unit))
    outlet_name = var_name + '_outlet'
    b.add_component(outlet_name, Port(initialize={'f': (b.find_component(var_name),
                                                        Port.Extensive, {'include_splitfrac': False})},
                                      doc='Power output port, using source convention (kW)'))
    return b


def fixed_power_load(b, **kwargs):
    """
    Fixed Power Source Block

    Rue for defining a power Source block who's power output is fixed using Parameter.

    :param b: block
    :param kwargs:  optional key-word arguments

        - `time` : for dynamic index
        - `param_name` : string for setting parameter name (default : `p`)
        - `within` : Pyomo Set for parameter definition (default : Reals)
        - `doc` : setting documentation
        - `default` : set the default value of the parameter (default : 0)
        - `unit` : unit of the variable (default : kW)

    :return: pyomo.Block

    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    p               new profile, indexed by time
    =============== ===================================================================

    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    p_outlet        output flow source using source convention
    =============== ===================================================================


    """
    unit = kwargs.pop('unit', 'kW')
    within = kwargs.pop('within', Reals)
    param_name = kwargs.pop('param_name', 'p')
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.pop('doc', f'fixed power load ({unit})')
    default = kwargs.pop('default', 0)

    b.add_component(param_name, Param(time, default=default, within=within, mutable=True, doc=doc, units=unit))
    inlet_name = param_name + '_inlet'
    b.add_component(inlet_name, Port(initialize={'f': (b.find_component(param_name),
                                                       Port.Extensive, {'include_splitfrac': False})},
                                     doc='Power input port, using load convention (kW)'))
    return b


# TODO unittest
def scalable_power_source(b, curtailable=False, **kwargs):
    """ Scalable Power Source block

    May be used for sizing sources, such as PV panel, wind turbines, etc.

    :param b: block
    :param curtailable: source production can be partially curtailed
    :param kwargs:  optional key-word arguments

        - `default` : set the default value of the parameter (default : 0)
        - `doc` : setting documentation
        - `param_name` : string for setting parameter name (default : `p`)
        - `time` : for dynamic index
        - `unit` : unit of the variable (default : kW)
        - `within` : Pyomo Set for parameter definition (default : Reals)

    :return: pyomo.Block

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p_scaled        Scaled output flow (kW)
    scale_fact      scaling factor within Positve reals (1)
    =============== ===================================================================

    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    p               new profile, indexed by time
    fact_min        factor lower bound
    fact_max        factor upper bound
    =============== ===================================================================

    ==================== ===================================================================
    Constraints          Documentation
    ==================== ===================================================================
    _scale_fact_bounds   optional bound constraint for the scaling factor.
    _flow_scaling        Constraint equality for flow scaling
    _debug_flow_scaling  Debug constraint equality for flow scaling
    ==================== ===================================================================

    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    outlet          output power using source convention
    =============== ===================================================================
    """

    unit = kwargs.get('unit', u.kW)
    scale_fact = kwargs.get('scale_fact', 'scale_fact')
    var_name = kwargs.get('var_name', 'p')
    fact = kwargs.get('fact', None)
    fact_max = kwargs.get('fact_max', None)
    fact_min = kwargs.get('fact_min', 0)
    time = kwargs.get('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.get('doc', f'power source profile before scaling ({unit})')
    b = fixed_power_source(b, **kwargs)

    scaled_var_name = var_name + '_scaled'

    # case where s is fixed:
    if fact is not None:
        assert 0 <= fact, 'sacling factor `fact` should be positive'
        b.add_component(scale_fact, Param(default=fact, mutable=True, within=PositiveReals,
                                          doc='scaling factor within positive reals (default=1)'))
    # case where s is variable:
    else:
        if fact_min is not None:
            b.fact_min = Param(default=fact_min, mutable=True, doc='factor lower bound', within=Any)
        if fact_max is not None:
            b.fact_max = Param(default=fact_max, mutable=True, doc='factor upper bound', within=Any)

        scaled_doc = f'power source profile after scaling ({unit})'
        b.add_component(scaled_var_name, Var(time, doc=scaled_doc, initialize=0, units=unit))

        b.add_component(scale_fact, Var(initialize=1, within=PositiveReals,
                                        doc='scaling factor within positive reals (default=1)'))

        @b.Constraint(time, doc='optional bound constraint for the scaling factor.')
        def _scale_fact_bounds(m, t):
            if (fact_max is None) and fact_min == 0:
                return Constraint.Skip
            else:
                return m.fact_min, m.find_component(scale_fact), m.fact_max

    if curtailable:
        # creation of a new positive variable, that should be smaller than the production scale_fact*p
        b.p_curt = Var(time, within=NonNegativeReals, doc=f'curtailed flow ({unit})', units=unit)

        @b.Constraint(time, doc='Constraint equality for flow scaling')
        def _flow_scaling(m, t):
            return m.find_component(scaled_var_name)[t] + m.p_curt[t] == \
                   m.find_component(scale_fact) * m.find_component(var_name)[t]

        @b.Constraint(time, doc='Curtailment must be smaller than production')
        def _curt_up_bound(m, t):
            return 0, m.find_component(scaled_var_name)[t], None

    else:
        @b.Constraint(time, doc='Constraint equality for flow scaling')
        def _flow_scaling(m, t):
            return m.find_component(scaled_var_name)[t] == \
                   m.find_component(scale_fact) * m.find_component(var_name)[t]

        @b.Constraint(time, doc='Debug constraint equality for flow scaling')
        def _debug_flow_scaling(m, t):
            return -0.0001, m.find_component(scaled_var_name)[t] - \
                   m.find_component(scale_fact) * m.find_component(var_name)[t], 0.0001

    b.del_component(var_name+'_outlet')
    outlet_name = scaled_var_name+'_outlet'
    b.add_component(outlet_name,
                    Port(initialize={'f': (b.component(scaled_var_name), Port.Extensive, {'include_splitfrac': False})},
                         doc='output power using source convention'))
    return b


def pv_panel(b, curtailable=False, **kwargs):
    """
    Scalable PV panel module.

    Derives from a scalable power source.

    :param b: block
    :param curtailable: panel production can be partially curtailed
    :param kwargs:  optional key-word arguments

        - `default` : set the default value of the parameter (default : 0)
        - `doc` : setting documentation
        - `s_max` : maximal surface
        - `s_min` : minimal surface
        - `param_name` : string for setting parameter name (default : `p`)
        - `time` : for dynamic index
        - `unit` : unit of the variable (default : kW)
        - `within` : Pyomo Set for parameter definition (default : Reals)

    :return: pyomo.Block
    """

    unit = kwargs.pop('unit', 'kW')
    within = kwargs.pop('within', NonNegativeReals)
    fact_max = kwargs.pop('s_max', None)
    fact_min = kwargs.pop('s_min', 0)
    s_pv = kwargs.pop('s_pv', None)

    if fact_min is not None:
        assert fact_min >= 0, 'Minimal scaling factor s_min, should be positive.'
        if fact_max is not None:
            assert fact_min <= fact_max, 'Minimal scaling factor s_min, should be smaller than s_max.'

    b = scalable_power_source(b,
                              curtailable=curtailable,
                              flow_name='p',
                              scale_fact='s',
                              fact = s_pv,
                              fact_max = fact_max,
                              fact_min = fact_min,
                              within=within,
                              unit=unit,
                              **kwargs)

    return b


# TODO unittest
def scalable_power_load(b, curtailable=False, **kwargs):
    """
    Scalable power load

    Scalable power load, using a variable scaling factor. May be used for sizing loads.

    :param b: block
    :param curtailable: source production can be partially curtailed
    :param kwargs: optional key-word arguments

        - `default` : set the default value of the parameter (default : 0)
        - `doc` : setting documentation
        - `param_name` : string for setting parameter name (default : `p`)
        - `time` : for dynamic index
        - `unit` : unit of the variable (default : kW)
        - `within` : Pyomo Set for parameter definition (default : Reals)

    :return: pyomo.Block
    """

    within = kwargs.pop('within', Reals)
    scale_fact = kwargs.pop('scale_fact', 'scale_fact')
    var_name = kwargs.pop('var_name', 'p')
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.pop('doc', 'power load profile to be scaled (kW)')
    default = kwargs.pop('default', 0)

    b = power_load(b, var_name=var_name, time=time, doc=doc, default=default, within=within)

    scaled_var_name = var_name + '_scaled'
    b.fact_min = Param(default=None, mutable=True, doc='factor lower bound', within=Any)
    b.fact_max = Param(default=None, mutable=True, doc='factor upper bound', within=Any)

    b.add_component(scaled_var_name, Var(time, doc='Scaled input flow (kW)', initialize=0))

    b.add_component(scale_fact, Var(initialize=1, within=PositiveReals, doc='scaling factor within Positve '
                                                                            'reals (default=1)'))

    @b.Constraint(time, doc='optional bound constraint for the scaling factor.')
    def _scale_fact_bounds(m, t):
        if (m.fact_max.value is None) and (m.fact_min.value is None):
            return Constraint.Skip
        else:
            return m.fact_min, m.find_component(scale_fact), m.fact_max

    if curtailable:
        # creation of a new positive variable, that should be smaller than the production scale_fact*p
        b.p_curt = Var(time, within=NonNegativeReals, doc='curtailed flow (kW)')

        @b.Constraint(time, doc='Constraint equality for flow scaling')
        def _flow_scaling(m, t):
            return m.find_component(scaled_var_name)[t] + m.p_curt[t] == \
                   m.find_component(scale_fact) * m.find_component(var_name)[t]

        @b.Constraint(time, doc='Curtailment must be smaller than production')
        def _curt_up_bound(m, t):
            return 0, m.find_component(scaled_var_name)[t], None

    else:
        @b.Constraint(time, doc='Constraint equality for flow scaling')
        def _flow_scaling(m, t):
            return m.find_component(scaled_var_name)[t] == \
                   m.find_component(scale_fact) * m.find_component(var_name)[t]

        @b.Constraint(time, doc='Debug constraint equality for flow scaling')
        def _debug_flow_scaling(m, t):
            return -0.0001, m.find_component(scaled_var_name)[t] - \
                   m.find_component(scale_fact) * m.find_component(var_name)[t], 0.0001

    b.del_component(var_name + '_inlet')
    outlet_name = scaled_var_name + '_inlet'
    b.add_component(outlet_name, Port(initialize={'f': (b.component(scaled_var_name),
                                                        Port.Extensive,
                                                        {'include_splitfrac': False})},
                                      doc='output power using load convention'))
    return b


def curtailable_load(b, **kwargs):
        """
        Curtailable load

        Rule for defining a curtailable load, A binary variable is defined to represent ON and OFF phases.
        The input port represent the curtailed input power.

        :param b: Block
        :param kwargs:

            - `default` : set the default value of the parameter (default : 0)
            - `doc` : setting documentation
            - `param_name` : string for setting parameter name (default : `p`)
            - `time` : for dynamic index
            - `unit` : unit of the variable (default : kW)
            - `within` : Pyomo Set for parameter definition (default : Reals)

        :return: pyomo.Block

        **Model description**

        .. math::
            u(t) &\\in \\{0, 1\\} \\forall t \\in time \\\\
            curt\_p(t) &= u(t).p(t)

        """
        var_name = kwargs.pop('var_name', 'p')
        time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
        doc = kwargs.pop('doc', 'power load profile (kW)')
        doc_curt = kwargs.pop('doc', 'power load profile after curtailment (kW)')
        default = kwargs.pop('default', 0)
        within = kwargs.pop('within', Reals)

        b.u = Var(time, within=Binary, doc='binary, equals to 1 when the load is ON, 0 otherwise.')
        b.add_component(var_name, Param(time, default=default, within=within, doc=doc))

        curt_var_name = var_name + '_curt'
        b.add_component(curt_var_name, Var(time, default=default, within=within, doc=doc_curt))

        inlet_name = var_name + '_inlet'
        b.add_component(inlet_name, Port(initialize={'f': (b.find_component(curt_var_name),
                                                           Port.Extensive, {'include_splitfrac': False})},
                                         doc='Power output port, using load convention (kW)'))

        @b.Constraint(time, doc='curtailment constraint')
        def _curtailing(m, t):
            return m.find_component(curt_var_name)[t], m.u[t]*m.find_component(var_name)[t]

        return b


# TODO unittest
# todo : the following is depreciated. reformulate
# class ProgrammableLoad(PowerLoad):
#     """
#     Programmable Load with fixed input profile.
#
#     This load can be programmed to be on at a free moment within t_1 andd t_2, when turning 'on', the load is consuming
#     the profile power. Ex : Washing machine.
#     """
#
#     def __init__(self, *args, flow_name='p', **kwds):
#
#         from lms2 import fix_profile
#         from pyomo.core import Binary
#         from pyomo.environ import Param, Var, Set
#
#         super().__init__(*args, flow_name=flow_name, **kwds)
#
#         def _bound_u(m, t):
#             if m.window.bounds()[0] <= t <= m.window.bounds()[-1]:
#                 return 0, 1
#             else:
#                 return 0, 0
#
#         fix_profile(self, flow_name='pp', profile_name='profile_value', index_name='profile_index')
#
#         self.w1 = Param()
#         self.w2 = Param()
#         self.window = Set(doc='time window where load can be turned ON.')
#
#         self.u = Var(self.time, bounds=_bound_u, within=Binary,
#                      doc='binary, equals to 1 when the load is turned ON, 0 otherwise.')
#
#         @self.Constraint(doc='the load is turned on only once')
#         def _turned_on(m):
#             return sum([m.u[t] for t in m.time]) == 1
#
#         @self.Constraint(self.time, doc='the load is contraint to be off outside the time range')
#         def _bound_p(m, t):
#             if m.window.bounds()[0] <= t <= m.window.bounds()[-1]:
#                 return Constraint.Skip
#             else:
#                 return 0, m.p[t], 0
#
#     def compile(self):
#         def _delay(m, t):
#             if t >= max(m.profile_index):
#                 return m.p[t] == sum([m.u[t - i] * m.profile_value[i] for i in m.profile_index])
#             else:
#                 return Constraint.Skip
#
#         self._delay = Constraint(self.time, rule=_delay, doc='the load follow the profile')


def debug_source(b, **kwargs):
    """
    Debug Power block

    Consist of an unbounded power source associated a significant positive cost weight.

    **Model description**

    =============== =============== =====================================================================
    Name            Type            Documentation
    =============== =============== =====================================================================
    abs_p           Var             Absolute value of variable p
    p               Var             Power output flow (kW)
    outlet          Port            Power output port, using source convention (kW)
    p_cost          Param           cost associated to the absolute value of p (euros/kWh)
    inst_cost       Expression      instantaneous bilinear cost (euros/s), associated with variable p
    time            ContinuousSet   Time continuous set (s)
    _bound1         Constraint      absolute value constraint 1
    _bound2         Constraint      absolute value constraint 2
    =============== =============== =====================================================================

    """
    from lms2.economic.cost import absolute_cost

    b = power_source(b, **kwargs)
    var_name = kwargs.pop('var_name', 'p')
    cost = kwargs.pop('cost', 1e4)

    b.inst_cost = absolute_cost(b, var_name=var_name, cost=cost)
    return b
