from pyomo.environ import *
from pyomo.environ import units as u
from pyomo.dae import Integral, ContinuousSet

__all__ = ['dwelling_v2']

from lms2.building.structure import thermal_structure_block
from lms2.building.systems import hot_water_tank, heat_pump
from lms2.social.occupancy import occupancy
from lms2.environment.environment import solar_inputs, environment


def dwelling_v1(b, **kwargs):
    graph = kwargs.pop('graph', None)
    horizon = kwargs.pop('horizon', 7200)

    b.time   = ContinuousSet(bounds=(0, horizon), doc='set of time')
    b.env    = Block(rule =environment, options={'time': b.time})
    b.sol    = Block(rule =solar_inputs, options={'time': b.time})
    b.hwt    = Block(rule =hot_water_tank, options={'time': b.time})
    b.occ    = Block(rule =occupancy, options={'time': b.time})
    b.hp     = Block(rule =heat_pump, options={'time': b.time, 'occ': b.occ})
    b.struct = Block(rule=thermal_structure_block,
                     options={'time': b.time, 'graph': graph, 'env': b.env, 'occ': b.occ})

    b.p_elec_max = Var(initialize=0, doc='Maximal electrical power ', units=u.watt, bounds=(0, 1e6))

    # the following hw_balance, thermal balance and electrical balance could be declared in respective blocks
    # (hp, struct, elec), but since this blocks are exchanging parameters and variable,
    # it is simpler to declare these constraints on dwelling level.

    @b.Constraint(b.time, doc='HW power balance')
    def hw_balance(b, t):
        # TODO : the factor 900 comes from the hot water flow unit, which is liter per 15 min
        return b.hwt.V * b.hwt.dT_HW[t], b.hp.Q_heat_HW[t] - (b.hwt.T_HW_d - b.hwt.T_CW) * b.occ.Flow_HW[t] / 900

    @b.Constraint(b.time, b.struct.id_nodes, doc='thermal power balance')
    def thermal_balance(b, t, n):
        if b.struct.C[n]() is None and b.struct.graph.nodes(data='T_fix')[n] is not None:
            return Constraint.Skip
        else:
            q_fix_dict = b.struct.graph.nodes(data='Q_fix')[n]
            q_control_dict = b.struct.graph.nodes(data='Q_control')[n]
            exp = 0

            # Discharge of thermal capacity (First law of thermodynamics)
            if b.struct.C[n]() is not None:
                exp -= b.struct.C[n] * b.struct.dT[n, t]

            # summing all the heat flow inputs (Q_fix in the graph description)
            if (q_fix_dict is not None) & (isinstance(q_fix_dict, dict)):
                exp += sum([round(fact, 6) * b.occ.component(q)[t] for q, fact in q_fix_dict.items()])

            # summing all the heat flow control variable (Q_control in the graph description)
            if (q_control_dict is not None) & (isinstance(q_control_dict, dict)):
                exp += sum([round(fact, 6) * b.hp.component(q)[t] for q, fact in q_control_dict.items()])

            # summing all the heat transfer from the neighbours (arithmetic sum)
            exp += sum([b.struct.q[qe[0], qe[1], t] for qe in b.struct.graph.in_edges(n)])
            exp -= sum([b.struct.q[qe[0], qe[1], t] for qe in b.struct.graph.out_edges(n)])
            return exp, 0

    @b.Expression(b.time, doc='total electric power')
    def p_elec(b, t):
        # TODO : handling sum of all electric power by hand, one might find a way to some automatically
        return (b.hp.Q_heat_N[t] + b.hp.Q_heat_D[t] + b.hp.Q_heat_HW[t])/b.hp.COP
        # return b.hp.p_elec_N[t] + b.hp.p_elec_D[t] + b.hp.p_elec_HW[t]

    @b.Constraint(b.time, doc='maximal electric power')
    def _p_elec_max(b, t):
        return 0, b.p_elec_max - b.p_elec[t], None

    @b.Expression(b.time, doc='total comfort of night and day zone (linear expression)')
    def comfort(b, t):
        return b.occ.u_D[t] * b.struct.comfort_D[t] + b.occ.u_N[t] * b.struct.comfort_N[t]

    @b.Constraint(b.time, doc='absolute value constraint, upper bound')
    def thermal_comfort(b, t):
        return b.comfort[t] <= b.struct.delta_T

    b.kpi_comfort = Integral(b.time, wrt=b.time, rule=comfort, doc='Integral of the comfort over the time horizon')


