"""
Economic Units and methods

This module contains Economic units and methods to define parameter, variables and objectives to an exiting block
"""
import pandas as pd
from pyomo.core import NonNegativeReals, PositiveReals
from pyomo.environ import Param, Var, Expression, Constraint

__all__ = ['linear_cost', 'bilinear_cost', 'linear_dyn_cost',
           'bilinear_dynamic_cost', 'absolute_cost']


def linear_cost(m, time, var_name='p'):
    """
    Method for adding a linear constant cost associated to variable 'p', to a block
    Final instantaneous cost expression is called "inst_cost"

    :param m: Block
    :param str var_name: Names of the expensive variable
    :return: A pyomo expression of the instantaneous cost

    - Partial model:

    .. math::
        m.instantcost(t) = m.var(t) \\times m.cost, \ \\forall t \\in m.time

    - Example of simple model using linear_cost():

    .. code-block:: python
        :caption: Creation of the Abstract model "m" (i.e. no data, no discretization)

        from lms2 import AbsLModel, linear_cost
        from pyomo.environ import Var, Objective
        from pyomo.dae import ContinuousSet, Integral

        m = AbsLModel(name='example')
        m.time = ContinuousSet()
        m.v = Var(m.time, doc='an expensive variable, associated to cost "c_v"')
        m.inst_cost  = linear_cost(m, var_name='v')
        m.integral_cost = Integral(m.time, wrt=m.time, rule=lambda m, i: m.inst_cost[i])
        m.obj = Objective(expr=m.integral_cost)

    .. code-block:: python
        :caption: Creation of a data set for the example, and instantiation of the problem

        data = {None: {'time': {None: [0, 10]}, 'cost': {None: 3.6}}}  # cost = 3.6 euro/kWh = 1e-3 euros/s
        inst = m.create_instance(data)

    .. code-block:: python
        :caption: Discretization of the continuous time (here every (10-0)/5 = 2 seconds)

        from pyomo.environ import TransformationFactory
        TransformationFactory('dae.finite_difference').apply(inst, nfe=5)
        inst.obj.expr.expr.to_string()


    """

    m.cost = Param(initialize=0, mutable=True, doc=f'simple linear cost, associated with variable {var_name}, (euros/kWh)')

    def _instant_cost(m, t):
        return m.find_component(var_name)[t] * m.cost / 3600

    return Expression(time, rule=_instant_cost,
                      doc=f'instantaneous linear cost (euros/s), associated with variable {var_name}')


def linear_dyn_cost(m, var_name='p'):
    """
    Method for adding a linear dynamic cost associated to variable 'p', to a block
    Final instantaneous cost expression is called "inst_cost"

    .. math::
        m.instantcost(t) = m.var(t) \\times m.cost(t), \ \\forall t \\in m.time

    :param m: Block
    :param str var_name: Names of the expensive variable
    :return: pyomo Expression
    """
    from lms2.base.block import fix_profile

    fix_profile(m, flow_name='cost', index_name='cost_index', profile_name='cost_value')

    def _instant_cost(m, t):
        return m.find_component(var_name)[t] * m.cost[t] / 3600

    return Expression(m.time, rule=_instant_cost,
                      doc=f'instantaneous linear cost (euros/s), associated with variable {var_name}')


def absolute_cost(m, time, var_name='p', cost=1):
    """
    Method for adding absolute cost related to an existing variable.

    Define a bilinear cost of coefficient -1 and +1 associated with variable 'p'. Define a new variable `abs_p`,
    a cost parameter, and two inequality constraints. The returned instantaneous cost expression is called "inst_cost"


    :param m: Block
    :param var_name: Name of the expensive variable, should already exist in he model
    :param cost: cost initialization value (default = 1 euro/kWh)
    :return: pyomo Expression (euro/s)
    """

    abs_var_name = f'abs_{var_name}'
    bound1 = f'_bound_1_{var_name}'
    bound2 = f'_bound_2_{var_name}'
    m.add_component(abs_var_name, Var(time, within=NonNegativeReals, initialize=0,
                                      doc=f'Absolute value of variable {var_name}'))
    m.add_component(f'{var_name}_cost', Param(default=cost, mutable=True, within=NonNegativeReals,
                                              doc=f'cost associated to the absolute value of {var_name} (euros/kWh)'))

    def _bound1(m, t):
        return m.find_component(abs_var_name)[t] >= -m.find_component(f'{var_name}_cost')*m.find_component(var_name)[t]
    m.add_component(bound1, Constraint(time, rule = _bound1,
                                       doc=f'absolute value constraint 1 on variable {abs_var_name}'))

    def _bound2(m, t):
        return m.find_component(abs_var_name)[t] >= m.find_component(f'{var_name}_cost')*m.find_component(var_name)[t]
    m.add_component(bound2, Constraint(time, rule = _bound2,
                                       doc=f'absolute value constraint 2 on variable {abs_var_name}'))

    def _instant_cost(m, t):
        return m.find_component(abs_var_name)[t] / 3600

    return Expression(time, rule=_instant_cost,
                      doc=f'instantaneous bilinear cost (euros/s), associated with variable {var_name}')


