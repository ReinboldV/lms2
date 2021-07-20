from pyomo.environ import *
from pyomo.environ import units as u
from pyomo.core import Reals, PositiveReals, NonNegativeReals, Any, Binary
from pyomo.dae import DerivativeVar, Integral, ContinuousSet

__all__ = ['solar_inputs', 'thermal_structure_block', 'heat_pump', 'occupancy', 'hot_water_tank', 'dwelling_v2']


def solar_inputs(sol, **kwargs):
    """
    Not implemented yet !
    Block responsible for the calculation of heat gain, with respect to the environment (lat, long, time),
    and building geometry windows surface etc.
    """

    time = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))
    pass


def thermal_structure_block(struct, **kwargs):
    """
    Thermal structure block.

    The thermal structure is defined by a set of nodes and edges. Temperature `T`, thermal capacity `C`, heat gain,
    heat control might be defined at each node. Heat flow `q` and thermal resistivity `U` is defied at each edges.
    Heat flow constraint and boundaries conditions are declared in the block, whereas Kirchhoff law (power balance)
    at the node level is declared in the dwelling.

    =============== ===================================================================
    Sets            Documentation
    =============== ===================================================================
    id_nodes        set of thermal nodes
    id_edges        set of thermal edges
    q_index         None
    T_index         None
    heat_flow_index None
    boundary_conditions_index None
    =============== ===================================================================
    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    q               heat flow (W)
    T               nodes temp.
    comfort_N       comfort in the night zone
    comfort_D       comfort in the day zone
    dT              node temperature derivative
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    U               thermal resistance of edges
    C               Thermal capacities of nodes
    alpha           weight coefficient between negative and positive deviation
    delta_T         acceptable temperature deviation for normal comfort
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    heat_flow       Edge heat transfer
    t_init          Initial condition on node temperature
    boundary_conditions Dirichlet condition for thermal nodes
    _bound_N1       absolute value constraint, lower bound N
    _bound_N2       absolute value constraint, upper bound N
    _bound_D1       absolute value constraint, lower bound D
    _bound_D2       absolute value constraint, upper bound D
    dT_disc_eq      None
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    Top_N           Operational temperature Night zone
    Top_D           Operational temperature Day zone
    =============== ===================================================================

    :param struct: thermal structure block
    :param kwargs: options needed for the block construction
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))
    occ   = kwargs.pop('occ', None)
    graph = kwargs.pop('graph', None)
    env   = kwargs.pop('env', None)

    struct.graph = graph

    struct.id_nodes = Set(initialize=list(graph.nodes), doc="set of thermal nodes")
    struct.id_edges = Set(initialize=list(graph.edges), doc="set of thermal edges")
    struct.id_edges.construct()
    struct.id_nodes.construct()

    # Variables
    struct.q     = Var(struct.id_edges, time, doc="heat flow (W)", units=u.watt)
    struct.T     = Var(struct.id_nodes, time, initialize=0, units=u.deg, bounds=(-20, 55), doc="nodes temp.")

    struct.comfort_N = Var(time, initialize=0, doc='comfort in the night zone', domain=NonNegativeReals)
    struct.comfort_D = Var(time, initialize=0, doc='comfort in the day zone', domain=NonNegativeReals)

    struct.dT    = DerivativeVar(struct.T, wrt=time, doc="node temperature derivative", units=u.deg / u.s)

    # Parameters of the thermal structure (names are based on the rc model description)
    struct.U = Param(struct.id_edges,
                     initialize={(i, j): d for i, j, d in graph.edges(data='U')},
                     doc='thermal resistance of edges',
                     units=u.meter * u.meter,
                     default=0,
                     domain=Reals)
    struct.C = Param(struct.id_nodes,
                     initialize={n: d for n, d in graph.nodes(data='C')},
                     doc='Thermal capacities of nodes',
                     units=u.meter * u.meter,
                     default=0,
                     within=Any)

    struct.alpha = Param(mutable=True, default=0.5, doc='weight coefficient between negative and positive deviation')
    struct.delta_T = Param(default=2.5, doc='acceptable temperature deviation for normal comfort')

    @struct.Constraint(time, struct.id_edges, doc='Edge heat transfer')
    def heat_flow(b, t, e1, e2):
        return b.U[(e1, e2)] * (b.T[e1, t] - b.T[e2, t]), b.q[(e1, e2), t]

    @struct.Constraint(struct.id_nodes, doc='Initial condition on node temperature')
    def t_init(b, n):
        t_0 = b.graph.nodes(data='T_init')[n]
        if t_0 is not None:
            return b.T[n, 0] == t_0
        else:
            return Constraint.Skip

    @struct.Constraint(time, struct.id_nodes, doc='Dirichlet condition for thermal nodes')
    def boundary_conditions(b, t, n):
        if b.graph.nodes(data='T_fix')[n] is not None:
            return b.T[n, t] == env.component(b.graph.nodes(data='T_fix')[n])[t]
        else:
            return Constraint.Skip

    @struct.Expression(time, doc='Operational temperature Night zone')
    def Top_N(b, t):
        return ((b.T['TwiN', t] + b.T['TwN', t] + b.T['TfiN', t]) / 3 + b.T['TiN', t]) / 2

    @struct.Expression(time, doc='Operational temperature Day zone')
    def Top_D(b, t):
        return ((b.T['TwiD', t] + b.T['TwD', t] + b.T['TfiD', t] + b.T['TflD', t]) / 4 + b.T['TiD', t]) / 2

    @struct.Constraint(time, doc='absolute value constraint, lower bound N')
    def _bound_N1(b, t):
        return b.comfort_N[t] >= -b.alpha * (b.Top_N[t] - occ.Tset_n[t])

    @struct.Constraint(time, doc='absolute value constraint, upper bound N')
    def _bound_N2(b, t):
        return b.comfort_N[t] >= (1 - b.alpha) * (b.Top_N[t] - occ.Tset_n[t])

    @struct.Constraint(time, doc='absolute value constraint, lower bound D')
    def _bound_D1(b, t):
        return b.comfort_D[t] >= -b.alpha * (b.Top_D[t] - occ.Tset_d[t])

    @struct.Constraint(time, doc='absolute value constraint, upper bound D')
    def _bound_D2(b, t):
        return b.comfort_D[t] >= (1 - b.alpha) * (b.Top_D[t] - occ.Tset_d[t])


def environment(env, **kwargs):
    """
    Environment Block

    Gather environment parameter such as temperatures, (irradiation, humidity, weather could be loaded here)

    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    Te              External temperature
    Tg              Ground temperature
    =============== ===================================================================

    :param env:
    :param kwargs:
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))

    env.Te  = Param(time, default=0, doc='External temperature', within=Reals, units=u.deg)
    env.Tg  = Param(time, default=10, doc='Ground temperature', within=Reals, units=u.deg)


