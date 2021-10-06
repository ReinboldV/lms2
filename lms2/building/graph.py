import networkx as nx

__all__ = ['build_dummy_1zone_graph', 'build_2zone_graph']

model_types = ['SFH_D_1_2zone_TAB', 'SFH_D_1_2zone_REF1', 'SFH_D_1_2zone_REF2', 'SFH_D_2_2zone_TAB',
               'SFH_D_2_2zone_REF1', 'SFH_D_2_2zone_REF2', 'SFH_D_3_2zone_TAB', 'SFH_D_3_2zone_REF1',
               'SFH_D_3_2zone_REF2', 'SFH_D_4_2zone_TAB', 'SFH_D_4_2zone_REF1', 'SFH_D_4_2zone_REF2',
               'SFH_D_5_2zone_TAB', 'SFH_D_5_ins_TAB', 'SFH_SD_1_2zone_TAB', 'SFH_SD_1_2zone_REF1',
               'SFH_SD_1_2zone_REF2', 'SFH_SD_2_2zone_TAB', 'SFH_SD_2_2zone_REF1', 'SFH_SD_2_2zone_REF2',
               'SFH_SD_3_2zone_TAB', 'SFH_SD_3_2zone_REF1', 'SFH_SD_3_2zone_REF2', 'SFH_SD_4_2zone_TAB',
               'SFH_SD_4_2zone_REF1', 'SFH_SD_4_2zone_REF2', 'SFH_SD_5_TAB', 'SFH_SD_5_Ins_TAB',
               'SFH_T_1_2zone_TAB', 'SFH_T_1_2zone_REF1', 'SFH_T_1_2zone_REF2', 'SFH_T_2_2zone_TAB',
               'SFH_T_2_2zone_REF1', 'SFH_T_2_2zone_REF2', 'SFH_T_3_2zone_TAB', 'SFH_T_3_2zone_REF1',
               'SFH_T_3_2zone_REF2', 'SFH_T_4_2zone_TAB', 'SFH_T_4_2zone_REF1', 'SFH_T_4_2zone_REF2',
               'SFH_T_5_TAB', 'SFH_T_5_ins_TAB']


def build_dummy_1zone_graph(**kwargs):
    """
    Dummy thermal model for test and debbug

    Considers 1 internal node, 1 wall, 1 external fixed temperature

    :param bui_param:
    :return:
    """
    CiD = kwargs.pop('CiD', 2000000)
    CwD = kwargs.pop('CwD', 90000000)
    UwD = kwargs.pop('UwD', 1200)
    hwD = kwargs.pop('hwD', 900)

    G = nx.DiGraph()

    # Day zone
    G.add_node('TiD',
               C=CiD,
               T_init=10,
               Q_control={'Q_heat_D': 1})

    G.add_node('TwD',
               T_init=10,
               C=CwD)

    # External temperatures
    G.add_node('Te',
               T_fix='Te')

    G.add_edge('Te', 'TwD', U=UwD)
    G.add_edge('TwD', 'TiD', U=hwD)

    return G


