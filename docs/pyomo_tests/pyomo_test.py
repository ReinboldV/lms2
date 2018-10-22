
if __name__ == "__main__":

    from lms2.core.models import LModel
    from lms2.core.time import Time
    from lms2.electric.batteries import Battery

    from pyomo.environ import *

    model = LModel(name='model')

    model.time = Time('00:00:00', '03:00:00', freq='30Min')
    #time = model.time.time_contSet

    model.bat = Battery(time=model.time.time_contSet, e0=50, pcmax=10, pdmax=20, ef=50, etac=0.8, etad=0.9, emax=100)
    model.bat2 = Battery(time=model.time.time_contSet, e0=50, pcmax=10, pdmax=20, ef=50, etac=0.8, etad=0.9, emax=100)

    # discretizer = TransformationFactory('dae.finite_difference')
    # discretizer.apply_to(model, wrt=model.time.time_contSet, nfe=6, scheme='BACKWARD')  # BACKWARD or FORWARD

    discretizer = TransformationFactory('dae.collocation')
    discretizer.apply_to(model, nfe=3, ncp=3, scheme='LAGRANGE-RADAU') # LAGRANGE-LEGENDRE or LAGRANGE-RADAU

    model.bat2.e.port_type = 'effort'
    model.bat.e.port_type = 'effort'
    model.connect_effort(model.bat.e, model.bat2.e)

    model.graph.nodes(data=True)
    model.pprint()








