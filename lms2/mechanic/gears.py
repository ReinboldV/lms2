# -*- coding: utf-8 -*-
"""
Contains gears models for mechanics
"""


# class MPole(FluxEffortPole):
#     """ Mechanical pole for gears and rotation modelling """
#     # TODO : implement MPole
#     pass
#
#
# class MDipole(TUnit):
#     """ General Mechanical dipole for Gears """
#     # TODO : implement MDipole
#     pass


class Red1():
    """Gear reduction, with factor k and efficiency e """

    pass
    # todo create Red1

    #
    # def __init__(self, th, name='RED0', description='Gear reduction, witime_horizon factor k and efficiency e', w1=None, w2=None, t1=None, t2=None, e=1., k=1.):
    #     """
    #
    #     :param MG:
    #     :param name:
    #     :param description:
    #     :param w1:
    #     :param w2:
    #     :param t1:
    #     :param t2:
    #     :param e:
    #     :param k:
    #     :param t1M:
    #     :param t1m:
    #     """
    #
    #     TUnit.__init__(self, th, name=name, description=description)
    #
    #     if w1 is None:
    #         self.addquantity(name='w1', unit='s-1', opt=True, vlen=th.len)
    #     else:
    #         self.addquantity(name='w1', unit='s-1', opt=False, value=w1)
    #
    #     if w2 is None:
    #         self.addquantity(name='w2', unit='s-1', opt=True, vlen=th.len)
    #     else:
    #         self.addquantity(name='w2', unit='s-1', opt=False, value=w2)
    #
    #     if t1 is None:
    #         self.addquantity(name='t1', unit='N.m', opt=True, vlen=th.len)
    #     else:
    #         self.addquantity(name='t1', unit='N.m', opt=False, value=t1)
    #
    #     if t2 is None:
    #         self.addquantity(name='t2', unit='N.m', opt=True, vlen=th.len)
    #     else:
    #         self.addquantity(name='t2', unit='N.m', opt=False, value=t2)
    #
    #     self.addquantity(name='t1m', unit='N.m', opt=False)
    #     self.addquantity(name='t1M', unit='N.m', opt=False)
    #
    #     self.addquantity(name='q0', description='usfull variable', lb=0, opt=True, vlen=th.len)
    #     self.addquantity(name='q1', description='usfull variable', lb=0, opt=True, vlen=th.len)
    #     self.addquantity(name='q2', description='usfull variable', lb=0, opt=True, vlen=th.len)
    #     self.addquantity(name='u', description='t1 positif', vtype='B', opt=True, vlen=th.len)
    #     self.addquantity(name='e', opt=False, value=e)
    #     self.addquantity(name='k', opt=False, value=k)
    #
    #     exp = """k*w2[t] == w1[t] for t in T
    #     t1m*q0[t] +             t1M*q2[t] == t1[t]    for t in T
    #     1/(e*k)*t1m*q0[t] + e/k*t1M*q2[t] == t2[t]    for t in T
    #     q0[t] + q1[t] >= u[t]        for t in T
    #     q1[t] + q2[t] >= (1-u[t])    for t in T
    #     q0[t] + q1[t] + q2[t] == 1   for t in T"""
    #
    #     self.addconst(name='cst1', exp=exp)


# class Red2(TUnit):
#     def __init__(self, th, name='RED0',
#                  description='Gear reduction, witime_horizon factor k and efficiency e',
#                  w1=None, w2=None, t1=None, t2=None, e=1., k=1.):
#
#         """
#
#         :param MG:
#         :param name:
#         :param description:
#         :param w1:
#         :param w2:
#         :param t1:
#         :param t2:
#         :param e:
#         :param k:
#         """
#         TUnit.__init__(self, th, name=name, description=description)
#
#         if w1 is None:
#             self.addquantity(name='w1', unit='s-1', opt=True, vlen=th.len)
#         else:
#             self.addquantity(name='w1', unit='s-1',  opt=False, value=w1)
#
#         if w2 is None:
#             self.addquantity(name='w2', unit='s-1', opt=True, vlen=th.len)
#         else:
#             self.addquantity(name='w2', unit='s-1', opt=False, value=w2)
#
#         if t1 is None:
#             self.addquantity(name='t1', unit='N.m', opt=True, vlen=th.len)
#         else:
#             self.addquantity(name='t1', unit='N.m', opt=False, value=t1)
#
#         if t2 is None:
#             self.addquantity(name='t2', unit='N.m', opt=True, vlen=th.len)
#         else:
#             self.addquantity(name='t2', unit='N.m', opt=False, value=t2)
#
#         self.addquantity(name='q0', description='usefull variable', lb=0, opt=True, vlen=th.len)
#         self.addquantity(name='q1', description='usefull variable', lb=0, opt=True, vlen=th.len)
#         self.addquantity(name='e', opt=False, value=e)
#         self.addquantity(name='k', opt=False, value=k)
#         exp1 = """k*w2[t] == w1[t] for t in T
#         q1[t] - q0[t] == t1[t] for t in T
#          1/(e*k)*q0[t] + e/k*q1[t] == t2[t] for t in T
#         q0[t] + q1[t] <= t1[t] for t in T"""
#
#         self.addconst(name='cst4', exp=exp1)