def occupancy(occ, **kwargs):
    """
    Occupancy block

    The occupancy block gathers all the dynamic paramters related to occupancy, such as hot water flow, internal
    heat gains, temperature set point and comfort coefficient  for night and day zone.

    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    Q_sol_N         Northern component solar radiation
    Q_sol_S         Southern component solar radiation
    Q_sol_E         Eastern component solar radiation
    Q_sol_W         Western component solar radiation
    Q_int_D         Day zone Internal heat gains
    Q_int_N         Night zone Internal heat gains
    Tset_d          Day zone set temperature
    Tset_n          Night zone Set temperature
    Flow_HW         HW demand of the occupants
    u_N             comfort coefficient for night zone
    u_D             comfort coefficient for day zone
    =============== ===================================================================

    :param occ: occupancy block
    :param kwargs: options for the block construction (time set)
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))

    # solar gains are included here because it is treated as a heat gain in the graph description
    occ.Q_sol_N = Param(time, default=0, doc='Northern component solar radiation', within=Reals, units=u.watt)
    occ.Q_sol_S = Param(time, default=0, doc='Southern component solar radiation', within=Reals, units=u.watt)
    occ.Q_sol_E = Param(time, default=0, doc='Eastern component solar radiation', within=Reals, units=u.watt)
    occ.Q_sol_W = Param(time, default=0, doc='Western component solar radiation', within=Reals, units=u.watt)
    occ.Q_int_D = Param(time, default=0, doc='Day zone Internal heat gains', within=Reals, units=u.watt)
    occ.Q_int_N = Param(time, default=0, doc='Night zone Internal heat gains', within=Reals, units=u.watt)

    occ.Tset_d  = Param(time, default=15, doc='Day zone set temperature', within=Reals, units=u.deg)
    occ.Tset_n  = Param(time, default=15, doc='Night zone Set temperature', within=Reals, units=u.deg)
    occ.Flow_HW = Param(time, default=0, doc='HW demand of the occupants', within=Reals, units=u.watt)
    occ.u_N     = Param(time, default=1, mutable=True, within=NonNegativeReals, doc='comfort coefficient for night zone')
    occ.u_D     = Param(time, default=1, mutable=True, within=NonNegativeReals, doc='comfort coefficient for day zone')


def hot_water_tank(hwt, **kwargs):
    """
    Hot Water TankBlock

    The HW block model the tank as an adiabatic thermal storage.

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    T_HW            HW storage temperature
    =============== ===================================================================
    =============== ===================================================================
    Derivative Var  Documentation
    =============== ===================================================================
    dT_HW           HW temperature derivative
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    T_HW_0          Initial temperature
    T_CW            Temperature of cold water
    T_HW_d          Temperature of demanded hot water
    V               HW storage tank Volume
    c_w             Specific heat capacity of water
    T_HW_LB         HW storage temperature LB
    T_HW_UB         HW storage temperature UB
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    bounds          HW temperature bounds
    init            HW initial temperature
    =============== ===================================================================

    :param hwt:
    :param kwargs:
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))

    hwt.T_HW_0  = Param(default=55, doc='Initial temperature ', within=Reals, units=u.deg)
    hwt.T_HW    = Var(time, initialize=55, units=u.deg, bounds=(0, 100), doc="HW storage temperature")
    hwt.T_CW    = Param(default=10, doc='Temperature of cold water', within=Reals, units=u.deg)
    hwt.T_HW_d  = Param(default=42, doc='Temperature of demanded hot water', within=Reals, units=u.deg)
    hwt.V       = Param(default=200, doc='HW storage tank Volume', within=Reals, units=u.kg)
    hwt.c_w     = Param(default=4186, doc='Specific heat capacity of water', within=Reals)
    hwt.T_HW_LB = Param(default=42, doc='HW storage temperature LB', within=Reals, units=u.deg)
    hwt.T_HW_UB = Param(default=56, doc='HW storage temperature UB', within=Reals, units=u.deg)

    hwt.dT_HW = DerivativeVar(hwt.T_HW, wrt=time, doc="HW temperature derivative",  units=u.deg / u.s)

    @hwt.Constraint(time, doc = 'HW temperature bounds')
    def bounds(b, t):
        return b.T_HW_LB, b.T_HW[t], b.T_HW_UB

    @hwt.Constraint(doc = 'HW initial temperature')
    def init(b):
        return b.T_HW[0] == b.T_HW_0


