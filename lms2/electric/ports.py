from pyomo.network import Port


def p_outlet(m):
    return dict(p=(m.p_out, Port.Extensive))


def p_inlet(m):
    return dict(p=(m.p_in, Port.Extensive))


def ui_inlet(m):
    return dict(u=m.u, i=(m.i, Port.Extensive))


def ui_outlet(m):
    return dict(u=m.u, i=(m.i, Port.Extensive))
