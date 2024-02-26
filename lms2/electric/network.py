import logging
import numpy as np
from pyomo.core import NonNegativeReals, Reals
from pyomo.environ import *
from pyomo.environ import units as u
from dataclasses import dataclass, field


logger = logging.getLogger('lms2.network')


@dataclass(repr=True, eq=True)
class Cable:
    """
    Cable object description

    A cable is a dataclass object described by a name, doc, type, linear resistance, reactance, nominal voltage
    and nominal power. Using dataclass make it easier to switch from a cable to another.

    """
    name: str = field(compare=False)
    doc: str = field(compare=False)
    type: str = field(compare=False)
    r: np.ndarray = field(repr=False)                   # resistance array
    x: np.ndarray = field(repr=False)                   # reactance array
    s_nom: float = field(repr=False)                    # nominal power in kW for one phase
    v_nom: float = field(repr=False)                    # nominal voltage
    unit_price: float = field(repr=False, default=0)    # unit price in Euro/kilometer


cable_3_150_95 = Cable(name  = 'cable_3_150_95',
                       doc   = 'Cable triphasé de section 150 mm²',
                       type  = 'triphasé 3 fils',
                       r     = np.array([[0.3953, 0.1834, 0.1908], [0.1834, 0.3809, 0.1834], [0.1908, 0.1834, 0.3953]]),
                       x     = np.array([[0.1602, 0.1216, 0.0844], [0.1216, 0.2067, 0.1216], [0.0844, 0.1216, 0.1602]]),
                       v_nom = 230,
                       s_nom = 250/3)

cable_4_70 = Cable(name  = 'cable_4_70',
                   doc   = 'Cable triphasé de section 70 mm²',
                   type  = 'triphasé 4 fils',
                   r     = np.array([[0.679, 0.2317, 0.2409], [0.2317, 0.6612, 0.2317], [0.2409, 0.2317, 0.6791]]),
                   x     = np.array([[0.2151, 0.1748, 0.1394], [0.1748, 0.2583, 0.1748], [0.1394, 0.1748, 0.2151]]),
                   v_nom = 230,
                   s_nom = 90/3)


