from settings import Settings
settings = Settings()

import program_functions as pf

def TAF_decoder_function(TAF, my_day=settings.day, my_time=settings.hour,
                             significant_start_hour=settings.significant_start_hour,
                             significant_end_hour=settings.significant_end_hour,
                             significant_start_day=settings.significant_start_day,
                             significant_end_day=settings.significant_end_day,
                             significant_range= settings.significant_range,
                             significant_range_active=settings.significant_range_active,
                             cancel_out_of_range_msg=settings.cancel_out_of_range_msg,
                             print_type = settings.print_type,
                             print_time_group = settings.print_time_group,

):
    """importing settings form settings.py"""
    #significant_range = settings.significant_range
    becmg_cancelling_wind = settings.becmg_cancelling_wind
    becmg_cancelling_vis = settings.becmg_cancelling_vis
    becmg_cancelling_weather = settings.becmg_cancelling_weather
    becmg_cancelling_clouds = settings.becmg_cancelling_clouds
    becmg_time_group_coloring = settings.becmg_time_group_coloring
    fm_canceling = settings.fm_canceling
    print_ranges_legend = settings.print_ranges_legend
    print_TAF_without_colouring = settings.print_TAF_without_colouring
    printing_active = settings.printing_active
    print_colouring_logic = settings.print_colouring_logic
    no_publication_time_not_an_error= settings.no_publication_time_not_an_error

    gap_symbol = settings.gap_symbol

    def ref(i=''):
        if printing_active:
            ref = ("\t\n# " + str(i) + " #")
            print("\033[94m {}\033[00m".format(ref))

    def prPurple(skk):
        return "\033[95m{}\033[00m".format(skk)

    def prCyan(skk):
        return "\033[96m{}\033[00m".format(skk)

    def prGreen(skk):
        return "\033[92m{}\033[00m".format(skk)

    # def prLightGray(skk):
    #     return "\033[57m{}\033[00m".format(skk)

    def prLightGray(skk):
        return "\033[1;90;40m" + str(skk)

    def prYellow(skk):
        return "\033[93m{}\033[00m".format(skk)

    def prUnderlined(skk):
        return ('\x1b[4;30;48m{}\x1b[0m'.format(skk))

    def prBoxed(skk):
        return ('\x1b[52;30;48m{}\x1b[0m'.format(skk))

    def TEMPO_color(string):
        # string = prCyan(string)
        string = prGreen(string)
        return string

    def BECMG_color(string):
        string = prGreen(string)
        # string = prPurple(string)
        return string

    def BECMG_non_significant_color(string):
        string = BECMG_color(string)
        # string = prGreen(string)
        return string

    def grayed_area_left(string):
        string = prLightGray(string)
        return string

    def grayed_area_right(string):
        string = prLightGray(string)
        return string

    def error_added(string):
        """error added at the end to final string"""
        string = prBoxed(string)
        return string


    def add_to_dict_gr_data(lista,key):
        """ adds data to gr_data list of dictionaries, name of KEY has to be given"""
        if len(lista) == len(gr_data):
            for n in range(len(lista)):
                gr_data[n][key] = lista[n]
        else:
            print(
                '\nERROR\n(1)Lenght of list do not match. Difference: ' + str(
                    len(gr_data) - len(lista)))
            exit()

    def print_dicts(lista, key):  # list is:
        # gr_data or time_gr_data, prints from selceted KEY
        print('')
        for n in range(len(lista)):
            print(key + ':\t\t' + str(lista[n][key]))

    def add_to_dict_TIME_gr_data(lista,
                                 key):  # adds data to gr_data list of dictionaries, name of KEY has to be given
        if len(lista) == len(time_gr_data):
            for n in range(len(lista)):
                time_gr_data[n][key] = lista[n]
        else:
            print('\nERROR\n(2)Lenght of list do not match. Difference: '
                  + str(len(time_gr_data) - len(lista)))
            exit()

    def string_to_list(string):
        l = []
        for s in string:
            l.append(s)
        return l

    # END OF INPUTS ----------


    # -----------------------------

    TAF_split = TAF.split(' ')
    """ spliiting TAF into words"""
    if printing_active:
        print('\n', prBoxed('TAF_split'), TAF_split)
    # searching for time groups which divide TAF into groups containing time range
    time_string = [0]
    """# Adding START index. 
    Each TAF part has to have beginning and end and . 
    0-2, 2-9,9-18 ect             """

    for n in range(len(TAF_split)):  # searching index of '/'
        if TAF_split[n].count('/') == 1 \
                and TAF_split[n][:4].isdigit() and TAF_split[n][5:].isdigit() \
                and len(TAF_split[n]) == 9:
            time_string.append(n)
        if TAF_split[n].count('FM') == 1:
            if len(TAF_split[n]) == 8 \
                    and TAF_split[n][2:].isdigit() \
                    and time_string.append(n):
                time_string.append(n)

    """seaching dash in words to group of words into time groups """

    time_string.append(len(TAF_split))  # END index-- ...9-18,18-END index
    if printing_active:
        print('\n', prBoxed('time_string1:'), time_string)

    time_string_uncorrected = time_string[
                              :]  # DO NOT REMOVE this - coping a list to use it below

    type_of_group = []
    error_type_of_group = []
    for n in range(
            len(time_string) - 1):  # -1 here prevents from creating fake group
        # time_string is one item longer than required
        """searching if word one before word containing dash has TEMPO or BECMG, 
        if there is TEMPO, than another one word is being search for containing PROB30/4- 
        PROB30/40. THe index of dash is being corrected to create correct ime group
        """
        n_minus1 = time_string[n] - 1
        n_minus2 = time_string[n] - 2

        zero_before = time_string[n]
        one_before = (TAF_split[n_minus1])
        two_before = (TAF_split[n_minus2])

        if one_before == 'BECMG' or one_before == 'PROB30' or one_before == \
                'PROB40':
            time_string[n] = time_string[n] - 1
        elif one_before == 'TEMPO':
            if two_before == 'PROB30' or two_before == 'PROB40':
                time_string[n] = time_string[n] - 2
            else:
                time_string[n] = time_string[n] - 1

    if printing_active:
        print('', prBoxed('time_string2:'), time_string)
    ref('Dividing TAF into time groups')

    groups = []
    for n in range(0, len(time_string) - 1):  # VERY IMPORTANT
        group = TAF_split[time_string[n]: time_string[n + 1]]
        groups.append(group)
    if printing_active:
        print(prBoxed('groups: '), groups)

    # creating list of dictionaries
    gr_data = []
    for n in range(len(groups)):
        gr_data.append({})

    ref('AAA')
    add_to_dict_gr_data(groups, 'TAF_slice')
    if printing_active:
        print(prBoxed('gr_data')), print_dicts(gr_data, 'TAF_slice')

    # function for easier printing of each line of sliced TAF

    formatted_TAF_slices = groups[:]
    for n in range(len(groups)):
        """ adding gap in front of time group strings to allign them when 
        printing all TAF"""

        points = []
        for g in groups[n]:
            if g == 'TAF':
                points.append(4)
            if g == 'TEMPO' or g == 'BECMG':
                points.append(6)
            if g == 'PROB30' or g == 'PROB40':
                points.append(7)

        formatted_TAF_slices[n].insert(0, ' ' * (13 - sum(points)))

    add_to_dict_gr_data(formatted_TAF_slices, 'formatted_TAF_slices')
    ref('BBB')
    if printing_active:
        print(prBoxed('gr_data')), print_dicts(gr_data, 'formatted_TAF_slices')

    # creates groups_strings --> that is list of strings containg each group separated by TEMPO, BCMG, PROB30/40
    groups_strings = []
    for n in range(len(groups)):
        s = ""
        for t in groups[n]:
            s += t + ' '
        groups_strings.append(s)

    add_to_dict_gr_data(groups_strings, 'groups_strings')
    ref('CCC')
    if printing_active:
        print(prBoxed('gr_data')), print_dicts(gr_data, 'groups_strings')

    ref('DDD')
    if printing_active:
        print(prBoxed('time_string_uncorrected'), time_string_uncorrected)
    # time_string_uncorrected - first and last lelemt removed to work correctly')
    del time_string_uncorrected[
        0]  ### DO NOT REMOVE this line - very important
    del time_string_uncorrected[
        -1]  ### DO NOT REMOVE this line - very important
    if printing_active:
        print(prBoxed('time_string_uncorrected'), '  ',
              time_string_uncorrected,
              '    -corrected')

    time_gr_data = []  # creating time_gr_data - this is gr_data MINUS first slice
    for n in range(len(time_string_uncorrected)):
        time_gr_data.append({})

    ref('EEE')
    if printing_active:
        print(prBoxed('time_gr_data'))
    if printing_active:
        print(prBoxed('time_gr_data')), pf.print_list(time_gr_data)

    ref(1)
    if printing_active:
        add_to_dict_TIME_gr_data(time_string_uncorrected,
                                 'time_string corrected for TEMPO and BECMG')

    if printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'time_string '
                                                    'corrected for TEMPO and BECMG')

    ref(2)
    add_to_dict_TIME_gr_data(time_string_uncorrected,
                             'time_string_END_uncorrected')  ### HERE
    if printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'time_string_END_uncorrected')

    time_group_list = []
    for n in range(len(time_string_uncorrected)):
        """ this part extracts string containing time and date of each TAF time 
        group, lets call it a dash_word. It is extracted fotm time_gr_data"""
        lista = TAF_split[time_string_uncorrected[n]]
        time_group_list.append(lista)
    ref(3)
    add_to_dict_TIME_gr_data(time_group_list, 'time_group_list')
    if printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'time_group_list')

    ref(4)

    def creating_start_end_times_dates():
        # ref('extracting time range in hours')
        # ref('[start_date, start_hour, end_date,end_hour, diff]')
        hours_list = []
        for n in range(len(time_group_list)):
            fm_in = False
            if 'FM' in time_group_list[n]:
                fm_in = True
            if printing_active:
                print(fm_in)

            sliced_word = string_to_list(time_group_list[n])
            if printing_active:
                print(sliced_word)
            if fm_in:
                fm_date = int(sliced_word[2] + sliced_word[3])
                fm_hour = int(sliced_word[4] + sliced_word[5])
                fm_minute = int(sliced_word[6] + sliced_word[7])

                start_date = fm_date
                start_hour = fm_hour - 1
                end_date = fm_date
                end_hour = fm_hour + 1
                # diff = end_hour - start_hour
                diff = 0
                hours = [start_date, start_hour, end_date, end_hour, diff]
                hours_list.append(hours)

            elif not fm_in:
                dash_word = sliced_word
                dash_location = dash_word.index('/')
                check_if_numbers = \
                    [dash_word[dash_location - 2],
                     dash_word[dash_location - 1],
                     dash_word[dash_location + 3],
                     dash_word[dash_location + 4],
                     dash_word[dash_location - 4],
                     dash_word[dash_location - 3],
                     dash_word[dash_location + 1],
                     dash_word[dash_location + 2]]

                digit = []
                for dash_surround_symbol in check_if_numbers:
                    if not dash_surround_symbol.isdigit():
                        digit.append(1)
                if printing_active:
                    print('digit', sum(digit))
                if sum(digit) == 0:

                    start = int(str(dash_word[dash_location - 2]) + str(
                        dash_word[dash_location - 1]))
                    # HOURS  of beginning
                    end = int(str(dash_word[dash_location + 3]) + str(
                        dash_word[dash_location + 4]))  #
                    # HOURS of end

                    left = int(str(dash_word[dash_location - 4]) + str(
                        dash_word[dash_location - 3]))  #
                    # DATE of beginning
                    right = int(str(dash_word[dash_location + 1]) + str(
                        dash_word[dash_location + 2]))  #
                    # DATE of end
                    end24 = end + 24
                    end48 = end + 48

                    if ((left == 28 or
                         left == 29 or
                         left == 30 or
                         left == 31) and right == 2) \
                            or ((left == 26 or
                                 left == 27 or
                                 left == 28 or
                                 left == 29) and right == left + 2)\
                            or ((left == 27 or
                                 left == 28 or
                                 left == 29 or
                                 left == 30) and right == 1):
                        diff = end48 - start

                    elif ((left == 28 or
                         left == 29 or
                         left == 30 or
                         left == 31) and right == 1) \
                            or ((left == 27 or
                                 left == 28 or
                                 left == 29 or
                                 left == 30) and right == left + 1):
                        diff = end24 - start
                    # elif (left == 28 or left == 29 or left == 30 or left == 31) and right != 1:
                    #   diff = 'err'
                    elif    (left == 28 and right == 28) or \
                            (left == 29 and right == 29) or \
                            (left == 30 and right == 30) or \
                            (left == 31 and right == 31):
                        diff = end - start
                    elif (left >= 1 and left <= 27) and right == left:
                        diff = end - start
                    elif (left >= 1 and left <= 26) and right == left + 1:
                        diff = end24 - start
                    elif (left >= 1 and left <= 25) and right == left + 2:
                        diff = end48 - start

                    elif (left >= 1 and left <= 24) and (
                            right != left or right != left + 1 or right != left + 2 ):
                        print('error! err2')
                        diff = 'err2'
                    else:
                        diff = 'else err'

                    start_date = left
                    end_date = right
                    start_hour = start
                    end_hour = end

                    hours = [start_date, start_hour, end_date, end_hour, diff]
                    hours_list.append(hours)
            else:
                print('search THTHTHTHT in code')
        add_to_dict_TIME_gr_data(hours_list, 'hours_list')

    creating_start_end_times_dates()
    ref('GGG')
    if printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data, 'hours_list')

    def creating_type_of_group():
        # storing data what type of weather group each string is
        # TEMPO or BECMG or PROB30/40
        type_of_group = []
        for n in range(len(time_string_uncorrected)):
            n_zero = time_string_uncorrected[n]
            n_minus1 = time_string_uncorrected[n] - 1
            n_minus2 = time_string_uncorrected[n] - 2
            zero = TAF_split[n_zero]
            one_before = (TAF_split[n_minus1])
            two_before = (TAF_split[n_minus2])
            if (len(one_before) == 4 and one_before.isalpha()):
                station_name.append(one_before)
            elif (len(two_before) == 4 and two_before.isalpha()):
                station_name.append(two_before)
            if 'FM' in zero:
                type_of_group.append('FM')
            elif one_before == 'BECMG':
                type_of_group.append('B')
            elif one_before == 'PROB30':
                type_of_group.append('P30')
            elif one_before == 'PROB40':
                type_of_group.append('P40')
            elif one_before == 'TEMPO':
                if two_before == 'PROB30':
                    type_of_group.append('P30 T')
                elif two_before == 'PROB40':
                    type_of_group.append('P40 T')
                else:
                    type_of_group.append('T')
            elif no_publication_time_not_an_error == True \
                    and (len(one_before) == 4 and one_before.isalpha()):
                type_of_group.append('Initial')
            elif no_publication_time_not_an_error == False \
                    and 'Z' in one_before and one_before.isalpha() == False:
                type_of_group.append('Initial')
            elif 'Z' in one_before and one_before.isalpha() == False :
                type_of_group.append('Initial')
            else:
                type_of_group.append('error type')

        add_to_dict_TIME_gr_data(type_of_group, "type_of_group")

    station_name =[] # do not remove!
    creating_type_of_group()

    ref('HHHH')
    if printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'type_of_group')

    error_found = []
    score = []
    reference = []

    def creating_weather_data_list():
        # creating weather_data list - list which stores weather conditions
        weather_data = []
        Ts1 = gr_data[1]['TAF_slice']

        type_of_group.insert(0,
                             'none')  ## adding none to match number of dictionaries
        for n in range(len(gr_data)):
            """this part extracts data like wind, vis, weather and clouds from 
            time groups"""
            time_slice = gr_data[n]['TAF_slice']
            weather_data_dict = {}
            weather_data_dict['n'] = {n}
            weather_data_dict['type'] = []
            weather_data_dict['wind'] = []
            weather_data_dict['vis'] = []
            weather_data_dict['weather'] = []
            weather_data_dict['clouds'] = []
            weather_data_dict['||   m'] = {n}

            # weather_data_dict['type'] = type_of_group[n]
            l = 0
            for p in time_slice :
                reference.append([n, l])  # line eqired for check of errors
                if 'SM' in p :
                    weather_data_dict['vis'].append(p)
                    score.append([n, l])

                elif len(p) == 4:
                    vis_list = string_to_list(p)
                    test = []
                    for s in vis_list:
                        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
                                   '0']
                        if s in numbers: test.append('p')
                    if test == ['p', 'p', 'p', 'p']:
                        if True:
                            weather_data_dict['vis'].append(p)
                            score.append([n, l])

                elif 'CAVOK' in p:
                    weather_data_dict['vis'].append(p)
                    score.append([n, l])

                wind = ['KT', 'MPS', 'CALM', 'VRB']
                for w in wind:

                    if w in p:
                        if printing_active:
                            print(p, 'wwwwwwwwwwwww')
                        weather_data_dict['wind'].append(p)
                        score.append([n, l])
                clouds = ['SKC', 'NSC', 'VV', 'FEW', 'SCT', 'BKN', 'OVC']

                for c in clouds:
                    if c in p:
                        weather_data_dict['clouds'].append(p)
                        score.append([n, l])

                if 'TX' in p:
                    weather_data_dict['temp_max'] = p
                    score.append([n, l])
                if 'TN' in p:
                    weather_data_dict['temp_min'] = p
                    score.append([n, l])

                wx = ['BC', 'BL', 'DR', 'FZ', 'MI', 'PR', 'SH', 'TS', 'DZ',
                      'GR', 'IC', 'GS', 'PL', 'RA', 'SN','SG', 'BR', 'DU', 'FG',
                      'FU', 'HZ', 'SA', 'DS', 'FC', 'FU', 'PO', 'SQ', 'SS',
                      'VA', 'UP', 'NSW']

                for w in wx:
                    if w == 'PO':
                        if p == 'TEMPO': pass
                    elif w == 'PR':
                        if p == 'PROB30': pass
                    elif w in p:
                        if p not in weather_data_dict['weather']:
                            weather_data_dict['weather'].append(p)
                            score.append([n, l])
                else:
                    """ this part is responsible for catching erroneous data or 
                    values which has were missed from decoding. Without this any of
                    erroneous data wont appear in final TAF ."""
                    propper_words = ['TEMPO', 'PROB30', 'BECMG', 'PROB40',
                                     'TAF',
                                     'COR', 'AMD']
                    gaps = []
                    for nn in range(1, 15):
                        gaps.append(' ' * nn)
                    icao_code = False
                    if len(p) == 4 and p.isalpha() and n == 0: # ICAO code can be only in first line
                        icao_code = True
                        weather_data_dict['wind'].append(p)

                    dash_number = p.count('/')
                    zulu_number = p.count('Z')
                    fm_present = p.count('FM')
                    if p in propper_words \
                            or p in gaps \
                            or dash_number == 1 \
                            or zulu_number == 1 \
                            or fm_present == 1 \
                            or p == '' \
                            or icao_code:
                        score.append([n, l])
                l += 1

            weather_data.append(weather_data_dict)

        return weather_data
        # make loop until dict full of weather
    weather_data = creating_weather_data_list()

    ref('III')
    if printing_active:
        print(prBoxed('weather_data'))
        pf.print_list(weather_data)

    """ part responsible for collecting above error data and showing which part 
    is erroneus 
    """
    while score:
        point = score.pop()
        if point in reference:
            reference.remove(point)
    ref('JJJ')
    if printing_active:
        print(reference)
        print('vvvvvv')
    m = 0
    for i in reference:
        n = i[0]
        p = i[1]
        error = (gr_data[n]['TAF_slice'][p])
        reference[m].append(error)
        m += 1
    error_found = reference

    def transferring_group_type_from_time_gr_data_to_weather_data():
        ref('Transferring group type from time_gr_data to weather_data')
        typ = ['none']
        for n in range(len(time_gr_data)):
            gr_type = time_gr_data[n]['type_of_group']
            typ.append(gr_type)
        for n in range(len(typ)):
            weather_data[n]['type'] = typ[n]

    transferring_group_type_from_time_gr_data_to_weather_data()
    ref('KKK')
    if printing_active:
        print(prBoxed('weather_data')), pf.print_list(weather_data)

    # searching for slice number containing BECMG or Initial in weather data:
    becmg_list = []
    for n in range(len(weather_data)):
        typ = ['B', 'Initial', 'FM']
        if weather_data[n]['type'] in typ:
            becmg_list.append(n)
    ref('LLL')
    if printing_active:
        print(prBoxed('becmg_list')), print(becmg_list)

    def print_keys():
        ref('---data groups[1]---')
        if len(time_gr_data) > 1:
            print('\ntime_gr_data[1]')
            for k, v in time_gr_data[1].items():
                print(f'{k} : {v}')

            print('\n---gr_data[1]---')
            for k, v in gr_data[1].items():
                print(f'{k} : {v}')

            print('\n---weather_data[1]---')
            for k, v in weather_data[1].items():
                print(f'{k} : {v}')

        elif len(time_gr_data) == 1:
            print('\ntime_gr_data[1]')
            print(time_gr_data)
            # for k, v in time_gr_data.items():
            #     print(f'{k} : {v}')

            print('\n---gr_data[1]---')
            print(gr_data)
            # for k, v in gr_data.items():
            #     print(f'{k} : {v}')

            print('\n---weather_data[1]---')
            print(weather_data)
            # for k, v in weather_data.items():
            #     print(f'{k} : {v}')

    if printing_active:
        print_keys()

    def add_to_dict_weather_data(lista,
                                 key):  # adds data to gr_data list of dictionaries, name of KEY has to be given
        if len(lista) == len(weather_data):
            for n in range(len(lista)):
                weather_data[n][key] = lista[n]
        else:
            print('\nERROR\n(3)Lenght of list do not match. Difference: '
                  + str(len(weather_data) - len(lista)))
            exit()

    # creating time taf slices time ranges
    time_range = [['x',
                   'x']]  # adding none item to match time_gr_data len to weather_data len
    for n in range(len(time_gr_data)):
        tg_hl = time_gr_data[n]['hours_list']
        ref_date = time_gr_data[0]['hours_list'][0]
        next_day = [(ref_date + 1), 1]
        range_start = 0  # this is to avoid yellow mark, range_start is only defined below as if statement, so without this line it is cause of caution message
        if tg_hl[0] == ref_date:
            # comparing if date og group is the same as date of start of TAF validity
            range_start = tg_hl[1]
            range_end = range_start + tg_hl[4]
            time_range.append([range_start, range_end])

        elif tg_hl[0] != ref_date:
            for i in next_day:
                if i == tg_hl[0]:
                    # tg_hl[0] == ref_date + 1:
                    range_start = tg_hl[1] + 24
            range_end = range_start + tg_hl[4]
            time_range.append([range_start, range_end])
    add_to_dict_weather_data(time_range, 'time_range')
    ref('MMM')
    if printing_active:
        print(prBoxed('time_range ADDED')), pf.print_list(weather_data)
        print(prBoxed('time_gr_data'))
        pf.print_list(time_gr_data)

    ref('NNN -- printing time range of BECMG slices')
    for i in becmg_list:
        s_range = weather_data[i]['time_range']
        range_start = s_range[0]
        range_end = s_range[1]
        if printing_active:
            print(range_start, range_end)

    ref('OOO - -creating bcmg_range list')
    bcmg_range = []
    bcmg_range.append(weather_data[1]['time_range'])
    for n in range(len(weather_data)):
        typ = weather_data[n]['type']
        s_range = weather_data[n]['time_range']
        range_start = s_range[0]
        range_end = s_range[1]
        # print(typ,vis,range_start, range_end)

        if typ == 'B' or typ == 'FM': bcmg_range.append(
            [range_start, range_end])
    if printing_active:
        print(prBoxed('bcmg_range - new list')), pf.print_list(bcmg_range)

    import copy
    modified_range = copy.deepcopy(bcmg_range)  # deep copy is necessary to avoid modification of time_range

    ref('RRRRR')
    r = []
    for n in range(len(modified_range)):
        r.append([])
        r[n] = modified_range[n][1]

    first_r = r.pop(0)
    r = r + [first_r]

    for m in range(len(r)):
        modified_range[m][1] = r[m]
    """re0 = modified_range[0][1]
    re1 = modified_range[1][1]
    re2 = modified_range[2][1]
    re3 = modified_range[3][1]

    modified_range[3][1] =re0
    modified_range[0][1] =re1
    modified_range[1][1] =re2
    modified_range[2][1] =re3
    """
    if printing_active:
        print(prBoxed('final modified range')), pf.print_list(modified_range)
    ref('PPP - modified range to overlap')
    if printing_active:
        print(prBoxed('modified range')), pf.print_list(modified_range)

    # adding modified time range
    for n in range(len(weather_data)):
        t_r = weather_data[n]['time_range']
        typ = weather_data[n]['type']
        if typ == 'B' or typ == 'Initial' or typ == 'FM':
            weather_data[n]['modified_range'] = modified_range.pop(0)
        else:
            weather_data[n]['modified_range'] = t_r

    ref('QQQ')
    if printing_active:
        print(prBoxed('weather_data - after adding modified_range')), \
        pf.print_list(weather_data)