def heat_pump(hp, **kwargs):
    """
    Heat pump Block

    The HP is modelled by tree heat control variable (day_zone, night_zone and HW tank). The total electrical power is
    calculated is the COP parameter.

    =============== ===================================================================
    Variables       Documentation
    =============== ===================================================================
    Q_heat_N        Heat pump flow Night zone
    Q_heat_D        Heat pump flow Day zone
    Q_heat_HW       Heat pump flow HW tank
    =============== ===================================================================
    =============== ===================================================================
    Parameters      Documentation
    =============== ===================================================================
    Q_heat_D_max    Maximal heat production in the day-zone
    Q_heat_N_max    Maximal heat production in the night-zone
    Q_HW_max        Maximal heat production in the HW storage tank
    COP             Coefficient of performance
    =============== ===================================================================
    =============== ===================================================================
    Constraints     Documentation
    =============== ===================================================================
    limits          heat_pumps heating bounds
    =============== ===================================================================
    =============== ===================================================================
    Expressions     Documentation
    =============== ===================================================================
    p_elec_D        Electrical power in the day zone
    p_elec_N        Electrical power in the night zone
    p_elec_HW       Electrical power for DHW
    =============== ===================================================================

    :param hp: Heat pump block
    :param kwargs: options for the block construction (time set and occupancy block)
    :return:
    """
    time  = kwargs.pop('time', ContinuousSet(bounds=(0, 1), doc='Time set'))
    occ   = kwargs.pop('occ', None)

    hp.Q_heat_D_max = Param(default=10000, doc='Maximal heat production in the day-zone')
    hp.Q_heat_N_max = Param(default=10000, doc='Maximal heat production in the night-zone')
    hp.Q_HW_max     = Param(default=2000,  doc='Maximal heat production in the HW storage tank')

    hp.Q_heat_N  = Var(time, initialize=0, doc='Heat pump flow Night zone', units=u.watt, bounds=(0, hp.Q_heat_N_max))
    hp.Q_heat_D  = Var(time, initialize=0, doc='Heat pump flow Day zone', units=u.watt, bounds=(0, hp.Q_heat_D_max))
    hp.Q_heat_HW = Var(time, initialize=0, doc='Heat pump flow HW tank', units=u.watt, bounds=(0, hp.Q_HW_max))

    hp.COP = Param(default=3, domain=NonNegativeReals, doc='Coefficient of performance')

    @hp.Expression(time, doc='Electrical power in the day zone')
    def p_elec_D(b, t):
        return b.Q_heat_D[t] / b.COP

    @hp.Expression(time, doc='Electrical power in the night zone')
    def p_elec_N(b, t):
        return b.Q_heat_N[t] / b.COP

    @hp.Expression(time, doc='Electrical power for DHW')
    def p_elec_HW(b, t):
        return b.Q_heat_HW[t] / b.COP

    @hp.Constraint(time, doc='heat_pumps heating bounds')
    def limits(b, t):
        return 0, b.Q_heat_N[t], occ.u_N[t] * b.Q_heat_N_max