def network_3phases_lindistflow(dist, **kwargs):
    """
    Linear load flow equation for tree phased unbalanced distribution network.

    Takes as input a radial network (see :meth:`lms2.electric.network_graph`)
    pmatrix and qmatrix are used to compute the square voltage magnitudes

    The network has three phases :
    - to each node of the input network is associated three square voltage magnitudes (one for each phase)
    - to each edge of the input network is associated three reactive powers (q) and three active powers (p)

    P, Q are indexed with: edges, phases and time
    Y denotes the square voltage magnitudes (V²) and is indexed with nodes, phases and time

    the power constraints are computed for each node with no dwelling of the network considering that the power entering
    the node is equal to the power exiting the node; when there is a source/load on the considered node,
    the power balance also needs to take into account this source/load --> this constraint needs to be added outside this
    function.

    .. table::
        :width: 100%
        =============== ===================================================================
        Sets            Documentation
        =============== ===================================================================
        edges           lines of the electrical distribution network
        nodes           buses of the electrical distribution network
        phases          phase index (instead of "a, b, c")
        =============== ===================================================================

    .. table::
        :width: 100%
        =============== ===================================================================
        Variables       Documentation
        =============== ===================================================================
        y               voltage square magnitudes in V²
        p               active power between two nodes in kW
        q               reactive power between two nodes in kW
        q_out           reactive power injection, using source convention in kW
        p_out           active power injection in kW
        =============== ===================================================================

    .. table::
        :width: 100%
        =============== ===================================================================
        Constraints     Documentation
        =============== ===================================================================
        unbalance_1     Voltage unbalance 1
        unbalance_2     Voltage unbalance 2
        active_balance  Active power balance on each node and phase
        reactive_balance Reactive power balance on each node and phase
        y_constraint    Linear DistFlow constraint for each edges
        active_transfo  Active Power Bounds of the transformer
        reactive_transfo Reactive Power Bounds of the transformer
        pq_transfo1     Linear approximation of the circular constraint on Snom
        pq_transfo2     Linear approximation of the circular constraint on Snom
        pq_line1        Linear approximation of the circular constraint on Snom
        pq_line2        Linear approximation of the circular constraint on Snom
        =============== ===================================================================


    This function is based on the article :
    E. Stewart, « A Linearized Power Flow Model for Optimization in Unbalanced Distribution Systems », 2016
    :cite:t:`sankur2016linearized`

    """
    dist.graph = kwargs.pop('graph', None)
    if dist.graph is None:
        raise ValueError('Need to specify an input radial network')

    time = kwargs.get('time', RangeSet(0, 1))
    dist.edges = Set(initialize=list(dist.graph.edges()), doc='lines of the electrical distribution network')
    dist.nodes = Set(initialize=list(dist.graph.nodes()), doc='buses of the electrical distribution network')
    dist.phases = Set(initialize=[0, 1, 2], doc='phase index (instead of "a, b, c"')  # phases indexes

    # Here are some function to initialize variable and their bounds. We use data from the graph,
    # nominal voltage or maximal power for instance.
    def initialize_pout(b, node, phase, time):
        try:
            p_out_init = b.graph.nodes[node]['p_out'][phase]
        except KeyError as err:
            p_out_init = 0
            logger.info(f'')
        return p_out_init

    def initialize_y_bounds(b, node, phase, time):
        """ Here we search for all edges connected to that node, and we consider the smaller nominal voltage
        to compute the bounds +/- 10 %. todo : add +/- 10% as a parameter somehow. """
        common_edges = list(b.graph.in_edges(node)) + list(b.graph.out_edges(node))
        v_nom = min([b.graph.edges[n1, n2]['cable'].v_nom for n1, n2 in common_edges])
        return (v_nom*0.9)**2, (v_nom*1.1)**2

    def initialize_qout(b, node, phase, time):
        try:
            q_out_init = b.graph.nodes[node]['q_out'][phase]
        except KeyError as err:
            q_out_init = 0
            logger.info(f'')
        return q_out_init

    def intialize_pout_bounds(b, node, phase, time):
        try:
            ub = b.graph.nodes[node]['p_out_max'][phase]
        except KeyError:
            ub = None
        try:
            lb = b.graph.nodes[node]['p_out_min'][phase]
        except KeyError:
            lb = None
        return lb, ub

    def intialize_qout_bounds(b, node, phase, time):
        try:
            ub = b.graph.nodes[node]['q_out_max'][phase]
        except KeyError:
            ub = None
        try:
            lb = b.graph.nodes[node]['q_out_min'][phase]
        except KeyError:
            lb = None
        return lb, ub

    def initialize_q_bounds(b, node1, node2, phase, time):
        return -b.graph.edges[node1, node2]['cable'].s_nom, b.graph.edges[node1, node2]['cable'].s_nom

    def initialize_p_bounds(b, node1, node2, phase, time):
        return -b.graph.edges[node1, node2]['cable'].s_nom, b.graph.edges[node1, node2]['cable'].s_nom

    def initialize_y(b, node, phase, time):
        """ Here we search for all edges connected to that node, and we consider the smaller nominal voltage"""
        try:
            common_edges = list(b.graph.in_edges(node)) + list(b.graph.out_edges(node))
            return min([b.graph.edges[n1, n2]['cable'].v_nom for n1, n2 in common_edges])**2
        except:
            logger.error(f'Problem with the node {node}')

    # We define variables

    dist.y = Var(dist.nodes, dist.phases, time, within=NonNegativeReals, bounds=initialize_y_bounds,
                 doc='voltage square magnitudes in V²', initialize=initialize_y, units=u.V * u.V)
    dist.p = Var(dist.edges, dist.phases, time, within=Reals, bounds=initialize_p_bounds, initialize=0,
                 doc='active power between two nodes in kW',  units=u.kW)
    dist.q  = Var(dist.edges, dist.phases, time, within=Reals, bounds=initialize_q_bounds, initialize=0,
                 doc='reactive power between two nodes in kW',  units=u.kW)
    dist.q_out = Var(dist.nodes, dist.phases, time, initialize=initialize_qout, within=Reals,
                     bounds=intialize_qout_bounds, doc='reactive power injection, using source convention in kW', units=u.kW)
    dist.p_out = Var(dist.nodes, dist.phases, time, initialize=initialize_pout, within=Reals,
                     bounds=intialize_pout_bounds, doc='active power injection in kW', units=u.kW)


    # variables p_in, p_out are initialized using rules initialize_pout and initialize_qout but can be fixed or unfixed
    # using the key 'fixed' in the edges' data of the graph. First we fixe them all.
    dist.p_out.fix()
    dist.q_out.fix()

    # Then we unfix selected nodes and phase if fixed is False
    for node, node_data in dist.graph.nodes(data=True):
        if isinstance(node_data, dict):  # if there is no data, node_data is None_type
            try:
                for i, fix_boolean in enumerate(node_data['fix_p_out']):
                    if not fix_boolean:
                        dist.p_out[node, i, :].unfix()
            except KeyError:
                logger.warning(f'Could not initialize Variable {dist.p_out[node, :, :]}')

    # Same thing for q_out
    for node, node_data in dist.graph.nodes(data=True):
        if isinstance(node_data, dict):  # if there is no data, node_data is None_type
            try:
                for i, fix_boolean in enumerate(node_data['fix_q_out']):
                    if not fix_boolean:
                        dist.q_out[node, i, :].unfix()
            except KeyError:
                logger.warning(f'Could not initialize Variable {dist.q_out[node, :, :]}')

    # Here we define the constraints

    @dist.Constraint(dist.nodes, dist.phases, time, doc='Voltage unbalance 1')
    def unbalance_1(dist, j, phi, t):
        y_avg = sum(dist.y[j, ph, t] for ph in dist.phases) / 3
        return -0.1 * y_avg <= dist.y[j, phi, t] - y_avg

    @dist.Constraint(dist.nodes, dist.phases, time, doc='Voltage unbalance 2')
    def unbalance_2(dist, j, phi, t):
        y_avg = sum(dist.y[j, ph, t] for ph in dist.phases) / 3
        return dist.y[j, phi, t] - y_avg <= 0.1 * y_avg

    @dist.Constraint(dist.nodes, dist.phases, time, doc='Active power balance on each node and phase')
    def active_balance(dist, j, phase, t):
        """
        Active power balance on each node.

        The sum of the active power entering the node (predecessors) is equal to the sum of the active power
        exiting the node (successors)
        P_{ij} = P_j_out + \sum_{m:j->m} P_{jm}
        """
        Childs = list(dist.graph.successors(j))  # children nodes of node j
        Parents = list(dist.graph.predecessors(j))

        if dist.nodes.first() < j:
            # if the node is not the first, then parents are not empty of lenth 1 (radial)
            parent = Parents[0]
            if len(Childs) > 0:
                return (dist.p[(parent, j), phase, t] ==
                        dist.p_out[j, phase, t] + sum(dist.p[(j, child), phase, t] for child in Childs))
            else:
                return dist.p[(parent, j), phase, t] == dist.p_out[j, phase, t]
        else:
            return Constraint.Skip

    @dist.Constraint(dist.nodes, dist.phases, time, doc='Reactive power balance on each node and phase')
    def reactive_balance(dist, j, phase, t):
        """
        Reactive power balance on each node and phase

        The sum of the reactive power entering the node (predecessors) is equal to the sum of the reactive power
        exiting the node (sucessors)
        Q_{pj} = Q_j_out + \sum_{m:k->m} Q_{jm}
        """

        Childs = list(dist.graph.successors(j))  # children nodes of node j
        Parents = list(dist.graph.predecessors(j))

        if dist.nodes.first() < j:
            # if the node is not the first, then parents are not empty of lenth 1 (radial)
            parent = Parents[0]
            if len(Childs) > 0:
                return (dist.q[(parent, j), phase, t] == dist.q_out[j, phase, t]
                        + sum(dist.q[(j, child), phase, t] for child in Childs))
            else:
                return dist.q[(parent, j), phase, t] == dist.q_out[j, phase, t]
        else:
            return Constraint.Skip

    @dist.Constraint(dist.edges, dist.phases, time, doc='Linear DistFlow constraint for each edges')
    def y_constraint(dist, i, j, phi, t):
        """
        |Vk|^2 = |Vi|^2 - 2(R_{ik}P_{ik} + X_{ik}Q_{ik})
        """
        return dist.y[i, phi, t] == dist.y[j, phi, t] - (
                sum(dist.graph[i][j]['pmatrix'][phi][phase] * dist.p[(i, j), phase, t] for phase in dist.phases) +
                sum(dist.graph[i][j]['qmatrix'][phi][phase] * dist.q[(i, j), phase, t] for phase in dist.phases))


    # fixing voltage for the first node (supposed to be the primary of the transformer)
    first_node = dist.nodes.first()
    dist.y[first_node, :, :].fix()

    @dist.Constraint(dist.edges, time, doc='Active Power Bounds of the transformer')
    def active_transfo(b, i, j, t):
        if (i, j) == b.edges.first():
            return -3 * dist.graph.edges[i, j]['cable'].s_nom, sum(b.p[i, j, phi, t] for phi in b.phases), 3 * dist.graph.edges[i, j]['cable'].s_nom
        else:
            return Constraint.Skip

    @dist.Constraint(dist.edges, time, doc='Reactive Power Bounds of the transformer')
    def reactive_transfo(b, i, j, t):
        if (i, j) == b.edges.first():
            return -3*dist.graph.edges[i, j]['cable'].s_nom, sum(b.q[i, j, phi, t] for phi in b.phases), 3*dist.graph.edges[i, j]['cable'].s_nom
        else:
            return Constraint.Skip

    @dist.Constraint(dist.edges, time, doc = 'Linear approximation of the circular constraint on Snom')
    def pq_transfo1(b, i, j, t):
        if (i, j) == b.edges.first():
            return -np.sqrt(2) * 3 * dist.graph.edges[i, j]['cable'].s_nom, sum(b.q[(i, j), phi, t] + b.p[(i, j), phi, t] for phi in b.phases), np.sqrt(
                2) * 3 * dist.graph.edges[i, j]['cable'].s_nom
        else:
            return Constraint.Skip

    @dist.Constraint(dist.edges, time, doc = 'Linear approximation of the circular constraint on Snom')
    def pq_transfo2(b, i, j, t):
        if (i, j) == b.edges.first():
            return -np.sqrt(2) * 3 * dist.graph.edges[i, j]['cable'].s_nom, sum(b.p[i, j, phi, t] - b.q[i, j, phi, t] for phi in b.phases), np.sqrt(2) * 3 * dist.graph.edges[i, j]['cable'].s_nom
        else:
            return Constraint.Skip

    @dist.Constraint(dist.edges, dist.phases, time, doc = 'Linear approximation of the circular constraint on Snom')
    def pq_line1(b, i, j, phi, t):
        if (i, j) == b.edges.first():
            return Constraint.Skip
        else:
            return -np.sqrt(2) * dist.graph.edges[i, j]['cable'].s_nom, b.q[i, j, phi, t] + b.p[i, j, phi, t], np.sqrt(2) * dist.graph.edges[i, j]['cable'].s_nom

    @dist.Constraint(dist.edges, dist.phases, time, doc = 'Linear approximation of the circular constraint on Snom')
    def pq_line2(b, i, j, phi, t):
        if (i, j) == b.edges.first():
            return Constraint.Skip
        else:
            return -np.sqrt(2) * dist.graph.edges[i, j]['cable'].s_nom, b.p[i, j, phi, t] - b.q[i, j, phi, t], np.sqrt(2) * dist.graph.edges[i, j]['cable'].s_nom
