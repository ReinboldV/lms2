# -*- coding: utf-8 -*-
"""
DrahiX case using variable cost

"""

if __name__ == "__main__":

    from lms2 import AbsDrahiX_v2
    from pyomo.environ import TransformationFactory, SolverFactory
    from pyomo.environ import Objective
    from pyomo.dae import Integral

    from lms2.template.drahix.abs_drahix_tools import get_drahix_data

    kwargs = {
        't_start':  '2018-06-01 00:00:00',
        't_end':    '2018-06-03 00:00:00',
        'freq':     '15Min'
    }

    import time

    t1 = time.time()

    path = '/home/admin/Documents/02-Recherche/02-Python/lms2/lms2/template/drahix/abs_drahix_data_cost.csv'
    df, t = get_drahix_data(path=path, **kwargs)

    data_batt = {
        'time':   {None: [df.index[0], df.index[-1]]},
        'socmin': {None: 10},
        'socmax': {None: 95},
        'soc0':   {None: 50},
        'socf':   {None: None},
        'dpcmax': {None: 1},
        'dpdmax': {None: 1},
        'emin':   {None: 0},
        'emax':   {None: 50},
        'pcmax':  {None: 5.0},
        'pdmax':  {None: 5.0},
        'etac':   {None: 0.95},
        'etad':   {None: 0.95}}

    data_mg = {
        'time': {None: [df.index[0], df.index[-1]]},
        'pmax': {None: 10},
        'pmin': {None: 0},
        'cost_in_index':  {None: df.index},
        'cost_out_index': {None: df.index},
        'cost_in_value':  {i : 0 for i in df.index},
        'cost_out_value': df.tarifs_bleu.to_dict()   # selection du tarif bleu
    }

    data_ps = {
        'time': {None: [df.index[0], df.index[-1]]},
        'profile_index': {None: df.index},
        'profile_value': df['P_pv'].to_dict()
    }

    data_pl = {
        'time': {None: [df.index[0], df.index[-1]]},
        'profile_index': {None: df.index},
        'profile_value': df['P_load'].to_dict()}

    data = {None: {
        'time': {None: [df.index[0], df.index[-1]]},
        'batt': data_batt,
        'mg': data_mg,
        'ps': data_ps,
        'pl': data_pl}}

    t2 = time.time() - t1
    print(f'Elapsed time for reading data : \t {t2}')

    drx = AbsDrahiX_v2()

    t1 = time.time()
    inst = drx.create_instance(data)
    t2 = time.time() - t1
    print(f'Elapsed time for creating instance : \t {t2}')

    inst.int = Integral(inst.time, wrt=inst.time, rule=lambda m, i: m.mg.instant_cost[i])
    inst.obj = Objective(expr=inst.int)

    inst.ps.debug_flow_scaling.deactivate()

    #%%  Discretizing and Optimizing
    import time

    t1 = time.time()
    TransformationFactory('dae.finite_difference').apply_to(inst, nfe=t.nfe)
    TransformationFactory("network.expand_arcs").apply_to(inst)
    t2 = time.time() - t1
    print(f'Elapsed time for discretization : \t {t2}')
    # inst.batt.deactivate()

    t1 = time.time()
    # opt = SolverFactory("glpk")
    opt = SolverFactory("gurobi", solver_io="direct")
    results = opt.solve(inst, tee=False)
    t2 = time.time() - t1
    print(f'Elapsed time for solving : \t {t2}')

    #%%  Post Processing and plots

    from lms2 import pplot
    import matplotlib.pyplot as plt
    from lms2.template.drahix.abs_drahix_tools import pgf_with_latex
    import matplotlib as mpl

    mpl.rcParams.update(pgf_with_latex)

    f = plt.figure()
    a = f.subplots(1, 1)
    pplot(inst.mg.p, inst.ps.p_scaled, inst.batt.p, inst.pl.p, fig=f, ax=a, index=t.datetime,
          legend=False, title="Bilan d'énergie"+f'   Cost of Use : ${inst.obj():.3f}~(euros)$', Marker='x', markevery=5)

    plt.legend(['Réseau', f'PV (${inst.ps.scale_fact():.1f} m^2$)',
                f'Batterie (${inst.batt.emax()}~kW.h$)', 'Charge (Zone 1)', '$p_{max}$ réseau'], loc=1)

    a.set_ylabel('Puissance (kW)')

    plt.grid(True)

    pplot(inst.batt.soc, marker='x', index=t.datetime)