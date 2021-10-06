Working with Pyomo
==================

The LMS2 library is based on the pyomo package. Some references for documentation, exercices and examples :

    - Documentation on the pyomo language is available at : http://www.pyomo.org/documentation/
    - Get started with Pyomo : https://github.com/Pyomo/PyomoGettingStarted
    - Gallery of state-of-the-art optimization problem : https://github.com/Pyomo/PyomoGallery
    - Pyomo Workshop, slides + exercices + solutions (2018) : http://www.pyomo.org/workshop-examples

1) Simple example using pyomo language
---------------------------------------

- Creating an basic Model using pyomo package

.. code-block:: python

    m = AbsLModel(name = 'Model')
    m.v = Var(doc='a viariable', within=NonNegativeIntegers)

    m.p = Param(default=10, doc='a parameter')
    m.c = Param(default=1, doc='cost associated to variable "v"')

    m.cst = Constraint(expr= 0 <= m.v*m.p <= 15)
    m.obj = Objective(expr=m.c*m.v, sense=1)

- Creating an instance of this model and print it using `pprint()` :

.. code-block:: python

    inst = m.create_instance()
    inst.pprint()

    2 Param Declarations
    c : cost associated to variable "v"
        Size=1, Index=None, Domain=Any, Default=1, Mutable=False
        Key : Value
    p : a parameter
        Size=1, Index=None, Domain=Any, Default=10, Mutable=False
        Key : Value
    >>> 1 Var Declarations
    >>>     v : a viariable
    >>>         Size=1, Index=None
    >>>         Key  : Lower : Value : Upper : Fixed : Stale : Domain
    >>>         None :     0 :  None :  None : False :  True : NonNegativeIntegers
    >>> 1 Objective Declarations
    >>>     obj : Size=1, Index=None, Active=True
    >>>         Key  : Active : Sense    : Expression
    >>>         None :   True : minimize :        c*v
    >>> 1 Constraint Declarations
    >>>     cst : Size=1, Index=None, Active=True
    >>>         Key  : Lower : Body : Upper : Active
    >>>         None :   0.0 :  p*v :  15.0 :   True
    >>> 5 Declarations: v p c cst obj


- Solving the problem :

.. code-block:: python

    from pyomo.environ import SolverFactory
    opt = SolverFactory("glpk")
    results = opt.solve(inst, tee=False)

    inst.v()
    >>> 1.0

2) working with pyomo  abstract model
-------------------------------------

Lms2 is based on abstract models that allows a clear separation between the mathematical model and data (i.e. values of parameters, set or initial values). See : https://pyomo.readthedocs.io/en/latest/working_abstractmodels/index.html for more details.

The basic steps of a simple modeling process are:

- Create an empty model
- declare components (blocks, parameter, constraints, etc.)
- Instantiate the model
- Load data
- Apply solver
- Interrogate solver results

- Here a full example using a different data set :

.. code-block:: python

    from pyomo.environ import *
    from pyomo.dae import *

    am = AbstractModel()
    am.t = ContinuousSet()
    am.x = Var(am.t, initialize=0)
    am.y = Var(am.t, initialize=0)
    am.p = Param()

    am.b = Block()
    am.b.x = Var(am.t, initialize=0)
    am.b.xmax = Param()
    am.b.p = Param()


    def cst(m, t):
        if m.p.value is None:
            return Constraint.Skip
        else :
            return 0, m.x[t] + m.p * m.y[t], 10

    def exp(m, t):
        if m.p.value is None:
            return 0
        else:
            return m.p*m.x[t] + m.p*m.y[t]


    am.c = Constraint(am.t, rule=cst)
    am.exp = Expression(am.t, rule=exp)
    am.pprint()

    data = dict(
        p={None: None},
        t={None: (0, 2)},
        b=dict(
            xmax={None: 15},
            p={None: None}
        )
    )

    inst = am.create_instance({None: data})
    TransformationFactory('dae.finite_difference').apply_to(inst, nfe=10)
    inst.pprint()

