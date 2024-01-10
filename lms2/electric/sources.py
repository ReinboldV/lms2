"""
Electrical sources and loads
"""
import pandas as pd
from pyomo.core import Var, Param
from pyomo.environ import *
from pyomo.core.base.set import Reals, PositiveReals, NonNegativeReals, Any, Binary
from pyomo.network import Port
from pyomo.dae import ContinuousSet
from pyomo.environ import units as u


__all__ = ['power_source', 'fixed_power_source', 'scalable_power_source',
           'power_load',   'fixed_power_load',   'scalable_power_load',
           'debug_source', 'pv_panel', 'curtailable_load']


# TODO unittest
def power_source(b, **kwargs):
    """ Power Source block

    Rule for defining a power source block. This rule add a variable and creates an output port.
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
    p0              new profile, indexed by time
    =============== ===================================================================

    =============== ===================================================================
    Ports           Documentation
    =============== ===================================================================
    p_outlet        output flow source using source convention
    =============== ===================================================================

    """
    unit = kwargs.pop('unit', 'kW')
    param_name = kwargs.pop('param_name', 'p0')
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.pop('doc', f'fixed power source ({unit})')
    default = kwargs.pop('default', 0)
    within = kwargs.pop('within', Reals)

    b.add_component(param_name, Param(time, default=default, within=within, mutable=True, doc=doc, units=unit))
    outlet_name = param_name + '_outlet'
    b.add_component(outlet_name, Port(initialize={'f': (b.find_component(param_name),
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

        - `doc` : setting documentation
        - `param_name` : string for setting parameter name (default : `p`)
        - `time` : for dynamic index
        - `unit` : unit of the variable (default : kW)
        - `within` : Pyomo Set for parameter definition (default : Reals)
        - `scale_fact` : Set the scaling factor name (default : scale_fact)
        - `var_name` : Set the name of the power variable (default : p_pv)
        - `fact` : Set the scaling factor value (default : None)
        - `fact_max` : Set the upper bound of fact (only if fact=None)
        - `fact_min` : Set the lower bound of fact (only if fact=None)


    :return: pyomo.Block

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p_scaled        Scaled output flow (kW)
    scale_fact      scaling factor within Positive reals (1)
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
    fact = kwargs.get('fact', None)
    fact_max = kwargs.get('fact_max', None)
    fact_min = kwargs.get('fact_min', 0)
    time = kwargs.get('time', ContinuousSet(bounds=(0, 1)))
    doc = kwargs.get('doc', f'power source profile before scaling ({unit})')

    param_name = kwargs.pop('param_name', 'p0')
    var_name = kwargs.pop('var_name', 'p')

    b = fixed_power_source(b, **dict(kwargs, param_name=param_name))

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
        b.add_component(var_name, Var(time, doc=scaled_doc, initialize=0, units=unit))

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
            return m.find_component(var_name)[t] + m.p_curt[t] == \
                   m.find_component(scale_fact) * m.find_component(param_name)[t]

        @b.Constraint(time, doc='Curtailment must be smaller than production')
        def _curt_up_bound(m, t):
            return 0, m.find_component(var_name)[t], None

    else:
        @b.Constraint(time, doc='Constraint equality for flow scaling')
        def _flow_scaling(m, t):
            return m.find_component(var_name)[t] == \
                   m.find_component(scale_fact) * m.find_component(param_name)[t]

        @b.Constraint(time, doc='Debug constraint equality for flow scaling')
        def _debug_flow_scaling(m, t):
            return -0.0001, m.find_component(var_name)[t] - \
                   m.find_component(scale_fact) * m.find_component(param_name)[t], 0.0001

    b.del_component(param_name+'_outlet')
    outlet_name = var_name+'_outlet'
    b.add_component(outlet_name,
                    Port(initialize={'f': (b.component(var_name), Port.Extensive, {'include_splitfrac': False})},
                         doc='output power using source convention'))
    return b


def pv_panel(b, curtailable=False, **kwargs):
    """
    Scalable PV panel module.

    Derives from a scalable power source. One can fix the scaling factor `s` using key-word argument `s_pv`. Otherwise,
    one should set lower and upper bounds `s_min` and `s_max` in the options.
    The source can also be curtailed, setting the key-word parameter `curtailable`=True. In this case, a positive
    portion of the generated power, named `p_curt`, can be curtailed.

    .. math::
        p_{pv}(t) + p_{curt}(t) = s_{pv}*p_0(t)

    :param b: block
    :param curtailable: panel production can be partially curtailed
    :param kwargs:  optional key-word arguments

    Additionnal key-word arguments :
        - `default` : set the default value of the parameter (default : 0)
        - `doc` : setting documentation
        - `s_max` : maximal surface
        - `s_min` : minimal surface
        - `param_name` : string for setting parameter name (default : `p`)
        - `time` : for dynamic index
        - `unit` : unit of the variable (default : kW)
        - `within` : Pyomo Set for parameter definition (default : Reals)

    .. table::
        :width: 100%

        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        p_pv            power source profile after scaling (kW)
        s_pv            scaling factor within positive reals (default=1)
        p_curt          curtailed flow (kW)
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Parameters      Documentation
        =============== ===================================================================
        p0              fixed power source (kW)
        fact_min        factor lower bound
        fact_max        factor upper bound
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        _scale_fact_bounds optional bound constraint for the scaling factor.
        _flow_scaling   Constraint equality for flow scaling
        _curt_up_bound  Curtailment must be smaller than production
        =============== ===================================================================

    .. table::
        :width: 100%

        =============== ===================================================================
        Ports           Documentation
        =============== ===================================================================
        p_scaled_outlet output power using source convention
        =============== ===================================================================


    Example :

    >>> from pyomo.environ import *
    >>> from lms2.electric.sources import pv_panel, fixed_power_load, power_source
    >>> m = ConcreteModel()
    >>> m.time = ContinuousSet(initialize=[0, 10])
    >>> option_pv = {'time': m.time, 's_max': 10, 's_min': 0.1}
    >>> m.pv = Block(rule=lambda x: pv_panel(x, **option_pv))
    >>> m.pv.p0.pprint()
    p0 : fixed power source (kW)
        Size=2, Index=time, Domain=NonNegativeReals, Default=0, Mutable=True
        Key : Value
          0 :     0
         10 :     0

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
                              var_name='p',
                              param_name='p0',
                              scale_fact='s_pv',
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
    time = kwargs.pop('time')

    b.inst_cost = absolute_cost(b, time, var_name=var_name, cost=cost)
    return b


def curtailable_load_2(b, **kwargs):
    """
    Modèle de charge écrêtable à partir d'un certain seuil PM.

    formulation 1, continue si dObj/dp > 0
    formulation 2, continue si dObj/dp < 0
    formulation 3, binaire sinon

    .. math::
        0 &\\leq p_0(t) \\left(1-u(t) \\right) \\leq p_M  \\\\
        0 &\\leq p_M.u(t) \\leq p_0(t)  \\\\
        p(t) &= pM.u(t) + p_0(t).(1-u(t))


    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p               power of the boat after curtailment
    u               1: load is curtailed, 0: load is not curtailed
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    p0              power load before curtailment (mutable)
    pM              power limit, power load p0 is curtailed if greater than pM
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    _binary1        impose u=1 if po > pM
    _binary2        impose u=0 if po < pM
    _curtailment    impose p=pM if u=1 et p=p0 if u=0
    =============== ===================================================================

    Example:

        1. Initialisation
            >>> from pyomo.environ import *
            >>> from pyomo.dae import ContinuousSet
            >>> from lms2.electric.sources import curtailable_load_2
            >>> from lms2.core.horizon import SimpleHorizon
            >>> horizon = SimpleHorizon(tstart='2020-01-01 00:00:00', tend='2020-01-08 00:00:00', time_step='10 min')

        2. Création du problème d'optimisation:
            >>> m = ConcreteModel()
            >>> m.time = ContinuousSet(initialize=[0, horizon.horizon.total_seconds()])
            >>> option_charge = {'time': m.time, 'pM': 200}
            >>> m.charge = Block(rule=lambda x: curtailable_load_2(x, **option_charge))

    """
    from numpy import Inf

    unit = kwargs.pop('unit', 'kW')
    pM = kwargs.pop('pM', Inf)
    time = kwargs.pop('time')

    b.p = Var(time, initialize=0, within=NonNegativeReals, doc='power of the boat after curtailment', units=unit)
    b.u = Var(time, initialize=0, within=Binary, doc='1: load is curtailed, 0: load is not curtailed', units='1')
    b.p0 = Param(time, default=0, within=NonNegativeReals, mutable=True,
                 units=unit, doc='power load before curtailment')
    b.pM = Param(default=pM, mutable=True, units=unit, doc='Curtailment level')

    @b.Constraint(time, doc='impose u=1 if po > pM')
    def _binary1(b, t):
        return 0, b.p0[t]*(1-b.u[t]), b.pM

    @b.Constraint(time, doc='impose u=0 if po < pM')
    def _binary2(b, t):
        return 0, b.pM*b.u[t], b.p0[t]

    @b.Constraint(time, doc='impose p=pM if u=1 et p=p0 if u=0')
    def _curtailment(b, t):
        return b.p[t], b.pM*b.u[t] + b.p0[t]*(1-b.u[t])


def square(b, **kwargs):

    pM = kwargs.pop('pM', 1)
    time = kwargs.pop('time')
    period = kwargs.pop('period', 4)
    dt = time.at(2) - time.at(1)

    # rule for initializing parameter value
    def initial(b, t):
        if (t//dt)%period < period/2:
            return -pM
        else:
            return pM

    b.p = Param(time, default=initial)


def def_pin_pout(m):
    # This could be better implemented.
    # In particular, it should not use m.p directly but m.find_component(name_var)

    """
    Defines power flow variables 'in' and 'out'

    :param m:
    :return:
    """

    assert isinstance(m, Block), f"argument 'm', must be an instance of Block, but is actually {type(m)}."
    assert hasattr(m, 'p'), f"model m does not have attribute named 'p'. This is needed. "

    m.pmax = Param(initialize=1e3, mutable=True, doc='maximal power out (kW)', within=Reals)
    m.pmin = Param(initialize=1e3, mutable=True, doc='maximal power in (kW)', within=Reals)

    m.pout = Var(m.time, doc='power to the main grid', within=NonNegativeReals, initialize=0)
    m.pin = Var(m.time, doc='power from the main grid', within=NonNegativeReals, initialize=0)
    m.u = Var(m.time, doc='binary variable', within=Binary, initialize=0)

    def _power_balance(b, t):
        return b.p[t] - b.pout[t] + b.pin[t] == 0

    def _pmax(b, t):
        if b.pmax.value is None:
            return Constraint.Skip
        return b.pout[t] - b.u[t] * b.pmax <= 0

    def _pmin(b, t):
        if b.pmin.value is None:
            return Constraint.Skip
        return b.pin[t] + b.u[t] * b.pmin <= b.pmin

    m._pmin = Constraint(m.time, rule=_pmin, doc='low bound')
    m._pmax = Constraint(m.time, rule=_pmax, doc='up bound')
    m._p_balance = Constraint(m.time, rule=_power_balance, doc='power balance')