def bilinear_cost(bl, time, var_in='p_in', var_out='p_out'):
    """
    Method for adding bilinear cost to a block associated to variables 'var_in', 'var_out'.

    Names of costs are 'cost_in' 'cost_out' and are not tunable for the moment.
    Final instantaneous cost expression is called "inst_cost"

    :param bl: Block
    :param str var_in: Name of the input variable
    :param str var_out: Name of the input variable
    :return: pyomo Expression
    """
    bl.cost_in  = Param(default=0, mutable=True, doc=f'buying cost of variable {var_in} (euro/kWh)')
    bl.cost_out = Param(default=0, mutable=True, doc=f'selling cost of variable {var_out} (euro/kWh)')

    def _instant_cost(m, t):
        return (m.find_component(var_out)[t] * m.cost_out - m.find_component(var_in)[t] * m.cost_in)/3600

    return Expression(time, rule=_instant_cost,
                      doc=f'instantaneous bilinear cost (euros/s), associated with variable {var_in} and {var_out}')


def bilinear_dynamic_cost(bl, time, var_in='p_in', var_out='p_out'):
    """
    Method for adding bilinear dynamic cost to a block associated to variables 'var_in', 'var_out'.

    Names of costs are 'cost_in' 'cost_out' and are not tunable for the moment.
    Final instantaneous cost expression is called "inst_cost"

    .. warning :: should only be used for convex cost ! i.e.  cost_out > -cost_in

    :param bl: Block
    :param str var_in: Name of the input variable
    :param str var_out: Name of the input variable
    :return: Expression
    """

    from lms2.base.block import fix_profile

    fix_profile(bl, flow_name='cost_in',  index_name='cost_in_index',  profile_name='cost_in_value',
                doc_index=f'index for the dynamic cost related to variable {var_in}',
                doc_value=f'values for dynamic cost related to variable {var_in}')
    fix_profile(bl, flow_name='cost_out', index_name='cost_out_index', profile_name='cost_out_value',
                doc_index=f'index for the dynamic cost related to variable {var_out}',
                doc_value=f'values for dynamic cost related to variable {var_out}')

    def _instant_cost(m, t):
        return (m.find_component(var_out)[t] * m.cost_out[t] - m.find_component(var_in)[t] * m.cost_in[t])/3600

    return Expression(time, rule=_instant_cost,
                      doc=f'instantaneous bilinear and dynamic cost, associated with variable {var_in} and {var_out}')


# TODO : create maintenance cost, with frequency parameter, and computation for long and short term horizon
def maintenance_cost(m):
    pass


# TODO : create recycling cost, computation for long and short term horizon
def recycling_cost(m):
    pass


# TODO : create buying cost, computation for long and short term horizon
def lifecycle_cost(m, time, lifetime = '10 years'):
    """
    Method for defining an expression of the buying cost.

    This can be expressed for the time set defined by m.time. this will introduce a parameter called lifetime and return
    the following expression $$ cost = \Delta T \times lifecycle_cost / lifetime $$

    :param m:
    :return:
    """
    m.lifecycle_cost = Param(default=0, within=NonNegativeReals, doc='buying cost associated with the device.')
    lifetime = pd.Timedelta(lifetime).total_seconds()
    m.lifetime    = Param(default=lifetime, doc='lifetime of the device.')
    use_time = time.last() - time.first()

    return use_time * m.lifecycle_cost / m.lifetime


# TODO : create replacement cost, computation for long and short term horizon
def replacement_cost(m):
    pass


# todo : add opex, capex, LCA...