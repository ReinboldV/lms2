Working with pyomo-lmes library components
==========================================

pyomo-lmes library gather mathematical models described using the pyomo mathematical language. All components, e.g. batteries, distribution grid, sources and charges are based on blocks. Available models are classified based on their fields, such as electric, thermal, economic, environement, etc. Some tools are also proposed for data processing, model processing, post_processing and decomposition strategies for dynamic and energetic systems (Bender's decomposition).

Models are created by aggregating blocks and create connexion, either using pyomo.network.Port or building constraints between variable from different block, or gathering objectives of different blocks.

The time is usually modeled as a continuous set by means of the modeling extension pyomo.dae (See : https://pyomo.readthedocs.io/en/latest/modeling_extensions/dae.html. All blocks of a model share the same time set.

1) Example of a block
----------------------

Example of a dummy block. It consists of two variables, one constraint and one expression that depends on external components : the set `time` and the block `env`. They are passed as key-word arguments.

.. code-block:: python

    from pyomo.environ import *
    from pyomo.environ import units as u
    from pyomo.core import Reals, PositiveReals, NonNegativeReals, Any, Binary
    from pyomo.dae import DerivativeVar, Integral, ContinuousSet


    def dummy_block(b, **kwargs):
        time = kwargs.pop('time', ContinuousSet(bounds=(0, 1)))
        env = kwargs.pop('env', None)
        b.x = Var(time, initialize=0, units=u.deg, bounds=(-20, 55), doc="nodes temperature")
        b.dx = DerivativeVar(b.x, initialize=0, wrt=time)

        @b.Expression(time)
        def exp(b, t):
            return b.x[t] + env.Te

        @b.Constraint()
        def sum_over_time(b):
            return sum([b.exp[t] for t in time]) >= 100


2) Example of model by aggregation of library's blocks
------------------------------------------------------

Constructing a model based on this block is quite simple :

.. code-block:: python

    m = ConcreteModel()
    m.i = RangeSet(1)
    m.time = ContinuousSet(bounds=(0, 5))
    m.env = Block()
    m.env.Te = Param(initialize=10)
    TransformationFactory('dae.finite_difference').apply_to(m, nfe=10)

    options = {'env': m.env, 'time': m.time}
    m.b = Block(rule=dummy_block, options={'env': m.env, 'time': m.time})

.. warning:: When using sum over continuous set, one should make the descretisation before instantiation o the blocks. Otherwise, the expression will only take into account the first and the last index of the continuous set. To overcome this, one could also use `pyomo.dae.Integral`: https://pyomo.readthedocs.io/en/stable/modeling_extensions/dae.html?highlight=Integral#declaring-integrals.

3) Example of creating blocks indexed by a set
----------------------------------------------

One may instantiate a set of similar blocks. Following the pyomo language, this can be done by giving a set in the Block
initialization method:

.. code-block:: python

    from pyomo.environ import *
    from lms2.electric.sources import pv_panel, fixed_power_load, power_source
    m = ConcreteModel()
    m.time = ContinuousSet(initialize=[0, 10])
    m.s = Set(initialize=['north', 'south', 'east'])
    option_pv = {'time': m.time, 's_max': 10, 's_min': 0.1}
    m.pv = Block(m.s, rule=lambda x: pv_panel(x, **option_pv))
