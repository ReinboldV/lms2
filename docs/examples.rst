Tutorial Examples
*****************

Working with Pyomo
==================

The LMS2 library is based on the pyomo package. Some references for documentation, exercices and examples :

-Documentation on the pyomo language is available at : http://www.pyomo.org/documentation/
-Get started with Pyomo : https://github.com/Pyomo/PyomoGettingStarted
-Gallery of state-of-the-art optimization problem : https://github.com/Pyomo/PyomoGallery
-Pyomo Workshop, slides + exercices + solutions (2018) : http://www.pyomo.org/workshop-examples

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

2) working with abstract model
-------------------------------

Lms2 is based on abstract models that allows a clear separation between the mathematical model and data (i.e. values of parameters, set or initial values). see : https://pyomo.readthedocs.io/en/latest/working_abstractmodels/index.html for more details.

- Here an example of instantiating our example using different data

.. code-block:: python

    data = {None: {'p': {None: 5},
                   'c': {None: 2}}}


    inst2 = m.create_instance(data)



Working with lms2 library components
====================================

Pyomo supports an object-oriented design for the definition of optimization models. The basic steps of a simple modeling process are:

- Create model and declare components
- Instantiate the model
- Apply solver
- Interrogate solver results

Lms2 library gather mathematical models described using the pyomo mathematical language. All components, e.g. batteries, distribution grid, sources and charges are based on classes that inherite from pyomo Simple Blocks. Available models are classified based on their fields, such as electric, thermal, economic, environement, etc.

Models are then created by aggregating blocks and create connexion, i.e. creating constraints between variable from different block, or gathering objectives of different blocks.

The time is modeled as a continuous set by means of the modeling extension pyomo.dae (See : https://pyomo.readthedocs.io/en/latest/modeling_extensions/dae.html. For now, all blocks has his own time set.

1) Example of model by aggregating blocks of the library
---------------------------------------------------------


2) Example of a block
------------------------


