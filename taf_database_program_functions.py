import json
apt_groups = {
    #g_groups - list of aports related to destination airport
        'gEPWAb':['EPWA', 'EPLL', 'EPKT', 'EPWR', 'EPPO', 'EPGD'],
        'gEPWA': ['EPWA','EPLL','EPKT','EPWR','EPPO','EPGD'],
        'gEPWAf':['EPWA','EPLL','EPKT','EPWR','EPPO','EPGD','eplb','epkk','eprz','lkpr','epsc','epby','epmo'],
        'gEGGW': ['eggw','egss','egbb','egcn','egcc'],
        'gEBCI': ['ebci', 'ebbr', 'lfqq', 'eddk', 'eheh', 'eblg'],
        'gEYKA': ['eyka', 'eyvi', 'eypa', 'evra'],
        'gENBR': ['enbr', 'ento', 'enzv', 'engm', 'essa'],
        'gLIME': ['lime', 'liml', 'limc' ,'lipx' ,'limf' ,'lipz' ,'liph', 'lipe','lsgg','lszh'],
        'gGCTS': ['gcts', 'gclp', 'gcxo', 'gcrr', 'gcfv'],
        'gLEMD': ['lemd', 'lebl', 'levc', 'lezg', 'lemg',],
        'gLIRN': ['lirn', 'libd', 'libp', 'lirf', 'lira',],
        'gESKN': ['eskn', 'essa', 'ento','engm'],
        'gEGPG': ['egph', 'egpf', 'eggp'],
        'gLIRF': ['lirf', 'lira', 'lirn', 'libp', 'libd'],
        'gESMS': ['esms', 'ekch', 'esgg', 'epgd', 'engm'],
        'gESGG': ['esgg', 'esms', 'eskn', 'essa', 'ekch'],
        'gEHEH': ['eheh', 'ebci', 'ehbk', 'edlv', 'edlp', 'eddk'],
        'gBIKF': ['bikf', 'bieg', 'egpd', 'egpf', 'egpk', 'enzv', 'enbr'],
        'gBKPR': ['bkpr', 'lwsk', 'lbsf', 'lgts'],
        'gLFSB': ['lfsb', 'lszh', 'edny', 'lsgg', 'edds'],


    }

def select_airports__use_apts_in_code():
    requested_airports_taf = 'gEPWAb LEBL'  # NO COMMAs !! - just SPACE
    print(requested_airports_taf)
    return requested_airports_taf

def create_list_of_apts_to_get_TAF__convertg_group_into_list(apt_groups, requested_airports_taf):
    """ - create list of apts of which TAF will be downloaded
        - converts g_groups to list of apts"""

    # make g_group_name recognizable as a group and not as an apt name
    g_string_apts = []
    for g_group_name in apt_groups.keys():
        g_string_apts.append(g_group_name)

    # combining g_grup airports and individual airports into one list
    taf_list = []
    for string in requested_airports_taf:
        g_string_true_flag = False

        for g_apt in g_string_apts:
            if string == g_apt:
                g_string_true_flag = True
                taf_list.append(apt_groups[g_apt])

                if not g_string_true_flag:
                    taf_list.append(string)
        if not g_string_true_flag:
            taf_list.append(string)

    return taf_list

def load_and_dump_g_groups_apts_data_from_taf_database_program_functions():
    filename = 'data/g_groups_apts_db.json'
    with open(filename, 'w') as f_obj:
        json.dump(apt_groups, f_obj, indent=2)
