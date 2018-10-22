
if __name__ == "__main__":
    from pyomo.environ import *

    from lms2.core.models import LModel
    from lms2.core.time import Time
    from lms2.electric.batteries import Battery
    from lms2.base.base_units import FlowSource
    # from lms2.core.var import Var
    from pyomo.dae.diffvar import DerivativeVar
    from pyomo.dae.contset import ContinuousSet

    import time as pyt
    import pandas as pd

    model = LModel(name='model')

    # time = model.t.time_contSet

    time = Time('00:00:00', '03:00:00', freq='30Min') #  ContinuousSet(bounds=(1,10)) #
    model.t = ContinuousSet(bounds=(time.timeSteps[0], time.timeSteps[-1]))

    # model.time = Time('00:00:00', '03:00:00', freq='30Min')
    # t = model.time.time_contSet

    f = pd.Series([0, 10, 50, 25, 20, 10, 10, 0, 0, 0, 90, 45], index=[0, 500, 2000, 2500, 3600, 7500, 8000, 8500, 9000, 9500, 10000, 10800])

    model.s = FlowSource(time=model.t, profile=f)
    model.bat1 = Battery(time=model.t, e0=12.0, emin=0.0, emax=500000, etac=0.8, etad=0.9, pcmax=100, pdmax=100)
    # model.bat2 = Battery(time=model.t, e0=50, etac=0.9, etad=0.9, pcmax=100, pdmax=100)

    model.connect_flux('s.flow', 'bat1.p') # , 'bat2.p')
    # model.

    t1 = pyt.time()
    discretizer = TransformationFactory('dae.finite_difference')
    discretizer.apply_to(model, nfe=25)  # BACKWARD or FORWARD
    print(f'discretization time : {pyt.time()-t1}')

    def _obj(m):
        return 0

    model.obj = Objective(rule=_obj)

    instance = model.clone()
    opt = SolverFactory('gurobi')
    t1 = pyt.time()
    results = opt.solve(instance)
    print(f'optim time : {pyt.time()-t1}')

    # model.pprint()

    from pyomo.opt import SolverStatus, TerminationCondition

    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        # this is feasible and optimal
        print(results.solver)
    elif results.solver.termination_condition == TerminationCondition.infeasible:
    # do something about it? or exit?
        print(results.solver)
    else:
        # something else is wrong
        print(results.solver)

    # for v in instance.component_objects(Var):
    #     print(v.name)
    #     for vi in v.itervalues():
    #         print(vi.value)

