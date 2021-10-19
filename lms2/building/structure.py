from pyomo.core import Set, Var, Param, Constraint, Reals, NonNegativeReals
from pyomo.core.base.units_container import units as u
from pyomo.dae import ContinuousSet, DerivativeVar
from pyomo.core.base.set import Any

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
    :param kwargs: kwargs needed for the block construction
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