#############
    my_time_copy = my_time

    initial_start = weather_data[1]['time_range'][0]
    initial_end = weather_data[1]['time_range'][1] - 1

    significant_time_range_data = pf.getting_significant_time_range(settings,my_day,my_time,
                                                                    initial_end,initial_start,
                                                                    significant_start_day,
                                                                    significant_start_hour,
                                                                    significant_end_day,
                                                                    significant_end_hour,
                                                                    significant_range,
                                                                    significant_range_active,
                                                                    cancel_out_of_range_msg)
    significant_time = significant_time_range_data[0]
    significant_start_hour = significant_time_range_data[1]
    significant_end_hour = significant_time_range_data[2]
##############
    ref('significant_time')
    if printing_active:
        print(significant_time, '\n')

    # adding time_grupe slice to weather data from time_gr_data
    weather_data[0]['time_group'] = []
    for n in range(1, len(weather_data)):
        weather_data[n]['time_group'] = time_gr_data[n - 1]['time_group_list']
    # adding key: group_type_long to weather data
    for n in range(len(weather_data)):
        weather_data[n]['group_type_long'] = ''
        w = weather_data[n]['group_type_long']

        weather_data[n]['gap'] = ''

        d = weather_data[n]['type']
        if d == 'none':
            weather_data[n]['group_type_long'] = ''
        elif d == 'Initial':
            weather_data[n]['group_type_long'] = '_i_'
        elif d == 'B':
            weather_data[n]['group_type_long'] = 'BECMG'
        elif d == 'T':
            weather_data[n]['group_type_long'] = 'TEMPO'
        elif d == 'P40 T':
            weather_data[n]['group_type_long'] = 'PROB40 TEMPO'
        elif d == 'P30 T':
            weather_data[n]['group_type_long'] = 'PROB30 TEMPO'
        elif d == 'P30':
            weather_data[n]['group_type_long'] = 'PROB30'
        elif d == 'P40':
            weather_data[n]['group_type_long'] = 'PROB40'
        elif d == 'FM':
            weather_data[n]['group_type_long'] = '_fm'
            weather_data[n]['time_group'] += ' '
            """ adding space at the end of time_group if group tyep is FM"""
        else:
            weather_data[n]['group_type_long'] = 'ukn_1'

        weather_data[n]['gap'] = gap_symbol * \
                                 (13 - len(weather_data[n]['group_type_long']))

    # printing weather for selected time
    # creating function based on above which creates

    ref('copy of weather data')
    import copy
    weather_data_copy = copy.deepcopy(weather_data)
    if printing_active:
       print(prBoxed('weather_data_copy'))
       pf.print_list(weather_data_copy)


    ref('ppppppp')
    if printing_active:
        pf.print_list(weather_data)
    # testing adding colour to hazardous weather
    becmg_time_group_coloring_list = []

    # colouring each weather item - using colouring.py
    pf.colouring_each_weather_item(becmg_time_group_coloring_list,weather_data)

    ref('--- weather_for_selected_time function -----')

    def weather_for_selected_time_RIGHT(key_):
        wx_key_bcmg = []
        temp_wx_key = []
        temp_range = []

        for n in range(1, len(weather_data)):
            typ = weather_data[n]['type']
            wx_key = weather_data[n][key_]
            t_range = weather_data[n]['modified_range']
            ### ------ TEMPO colouring ------------------------------------------
            significant_time_stack = []
            # creating significant_time_stack to monitor if significant_time
            # encroaches range
            for h in range(t_range[0], t_range[1]):
                if h in significant_time:
                    significant_time_stack.append(1)

            if len(significant_time_stack) > 0:
                if wx_key == []:
                    # print(typ, t_range, 'empty\n')
                    if typ == 'Initial' or typ == 'B' or typ == 'FM':
                        pass
                elif wx_key != []:
                    # print(typ, t_range, wx_key)

                    if typ == 'T' or typ == 'P40 T' or typ == 'P30 T' or typ == 'P40' or typ == 'P30':
                        if key_ == 'clouds' or key_ == 'weather' or key_ == 'vis' or key_ == 'wind':
                            m = 0
                            for i in wx_key:
                                if str('\x1b') not in i[1]:
                                    skk = i[1]
                                    tempo_text = TEMPO_color(skk)
                                    i = tempo_text
                                    weather_data[n][key_][m][1] = i
                                    weather_data[n][key_][m].append('relevant TEMPO')

                                elif str('\x1b') in i[1]:
                                    weather_data[n][key_][m].append('relevant TEMPO')

                                else:
                                    print('error -121 - update code ')
                                    quit()
                                    skk = wx_key
                                    tempo_text = TEMPO_color(skk)
                                    wx_key = tempo_text
                                    weather_data[n][key_] = wx_key
                                m += 1

                    elif typ == 'Initial' or typ == 'B' or typ == 'FM':
                        pass
                    else:
                        print('unknown format\n', wx_key)

                        skk = wx_key
                        tempo_text = TEMPO_color(skk)
                        wx_key = tempo_text
                        weather_data[n][key_] = wx_key

            elif len(significant_time_stack) == 0:
                """ stores n which contain TEMPO and is outside significant time
                - it is stored in tempo_line_n"""
                if typ == 'T' or typ == 'P40 T' or typ == 'P30 T' or typ == 'P40' or typ == 'P30':
                    if key_ == 'wind':
                        tempo_line_n.append(n)
                        #print('llllllllllll---why only wind??')
                        # print('tempo_line_n',tempo_line_n)
                        # m = 0
                        # for i in wx_key:
                        #     weather_data[n][key_][m].append('not-relevant')
                        #     m += 1

                # if typ == 'T' or typ == 'P40 T' or typ == 'P30 T' or typ == 'P40' or typ == 'P30':
                #     if key_ == 'clouds' or key_ == 'weather' or key_ == 'vis':
                #         m = 0
                #         for i in wx_key:
                #             weather_data[n][key_][m].append('not-relevant')
                #             m +=1


        for n in range(1, len(weather_data)):
            # ------Initial, BECMG and FM acolouring -------------------------
            """ colouring fo mentioned groups.. 
            FM cancels out all what was before it - (y/n option)
            BECMG changes only mthose parameters which are mentioned (wind, vis, clouds.. weather (y/n)"""

            typ = weather_data[n]['type']
            wx_key = weather_data[n][key_]
            t_range = weather_data[n]['modified_range']

            """ below part modifies effective ranges based on: 
                - wind,vis,weather, and clouds and
                - depends if one of those parameters had value, 
                if there is no value than it falls back on previous which had value.
                Range i modified accordingly. Very important part!!"""
            if (typ == 'Initial' or typ == 'B' or typ == 'FM') and wx_key != []:
                wx_key_bcmg.append(n)
                temp_range.append([t_range[0], t_range[1]])
                if printing_active:
                    print('filled', 'n=', n, 'typ', typ, key_, wx_key,
                          '\ntemp_range', temp_range, )
                ##print('IF',temp_range)

            elif fm_canceling == 'y' and (
                    typ == 'Initial' or typ == 'B') and wx_key == []:
                """fm canceling engine - description at INPUTS """
                if len(wx_key_bcmg) > 0:
                    temp_range[-1] = \
                        [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                         weather_data[n]['modified_range'][1]]
                    ##print('elif', temp_range)
            elif fm_canceling == 'n' and (
                    typ == 'Initial' or typ == 'B' or typ == 'FM') and wx_key == []:
                if len(wx_key_bcmg) > 0:
                    temp_range[-1] = \
                        [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                         weather_data[n]['modified_range'][1]]

                if printing_active:
                    print('empty', 'n=', n, 'typ', typ, wx_key, '\ntemp_range',
                          temp_range, )

        if printing_active:
            print('')
        for nn in range(0, len(wx_key_bcmg)):
            """part responsible for making temp_ranges 
            - responsible for fallback on previous weather-key to keep contionous range
            - wx_key_bcmg - store n number of line of BECMG and FM plus Initial
            - stack 2 indicates if significant time necroaches on BECMG/FM range, it is related to temp_range
            - temp_range - most important part!! it is hour range of BECMG/FM group includng correction for fallbac
            """

            wx_key = weather_data[wx_key_bcmg[nn]][key_]
            stack2 = []

            for h in range(temp_range[nn][0], temp_range[nn][1]):
                if h in significant_time:
                    stack2.append(1)
            ranges_data = [key_, wx_key_bcmg[nn], '|', temp_range[nn][0],
                           temp_range[nn][1], stack2, wx_key]
            if print_colouring_logic:
                print('ranges_data', ranges_data)

            if becmg_cancelling_wind == 'n' and key_ == 'wind':
                wind_ranges.append(ranges_data)
            if becmg_cancelling_wind == 'y' and key_ == 'time_group':
                wind_ranges.append(ranges_data)

            if becmg_cancelling_vis == 'n' and key_ == 'vis':
                vis_ranges.append(ranges_data)
            if becmg_cancelling_vis == 'y' and key_ == 'time_group':
                vis_ranges.append(ranges_data)

            if becmg_cancelling_weather == 'n' and key_ == 'weather':
                weather_ranges.append(ranges_data)
            if becmg_cancelling_weather == 'y' and key_ == 'time_group':
                weather_ranges.append(ranges_data)

            if becmg_cancelling_clouds == 'n' and key_ == 'clouds':
                clouds_ranges.append(ranges_data)
            if becmg_cancelling_clouds == 'y' and key_ == 'time_group':
                clouds_ranges.append(ranges_data)

            if len(stack2) > 0:  # significant time in range of temp range
                """part responsible for colouring BECMG Initial and FM group
                stack2 - indicattes that  part is in significant time"""

                if not (wx_key_bcmg[nn] == 1 and key_ == 'time_group'):
                    """ wind, BECMG_colour, except Initial  """
                    if type(wx_key) == list:
                        m = 0
                        for i in wx_key:

                            if printing_active:
                                print(i, 'list L')

                            if str('\x1b') not in i[1]:
                                becmg_text = i[1]
                                i = BECMG_color(becmg_text)
                                weather_data[wx_key_bcmg[nn]][key_][m][1] = i

                            m += 1

                    elif type(wx_key) == str:
                        print('error 542 - update code here')
                        quit()
                        if printing_active:
                            print(wx_key, 'string S')
                        becmg_text = wx_key
                        wx_key = BECMG_color(becmg_text)
                        weather_data[wx_key_bcmg[nn]][key_] = wx_key

                if wx_key_bcmg[nn] == 1 and sum(
                        init_stack) == 0:  # if segment necessary to colour the time_group of Initial. Whithout this line Initial time_group will never be painted because time_group is never empty, so BECMG never fall back on initial group whenever ther is any BECMG group
                    """ colouring of Initial - to be checked for selective fall back"""
                    if printing_active:
                        print('nn==1', key_)
                    weather_data[1]['time_group'] = \
                        BECMG_color(weather_data[1]['time_group'])
                    init_stack.append(1)
                if not wx_key_bcmg[nn] == 1 and key_ == 'time_group':
                    becmg_text = wx_key
                    wx_key = BECMG_color(becmg_text)
                    weather_data[wx_key_bcmg[nn]][key_] = wx_key

            elif len(stack2) == 0 and key_ == 'time_group':
                if becmg_cancelling_wind == 'n' \
                        or becmg_cancelling_vis == 'n' \
                        or becmg_cancelling_weather == 'n' \
                        or becmg_cancelling_clouds == 'n':
                    for l in weather_ranges:
                        if l[2] == n:
                            if printing_active:
                                print('sssssss', weather_ranges)
                            becmg_text = wx_key
                            wx_key = BECMG_color(becmg_text)
                            weather_data[n][key_] = wx_key
                            if printing_active:
                                print('vvvvvv', n, weather_data[n][key_])

    def weather_for_selected_time(key_):
        wx_key_bcmg = []
        temp_wx_key = []
        temp_range = []

        for n in range(1, len(weather_data)):
            typ = weather_data[n]['type']
            wx_key = weather_data[n][key_]
            t_range = weather_data[n]['modified_range']
            ### ------ TEMPO colouring ------------------------------------------
            significant_time_stack = []
            # creating significant_time_stack to monitor if significant_time
            # encroaches range
            for h in range(t_range[0], t_range[1]):
                if h in significant_time:
                    significant_time_stack.append(1)

            if len(significant_time_stack) > 0:
                if wx_key == []:
                    # print(typ, t_range, 'empty\n')
                    if typ == 'Initial' or typ == 'B' or typ == 'FM':
                        pass
                elif wx_key != []:
                    # print(typ, t_range, wx_key)
                    if typ == 'T' or typ == 'P40 T' or typ == 'P30 T' or typ == 'P40' or typ == 'P30':
                        if key_ == 'clouds' or key_ == 'weather' or key_ == 'vis':
                            m = 0
                            for i in wx_key:
                                if str('\x1b') not in i:
                                    skk = i
                                    tempo_text = TEMPO_color(skk)
                                    i = tempo_text
                                    weather_data[n][key_][m] = i
                                m += 1
                        else:
                            if type(wx_key) == list:
                                m = 0
                                for i in wx_key:
                                    if str('\x1b') not in i:
                                        skk = i
                                        tempo_text = TEMPO_color(skk)
                                        i = tempo_text
                                        weather_data[n][key_][m] = i
                                    m += 1

                            else:
                                skk = wx_key
                                tempo_text = TEMPO_color(skk)
                                wx_key = tempo_text
                                weather_data[n][key_] = wx_key

                    elif typ == 'Initial' or typ == 'B' or typ == 'FM':
                        pass
                    else:
                        print('unknown format\n', wx_key)

                        skk = wx_key
                        tempo_text = TEMPO_color(skk)
                        wx_key = tempo_text
                        weather_data[n][key_] = wx_key

            elif len(significant_time_stack) == 0:
                """ stores n which contain TEMPO and is outside significant time
                - it is stored in tempo_line_n"""
                if typ == 'T' or typ == 'P40 T' or typ == 'P30 T' or typ == 'P40' or typ == 'P30':
                    if key_ == 'wind':
                        tempo_line_n.append(n)

        for n in range(1, len(weather_data)):
            # ------Initial, BECMG and FM acolouring -------------------------
            """ colouring fo mentioned groups.. 
            FM cancels out all what was before it - (y/n option)
            BECMG changes only mthose parameters which are mentioned (wind, vis, clouds.. weather (y/n)"""

            typ = weather_data[n]['type']
            wx_key = weather_data[n][key_]
            t_range = weather_data[n]['modified_range']

            """ below part modifies effective ranges based on: 
                - wind,vis,weather, and clouds and
                - depends if one of those parameters had value, 
                if there is no value than it falls back on previous which had value.
                Range i modified accordingly. Very important part!!"""
            if (
                    typ == 'Initial' or typ == 'B' or typ == 'FM') and wx_key != []:
                wx_key_bcmg.append(n)
                temp_range.append([t_range[0], t_range[1]])
                if printing_active:
                    print('filled', 'n=', n, 'typ', typ, key_, wx_key,
                          '\ntemp_range', temp_range, )
                ##print('IF',temp_range)

            elif fm_canceling == 'y' and (
                    typ == 'Initial' or typ == 'B') and wx_key == []:
                """fm canceling engine - description at INPUTS """
                if len(wx_key_bcmg) > 0:
                    temp_range[-1] = \
                        [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                         weather_data[n]['modified_range'][1]]
                    ##print('elif', temp_range)
            elif fm_canceling == 'n' and (
                    typ == 'Initial' or typ == 'B' or typ == 'FM') and wx_key == []:
                if len(wx_key_bcmg) > 0:
                    temp_range[-1] = \
                        [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                         weather_data[n]['modified_range'][1]]

                if printing_active:
                    print('empty', 'n=', n, 'typ', typ, wx_key, '\ntemp_range',
                          temp_range, )

        if printing_active:
            print('')
        for nn in range(0, len(wx_key_bcmg)):
            """part responsible for making temp_ranges 
            - responsible for fallback on previous weather-key to keep contionous range
            - wx_key_bcmg - store n number of line of BECMG and FM plus Initial
            - stack 2 indicates if significant time necroaches on BECMG/FM range, it is related to temp_range
            - temp_range - most important part!! it is hour range of BECMG/FM group includng correction for fallbac
            """

            wx_key = weather_data[wx_key_bcmg[nn]][key_]
            stack2 = []

            for h in range(temp_range[nn][0], temp_range[nn][1]):
                if h in significant_time:
                    stack2.append(1)
            ranges_data = [key_, wx_key_bcmg[nn], '|', temp_range[nn][0],
                           temp_range[nn][1], stack2, wx_key]
            if print_colouring_logic:
                print('ranges_data',ranges_data)

            if becmg_cancelling_wind == 'n' and key_ == 'wind':
                wind_ranges.append(ranges_data)
            if becmg_cancelling_wind == 'y' and key_ == 'time_group':
                wind_ranges.append(ranges_data)

            if becmg_cancelling_vis == 'n' and key_ == 'vis':
                vis_ranges.append(ranges_data)
            if becmg_cancelling_vis == 'y' and key_ == 'time_group':
                vis_ranges.append(ranges_data)

            if becmg_cancelling_weather == 'n' and key_ == 'weather':
                weather_ranges.append(ranges_data)
            if becmg_cancelling_weather == 'y' and key_ == 'time_group':
                weather_ranges.append(ranges_data)

            if becmg_cancelling_clouds == 'n' and key_ == 'clouds':
                clouds_ranges.append(ranges_data)
            if becmg_cancelling_clouds == 'y' and key_ == 'time_group':
                clouds_ranges.append(ranges_data)

            if len(stack2) > 0:  # significant time in range of temp range
                """part responsible for colouring BECMG Initial and FM group
                stack2 - indicattes that  part is in significant time"""

                if not (wx_key_bcmg[nn] == 1 and key_ == 'time_group'):
                    """ wind, BECMG_colour, except Initial  """
                    if type(wx_key) == list:
                        m = 0
                        for i in wx_key:
                            if printing_active:
                                print(i, 'list L')

                            if str('\x1b') not in i:
                                becmg_text = i
                                i = BECMG_color(becmg_text)
                                weather_data[wx_key_bcmg[nn]][key_] = i

                            m += 1

                    elif type(wx_key) == str:
                        if printing_active:
                            print(wx_key, 'string S')
                        becmg_text = wx_key
                        wx_key = BECMG_color(becmg_text)
                        weather_data[wx_key_bcmg[nn]][key_] = wx_key

                if wx_key_bcmg[nn] == 1 and sum(
                        init_stack) == 0:  # if segment necessary to colour the time_group of Initial. Whithout this line Initial time_group will never be painted because time_group is never empty, so BECMG never fall back on initial group whenever ther is any BECMG group
                    """ colouring of Initial - to be checked for selective fall back"""
                    if printing_active:
                        print('nn==1', key_)
                    weather_data[1]['time_group'] = \
                        BECMG_color(weather_data[1]['time_group'])
                    init_stack.append(1)
                if not wx_key_bcmg[nn] == 1 and key_ == 'time_group':
                    becmg_text = wx_key
                    wx_key = BECMG_color(becmg_text)
                    weather_data[wx_key_bcmg[nn]][key_] = wx_key

            elif len(stack2) == 0 and key_ == 'time_group':
                if becmg_cancelling_wind == 'n' \
                        or becmg_cancelling_vis == 'n' \
                        or becmg_cancelling_weather == 'n' \
                        or becmg_cancelling_clouds == 'n':
                    for l in weather_ranges:
                        if l[2] == n:
                            if printing_active:
                                print('sssssss', weather_ranges)
                            becmg_text = wx_key
                            wx_key = BECMG_color(becmg_text)
                            weather_data[n][key_] = wx_key
                            if printing_active:
                                print('vvvvvv', n, weather_data[n][key_])

    # ref('copy of weather data') # MOVED from earlier code position. Original remained with hashes '#'
    #
    # import copy
    # weather_data_copy = copy.deepcopy(weather_data)
    # if printing_active:
    #    print(prBoxed('weather_data_copy'))
    #    pf.print_list(weather_data_copy)
    init_stack = []  # do not remove - in use

    wind_ranges = []
    vis_ranges = []
    weather_ranges = []
    clouds_ranges = []

    tempo_line_n = []

    weather_for_selected_time_RIGHT('wind')
    weather_for_selected_time_RIGHT('vis')
    weather_for_selected_time_RIGHT('clouds')
    weather_for_selected_time_RIGHT('weather')
    weather_for_selected_time('time_group')
    weather_for_selected_time('group_type_long')

    ref('Print weather again')
    if printing_active:
        pf.print_list(weather_data)

    print('\n')
    # print('----------TAF string ---------')
    if print_TAF_without_colouring:
        print(TAF)

    # print('-------- RAW TAF -------------')
    if print_TAF_without_colouring:
        print_dicts(gr_data, 'groups_strings')
        print(' ')

    # changing colour of not significant weather data to light grey

    for n in range(1, len(weather_data)):
        for key, value in weather_data[n].items():
            if key == 'weather' or key == 'clouds' or key == 'vis' or key == 'wind':
                # if key == 'group_type_long': pass
                def colouring_outside_sgignificant(key_4, list_4):
                    if key == key_4:
                        for i in list_4:
                            if n == i[1] and 1 in i[5]:
                                becmg_time_group_coloring_list[n - 1].append(1)
                                m = 0
                                if type(weather_data[n][key]) == str:
                                    print('error 3224 - T_d- add code here')
                                    quit()
                                elif type(weather_data[n][key]) == list:
                                    m=0
                                    for w in weather_data[n][key]:
                                        weather_data[n][key][m] = w
                                        # IMPORTANT!!
                                        weather_data[n][key][m].append('relevant BECMG')
                                        m+=1

                                else:
                                    print('error 525 - check code here')
                                    quit()


                            elif n == i[1] and i[5] == []:
                                m = 0
                                for w in weather_data_copy[n][key]:
                                    w = grayed_area_right(w)
                                    weather_data[n][key][m][1] = w # VERY IMPORTANT - data from copy - raw wather value without threat level is being coloured gray and than stored in original weather file at correct value location wiht already added threat level
                                    # adding info to weather value that this part of weather in BECMG is not relevant for selected time period
                                    weather_data[n][key][m].append('not-relevant BECMG') # VERY IMPORTANT!
                                    m += 1
                            else:
                                pass

                colouring_outside_sgignificant('wind', wind_ranges)
                colouring_outside_sgignificant('vis', vis_ranges)
                colouring_outside_sgignificant('weather', weather_ranges)
                colouring_outside_sgignificant('clouds', clouds_ranges)

                for number in tempo_line_n:
                    """ths part paints all TEMPO lines outside significant time gray 
                    - compares curent n with n in tempo_line_n
                    - tempo_line_n lsit stores all n caotaing TEMPO outsid significatntime"""
                    if len(tempo_line_n) > 0 and n == number:
                        m = 0
                        for i in weather_data_copy[n][key]:
                            i = grayed_area_right(i)
                            weather_data[n][key][m][1] = i
                            # add non relevant to  wx value data
                            weather_data[n][key][m].append('not-relevant TEMPO')
                            m += 1

            elif key == 'time_group' or key == 'group_type_long':
                """ this part colours in gray time group and everything left of 
                it - it uses copy of weather data group"""
                if type(value) == list:
                    m = 0
                    for p in value:
                        i = grayed_area_left(weather_data_copy[n][key][m])
                        weather_data[n][key][m] = i

                        m += 1
                elif type(value) == str:
                    """ colouring of time_group of BECEMG """
                    if becmg_time_group_coloring == 'y':
                        if not sum(becmg_time_group_coloring_list[n - 1]) > 0:
                            value = grayed_area_left(value)
                            weather_data[n][key] = value
                        elif sum(becmg_time_group_coloring_list[n - 1]) > 0:
                            value = BECMG_non_significant_color(value)
                            weather_data[n][key] = value
                    elif becmg_time_group_coloring == 'n':
                        value = grayed_area_left(value)
                        weather_data[n][key] = value

                """elif weather_data[n][key] == list:
                    m = 0
                    for i in weather_data[n][key]:
                        if '\x1b[' not in i:
                            i = prLightGray(i)
                            weather_data[n][key][m] = i
                        m+=1"""
    ##################
    """creating code which will display only caution,warning and severe wx"""

    # creating new weather data list of selected items
    thr_lvl_data =pf.create_thr_lvl_data_list(weather_data,weather_data_copy, settings)

    # creating copy of thr_lvl_data - required depending on settings to change colour of type and time_group
    thr_lvl_data_copy = copy.deepcopy(thr_lvl_data)

    # adding relevance part to data in 'type' and 'time_group'
    pf.add_relevance_to__type__and__time_group(BECMG_color, TEMPO_color, grayed_area_right, thr_lvl_data)

    ### finding and colouring the highest level o threat for an airport ###
    # finding max threat level in one_line of TAF
    max_threat_level_in_one_line = pf.find_max_threat_level_in_one_line(thr_lvl_data)


    # 'type' and time_group' data - adding threat level of one_line
    pf.adding_threat_level_data_of__type__and_time_group__to__thr_lvl_data(max_threat_level_in_one_line, thr_lvl_data)


    # finding max threat level at the airport
    max_threat_level_at_airport = pf.finding_max_threat_level_at_the_airport(max_threat_level_in_one_line)

    # adding threat level to airport name data
    thr_lvl_data[0]['wind'] = max_threat_level_at_airport + thr_lvl_data[0]['wind']

    pf.colouring_airport_in_thr_lvl_data(thr_lvl_data, thr_lvl_data_copy, grayed_area_right)

    pf.change_colour_of__type__and__time_group_to_match_max_thr_lvl_in__one_line(thr_lvl_data, thr_lvl_data_copy, settings)

    # crating list of hazardpus weather- ready to print
    all_lines = pf.create_list_of_thr_lvl_weather(thr_lvl_data, settings, print_type, print_time_group)

    # adding coloured station name - required for later printing of data
    colored_station_name = pf.adding_coloured_station_name(thr_lvl_data)

    # printing all lines - END
    final_line = pf.print_final_all_lines_data(all_lines,settings)
    ###

    def priniting_significant_time_ranges():
        import math
        try:
            s_from = [math.floor(significant_time[0] / 24) + 1,
                      significant_time[0] % 24]
            s_to = math.floor(significant_time[-1] / 24) + 1, significant_time[
                -1] % 24
            # print('----------FINAL TAF ----------------')
            # print(f' day:{my_day} time:{my_time_copy}, '

            day_left = int(weather_data_copy[1]['time_group'][0:2])
            day_right = int(weather_data_copy[1]['time_group'][5:7])

            def geting_day_start(significant_time):
                if 0 < significant_time[0] < 24:
                    day_start = day_left
                    return day_start
                elif 24 <= significant_time[0] < 48:
                    if day_right == 1:
                        day_start = day_left+1
                        return day_start
                    elif day_right == 2 and day_left != 1:
                        day_start = day_right - 1
                        return day_start
                    elif day_right >= 2 and day_left == day_right -1:
                        day_start = day_right
                        return day_start
                    elif day_right >= 3 and day_left == day_right - 2:
                        day_start = day_right -1
                        return day_start
                elif 48 <= significant_time[0] < 72:
                    day_start = day_right
                    return day_start
            day_start=geting_day_start(significant_time)

            def getting_day_end(significant_time):
                if 0 < significant_time[-1] < 24:
                    day_end = day_left
                    return day_end
                elif 24 <= significant_time[-1] < 48:
                    if day_right == 1:
                        day_end = day_left + 1
                        return day_end
                    elif day_right == 2 and day_left != 1:
                        day_end = day_right - 1
                        return day_end
                    elif day_right >= 2 and day_left == day_right - 1:
                        day_end = day_right
                        return day_end
                    elif day_right >= 3 and day_left == day_right - 2:
                        day_end = day_right -1
                        return day_end
                elif 48 <= significant_time[-1] < 72:
                        day_end = day_right
                        return day_end
            day_end = getting_day_end(significant_time)


            #Printing ICAO station name in different colour depending what is the maximum threat level of wather at the airport
            if significant_range_active:
                print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
                print('Taf_decoder.py r1')
                print(f'{colored_station_name}\t\t      dd{day_start}h{s_from[1]}/d{day_end}h{s_to[1]+1}',
                      f'\t\t\tsignificant_range={significant_range},', significant_time[0], significant_time[-1])
            elif not significant_range_active:
                print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
                print('Taf_decoder.py r2')
                print(f'{colored_station_name}\t\t /{day_start}/ {s_from[1]}:00  -> /{day_end}/ {s_to[1]+1}:00',
                    f'\t\t\t',significant_start_hour, significant_end_hour)

        except IndexError:
            print('\n\t\t\t',TAF)
            print('')
            pass

    def print_all_data():
        ref('gr_data:')
        pf.print_list(gr_data)
        ref('time_gr_data')
        pf.print_list((time_gr_data))
        ref('weather_data')
        pf.print_list(weather_data)
        ref('weather_data_copy')
        pf.print_list(weather_data_copy)

    if print_ranges_legend:
        priniting_significant_time_ranges()

    # below - line responsible for printing airport _publication time line


    ###### PRINTING OUT COLOURED TAF ############
    final_coloured_taf_string = pf.final_coloured_TAF_printout(BECMG_color, error_added, error_found, grayed_area_right, weather_data, gr_data)

    #### RUNWAY DATA FINAL PRINT OUT BELOW TAF #####
    # Printing rwy_data(end_string) below TAF
    end_string = pf.runway_data_below_TAF_printout(TAF)
    #####
    if not error_found == []:
        err_msg = error_added("Errors found:")
        print('\nLegend:' + "\033[94m {}\033[00m".format('TEMPO'),
              "\033[95m {}\033[00m".format('Initial/BECMG') + ' ' + err_msg)
        print(error_found)
        print(error_type_of_group)

        print_dicts(gr_data, 'groups_strings')

    # print_all_data()

    if print_colouring_logic:
        print('wind_ranges'),pf.print_list(wind_ranges)
        print()
        pf.print_list(vis_ranges)
        print('')
        pf.print_list(weather_ranges)
        print('')
        pf.print_list(clouds_ranges)
        print(becmg_time_group_coloring_list)

    apt_code = weather_data_copy[0]['wind'][0]
    runway_string = pf.avaliable_rwys(apt_code)


    # final line: EPWA 28015G25KT -SHRA BKN020CB SHRA BKN012CB BR,

    # runway_string: 15|33 3690 11|29 2800,

    # end_string: 					   11 2560 ILS (2*)(1*)
    # 										  ||ILS*: 2*"Y"(110-R300m) 2*"Z"(110-R300m) 1*"Y"(220-550m) 1*"Z"(220-550m)
    # 					                      ||NPAs: ..(+4)  0/4
    # 					   29 2299 (ect....

    return [final_coloured_taf_string,final_line, runway_string, end_string]