def dwelling_v1(b, **kwargs):
    graph = kwargs.pop('graph', None)
    horizon = kwargs.pop('horizon', 7200)

    b.time   = ContinuousSet(bounds=(0, horizon), doc='set of time')
    b.env    = Block(rule = environment, options={'time': b.time})
    b.sol    = Block(rule = solar_inputs, options={'time': b.time})
    b.hwt    = Block(rule = hot_water_tank, options={'time': b.time})
    b.occ    = Block(rule = occupancy, options={'time': b.time})
    b.hp     = Block(rule = heat_pump, options={'time': b.time, 'occ': b.occ})
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
    env = kwargs.pop('env', Block(rule=environment, options={'time': time}))

    b.sol = Block(rule=solar_inputs, options={'time': time})
    b.hwt = Block(rule=hot_water_tank, options={'time': time})
    b.occ = Block(rule=occupancy, options={'time': time})
    b.hp = Block(rule=heat_pump, options={'time': time, 'occ': b.occ})
    b.struct = Block(rule=thermal_structure_block, options={'time': time, 'graph': graph, 'env': env, 'occ': b.occ})

    b.p_elec_max = Var(initialize=0, doc='Maximal electrical power ', units=u.watt, bounds=(0, 1e6))

    @b.Constraint(time, doc='HW power balance')
    def hw_balance(b, t):
        # TODO : the factor 900 comes from the hot water flow unit, which is liter per 15 min
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
        # TODO : handling sum of all electric power by hand, one might find a way to some automatically
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