def build_2zone_graph(bp):
    """
    Creates a directed graph of a RC 2 zone model using the building parameters stored in `bui_param`

    :param bp: building parameters

    :return:
    """
    G = nx.DiGraph()
    t_in_D = 20
    t_in_N = 15

    # Day zone
    G.add_node('TiD',
               T_init=t_in_D,
               C=bp['CiD'],
               Q_fix={'Q_sol_N': bp['abs3ND'], 'Q_sol_E': bp['abs3ED'], 'Q_sol_S': bp['abs3SD'],
                      'Q_sol_W': bp['abs3WD'], 'Q_int_D': bp['f3D']},
               Q_control={'Q_heat_D': bp['f3D']},
               state_type='day')
    G.add_node('TflD',
               T_init=t_in_D,
               C=bp['CflD'],
               Q_fix={'Q_sol_N': bp['abs4ND'], 'Q_sol_E': bp['abs4ED'], 'Q_sol_S': bp['abs4SD'],
                      'Q_sol_W': bp['abs4WD'], 'Q_int_D': bp['f4D']},
               Q_control={'Q_heat_D': bp['f4D']})
    G.add_node('TwiD',
               T_init=t_in_D,
               C=bp['CwiD'],
               Q_fix={'Q_sol_N': bp['abs2ND'], 'Q_sol_E': bp['abs2ED'], 'Q_sol_S': bp['abs2SD'],
                      'Q_sol_W': bp['abs2WD'], 'Q_int_D': bp['f2D']},
               Q_control={'Q_heat_D': bp['f2D']})
    G.add_node('TwD',
               T_init=t_in_D,
               C=bp['CwD'],
               Q_fix={'Q_sol_N': bp['abs1ND'], 'Q_sol_E': bp['abs1ED'], 'Q_sol_S': bp['abs1SD'],
                      'Q_sol_W': bp['abs1WD'], 'Q_int_D': bp['f1D']},
               Q_control={'Q_heat_D': bp['f1D']})

    # Internal floor
    G.add_node('TfiD',
               T_init=t_in_D,
               C=bp['CfiD'],
               Q_fix={'Q_sol_N': bp['abs5ND'], 'Q_sol_E': bp['abs5ED'], 'Q_sol_S': bp['abs5SD'],
                      'Q_sol_W': bp['abs5WD'], 'Q_int_D': bp['f5D']},
               Q_control={'Q_heat_D': bp['f5D']})
    G.add_node('TfiN',
               T_init=t_in_N,
               C=bp['CfiD'],
               Q_fix={'Q_sol_N': bp['abs5NN'], 'Q_sol_E': bp['abs5EN'], 'Q_sol_S': bp['abs5SN'],
                      'Q_sol_W': bp['abs5WN'], 'Q_int_N': bp['f5N']},
               Q_control={'Q_heat_N': bp['f5N']})

    # Night zone
    G.add_node('TiN',
               T_init=t_in_N,
               C=bp['CiN'],
               Q_fix={'Q_sol_N': bp['abs3NN'], 'Q_sol_E': bp['abs3EN'], 'Q_sol_S': bp['abs3SN'],
                      'Q_sol_W': bp['abs3WN'], 'Q_int_N': bp['f3N']},
               Q_control={'Q_heat_N': bp['f3N']},
               state_type='night')
    G.add_node('TwiN',
               C=bp['CwiN'],
               T_init=t_in_N,
               Q_fix={'Q_sol_N': bp['abs2NN'], 'Q_sol_E': bp['abs2EN'], 'Q_sol_S': bp['abs2SN'],
                      'Q_sol_W': bp['abs2WN'], 'Q_int_N': bp['f2N']},
               Q_control={'Q_heat_N': bp['f2N']})
    G.add_node('TwN',
               C=bp['CwN'],
               T_init=t_in_N,
               Q_fix={'Q_sol_N': bp['abs1NN'], 'Q_sol_E': bp['abs1EN'], 'Q_sol_S': bp['abs1SN'],
                      'Q_sol_W': bp['abs1WN'], 'Q_int_N': bp['f1N']},
               Q_control={'Q_heat_N': bp['f1N']})

    # External temperatures
    G.add_node('Te',
               T_fix='Te')

    G.add_node('Tg',
               T_fix='Tg')

    # Hot water storage tank
    G.add_node('T_HW',
               T_init=55,
               Flow_HW='Flow_HW',
               Q_control='Q_heat_HW')

    # Connections
    G.add_edge('Te', 'TwD', U=bp['UwD'])
    G.add_edge('Te', 'TiD', U=bp['infD'])
    G.add_edge('TwD', 'TiD', U=bp['hwD'])
    G.add_edge('TiD', 'TflD', U=bp['hflD'])
    G.add_edge('TflD', 'Tg', U=bp['UflD'])

    G.add_edge('TiD', 'TwiD', U=bp['hwiD'])
    G.add_edge('TiD', 'TfiD', U=bp['UfDN'])
    G.add_edge('TfiD', 'TfiN', U=bp['UfND'])

    G.add_edge('TfiN', 'TiN', U=bp['UfND'])
    G.add_edge('TiN', 'TwiN', U=bp['hwiN'])
    G.add_edge('TiN', 'TwN', U=bp['hwN'])
    G.add_edge('TwN', 'Te', U=bp['UwN'])
    G.add_edge('TiN', 'Te', U=bp['infN'])

    return G