def dwelling_v2(b, **kwargs):
    """
    =============== ===================================================================
    Blocks          Documentation
    =============== ===================================================================
    sol             None
    hwt             None
    occ             None
    hp              None
    struct          None
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    p_elec_max      Maximal electrical power
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    hw_balance      HW power balance
    thermal_balance thermal power balance
    _p_elec_max     maximal electric power
    thermal_comfort absolute value constraint, upper bound
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    p_elec          total electric power
    comfort         total comfort of night and day zone (linear expression)
    =============== ===================================================================

    :param b: Dwelling Block
    :param kwargs:
    :return:
    """

    graph = kwargs.pop('graph', None)
    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))
    dict_env = {'time': time}
    env_temp = Block()
    env = kwargs.pop('env', environment(env_temp, **dict_env))

    # solar inputs block:
    dict_sol = {'time': time}
    b.sol = Block()
    solar_inputs(b.sol, **dict_sol)

    # hot water tank block:
    dict_hwt = {'time': time}
    b.hwt = Block()
    hot_water_tank(b.hwt, **dict_hwt)

    # occupancy block:
    dict_occ = {'time': time}
    b.occ = Block()
    occupancy(b.occ, **dict_occ)

    # heat pump block:
    dict_hp = {'time': time, 'occ': b.occ}
    b.hp = Block()
    heat_pump(b.hp, **dict_hp)

    # thermal structure block:
    dict_struct = {'time': time, 'graph': graph, 'env': env, 'occ': b.occ}
    b.struct = Block()
    thermal_structure_block(b.struct, **dict_struct)

    b.p_elec_max = Var(initialize=0, doc='Maximal electrical power ', units=u.watt, bounds=(0, 1e6))

    @b.Constraint(time, doc='HW power balance')
    def hw_balance(b, t):
        # ..note :: the factor 900 comes from the hot water flow unit, which is liter per 15 min
        return b.hwt.V * b.hwt.dT_HW[t], b.hp.Q_heat_HW[t] - (b.hwt.T_HW_d - b.hwt.T_CW) * b.occ.Flow_HW[t] / 900

    @b.Constraint(time, b.struct.id_nodes, doc='thermal power balance')
    def thermal_balance(b, t, n):
        if b.struct.C[n]() is None and b.struct.graph.nodes(data='T_fix')[n] is not None:
            return Constraint.Skip
        else:
            q_fix_dict = b.struct.graph.nodes(data='Q_fix')[n]
            q_control_dict = b.struct.graph.nodes(data='Q_control')[n]
            exp = 0

            # Discharge of thermal capacity (First law of thermodynamics)
            if b.struct.C[n]() is not None:
                exp -= b.struct.C[n] * b.struct.dT[n, t]

            # summing all the heat flow inputs (Q_fix in the graph description)
            if (q_fix_dict is not None) & (isinstance(q_fix_dict, dict)):
                exp += sum([round(fact, 6) * b.occ.component(q)[t] for q, fact in q_fix_dict.items()])

            # summing all the heat flow control variable (Q_control in the graph description)
            if (q_control_dict is not None) & (isinstance(q_control_dict, dict)):
                exp += sum([round(fact, 6) * b.hp.component(q)[t] for q, fact in q_control_dict.items()])

            # summing all the heat transfer from the neighbours (arithmetic sum)
            exp += sum([b.struct.q[qe[0], qe[1], t] for qe in b.struct.graph.in_edges(n)])
            exp -= sum([b.struct.q[qe[0], qe[1], t] for qe in b.struct.graph.out_edges(n)])
            return exp, 0

    @b.Expression(time, doc='total electric power')
    def p_elec(b, t):
        # TODO : handling sum of all electric power by hand, one might find a way to do it automatically
        return (b.hp.Q_heat_N[t] + b.hp.Q_heat_D[t] + b.hp.Q_heat_HW[t]) / b.hp.COP
        # return b.hp.p_elec_N[t] + b.hp.p_elec_D[t] + b.hp.p_elec_HW[t]

    @b.Constraint(time, doc='maximal electric power')
    def _p_elec_max(b, t):
        return 0, b.p_elec_max - b.p_elec[t], None

    @b.Expression(time, doc='total comfort of night and day zone (linear expression)')
    def comfort(b, t):
        return b.occ.u_D[t] * b.struct.comfort_D[t] + b.occ.u_N[t] * b.struct.comfort_N[t]

    @b.Constraint(time, doc='absolute value constraint, upper bound')
    def thermal_comfort(b, t):
        return b.comfort[t] <= b.struct.delta_T

    # integral are not working well for blocks and sub-blocks, defining confort on the upper level (feeder)
    #b.kpi_comfort = Integral(time, wrt=time, rule=comfort, doc='Integral of the comfort over the time horizon')

    return b