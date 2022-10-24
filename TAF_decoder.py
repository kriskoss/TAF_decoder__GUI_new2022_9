"""HOW DOES TAF DECODER WORKS?
1. TAF in a form of string isan input
2. It is being parsed into time groups (imaginary ROWS) of Initial, TEMPO, BECMG,PROB.. etc
3. In each time group elements are assigned into groups such as: WIND,VIS, WEATHER, CLOUDS.. etc
4. Than, based on the INPUT of the  significant range - the preriod of time that the user wants the TAF to be analised- the parts of the THF are being split into RELEVANT and NON-RELEVANT.
5. For Init, TEMPO, PROB and PROB TEMPO  time groups - they can be sent to be COLOURED based on the WIND,VIS, WEATHER, CLOUDS limits
6. For BECMG and FM time groups, each group: WIND,VIS, WEATHER, CLOUDS is treated as a stack
    - only the last item in the e.g CLOUD stack is RELEVANT, and any other is being trated as a NON RELEVANT
    - once the RELEVANT items found then time group is ready  for COLOURING.

    TO DO:
    - split code into two parts: - parsing into the groups
    - checking if time group is in the SIGNIFICNT RANGE (selected by the user)
    - analizing BECMG/FM and TEMPO/PROB
    - colouring

    !!!! FIND A DATASTRUCTURE WHERE IT ALL WILL BE CLEARLY VISIBLE - csv? json file with propprt plugin?"""






import TAF_decoder__functions as Tdf
import final_program_functions
from TAF_decoder__helper_functions import ref, prBoxed,TEMPO_color,BECMG_color, INTER_color,BECMG_non_significant_color,grayed_area_left,grayed_area_right,error_added,add_to_dict_gr_data,print_dicts,add_to_dict_TIME_gr_data, print_keys, print_all_data, print_list
import copy
def TAF_decoder_function(settings, TAF, start_hour, end_hour):

    ### IF ERROR DETECTED  -- returns RAW (may need some more work)
    return_raw__error_detected = False

    # Spliiting TAF into words
    TAF_split = TAF.split(' ')

    if settings.printing_active:
        print('\n', prBoxed('TAF_split'), TAF_split)


    # Searching for time groups which divide TAF into groups containing time range
    time_string = [0]
        # Adding START index.
        # Each TAF part has to have beginning and end and 0-2, 2-9,9-18 ect             """

    for n in range(len(TAF_split)):
        # Seaching dash in words to group of words into time groups """
        # searching index of '/'
        if TAF_split[n].count('/') == 1 \
                and TAF_split[n][:4].isdigit() and TAF_split[n][5:].isdigit() \
                and len(TAF_split[n]) == 9:
            time_string.append(n)
        if TAF_split[n].count('FM') == 1:
            if len(TAF_split[n]) == 8 \
                    and TAF_split[n][2:].isdigit() \
                    and time_string.append(n):
                time_string.append(n)

    time_string.append(len(TAF_split))
    # END index-- ...9-18,18-END index


    if settings.printing_active:
        print('\n', prBoxed('time_string1:'), time_string)

    time_string_uncorrected = time_string[:]
        # DO NOT REMOVE this - coping a list to use it below

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
        elif one_before == 'TEMPO' or one_before == 'INTER' :
            if two_before == 'PROB30' or two_before == 'PROB40':
                time_string[n] = time_string[n] - 2
            else:
                time_string[n] = time_string[n] - 1


    if settings.printing_active:
        print('', prBoxed('time_string2:'), time_string)
    ref('Dividing TAF into time groups')



    groups = []
    for n in range(0, len(time_string) - 1):  # VERY IMPORTANT
        group = TAF_split[time_string[n]: time_string[n + 1]]
        groups.append(group)
    if settings.printing_active:
        print(prBoxed('groups: '), groups)

    # Creating list of dictionaries
    gr_data = []
    for n in range(len(groups)):
        gr_data.append({})

    ref('AAA')
    add_to_dict_gr_data(groups, 'TAF_slice', gr_data)

    if settings.printing_active:
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
            if g == 'TEMPO' or g == 'BECMG' or g =='INTER':
                points.append(6)
            if g == 'PROB30' or g == 'PROB40':
                points.append(7)

        formatted_TAF_slices[n].insert(0, ' ' * (13 - sum(points)))

    add_to_dict_gr_data(formatted_TAF_slices, 'formatted_TAF_slices', gr_data)

    ref('BBB')
    if settings.printing_active:
        print(prBoxed('gr_data')), print_dicts(gr_data, 'formatted_TAF_slices')

    # creates groups_strings --> that is list of strings containg each group separated by TEMPO, BCMG, PROB30/40
    groups_strings = []
    for n in range(len(groups)):
        s = ""
        for t in groups[n]:
            s += t + ' '
        groups_strings.append(s)

    add_to_dict_gr_data(groups_strings, 'groups_strings', gr_data)
    ref('CCC')
    if settings.printing_active:
        print(prBoxed('gr_data')), print_dicts(gr_data, 'groups_strings')

    ref('DDD')
    if settings.printing_active:
        print(prBoxed('time_string_uncorrected'), time_string_uncorrected)
    # time_string_uncorrected - first and last lelemt removed to work correctly')
    del time_string_uncorrected[
        0]  ### DO NOT REMOVE this line - very important
    del time_string_uncorrected[
        -1]  ### DO NOT REMOVE this line - very important
    if settings.printing_active:
        print(prBoxed('time_string_uncorrected'), '  ',
              time_string_uncorrected,
              '    -corrected')

    time_gr_data = []  # creating time_gr_data - this is gr_data MINUS first slice
    for n in range(len(time_string_uncorrected)):
        time_gr_data.append({})

    ref('EEE')
    if settings.printing_active:
        print(prBoxed('time_gr_data'))
    if settings.printing_active:
        print(prBoxed('time_gr_data')), print_list(time_gr_data)

    ref(1)
    if settings.printing_active:
        add_to_dict_TIME_gr_data(time_string_uncorrected,
                                 'time_string corrected for TEMPO and BECMG and INTER',time_gr_data)

    if settings.printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'time_string '
                                                    'corrected for TEMPO and BECMG and INTER')

    ref(2)
    add_to_dict_TIME_gr_data(time_string_uncorrected,
                             'time_string_END_uncorrected',time_gr_data)  ### HERE
    if settings.printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'time_string_END_uncorrected')

    time_group_list = []
    for n in range(len(time_string_uncorrected)):
        """ this part extracts string containing time and date of each TAF time 
        group, lets call it a dash_word. It is extracted fotm time_gr_data"""
        lista = TAF_split[time_string_uncorrected[n]]
        time_group_list.append(lista)
    ref(3)
    add_to_dict_TIME_gr_data(time_group_list, 'time_group_list', time_gr_data)
    if settings.printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'time_group_list')

    ### FUNCTION CALL ###
    ref(4)
    # Creating start and end time dates
    Tdf.creating_start_end_times_dates(settings,time_group_list, Tdf, time_gr_data)

    ref('GGG')
    if settings.printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data, 'hours_list')


    ### FUNCTION CALL ###
    station_name =[] # do not remove!
    Tdf.creating_type_of_group(settings, time_string_uncorrected, TAF_split, station_name, time_gr_data)


    ref('HHHH')
    if settings.printing_active:
        print(prBoxed('time_gr_data')), print_dicts(time_gr_data,
                                                    'type_of_group')

    error_found = []
    score = []
    reference = []


    ### FUNCTION CALL ###
    weather_data = Tdf.creating_weather_data_list(settings,gr_data, type_of_group, reference, score)
#["vis"]
    ref('III')
    if settings.printing_active:
        print(prBoxed('weather_data'))
        print_list(weather_data)

    """ part responsible for collecting above error data and showing which part 
    is erroneus 
    """
    while score:
        point = score.pop()
        if point in reference:
            reference.remove(point)
    ref('JJJ')
    if settings.printing_active:
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


    ### FUNCTION CALL ###
    ref('Transferring group type from time_gr_data to weather_data')
    Tdf.transferring_group_type_from_time_gr_data_to_weather_data(time_gr_data, weather_data)

    ref('KKK')
    if settings.printing_active:
        print(prBoxed('weather_data')), print_list(weather_data)

    # searching for slice number containing BECMG or Initial in weather data:
    becmg_list = []
    for n in range(len(weather_data)):
        typ = ['B', 'Initial', 'FM']
        if weather_data[n]['type'] in typ:
            becmg_list.append(n)
    ref('LLL')
    if settings.printing_active:
        print(prBoxed('becmg_list')), print(becmg_list)



    if settings.printing_active:
        print_keys(time_gr_data, gr_data, weather_data)


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



    ### FUNCTION CALL ###
    Tdf.add_to_dict_weather_data(time_range, 'time_range', weather_data)
    ref('MMM')
    if settings.printing_active:
        print(prBoxed('time_range ADDED')), print_list(weather_data)
        print(prBoxed('time_gr_data'))
        print_list(time_gr_data)


    ref('NNN -- printing time range of BECMG slices')
    for i in becmg_list:
        s_range = weather_data[i]['time_range']
        range_start = s_range[0]
        range_end = s_range[1]
        if settings.printing_active:
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
    if settings.printing_active:
        print(prBoxed('bcmg_range - new list')), print_list(bcmg_range)


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
    if settings.printing_active:
        print(prBoxed('final modified range')), print_list(modified_range)
    ref('PPP - modified range to overlap')
    if settings.printing_active:
        print(prBoxed('modified range')), print_list(modified_range)

    # adding modified time range
    for n in range(len(weather_data)):
        t_r = weather_data[n]['time_range']
        typ = weather_data[n]['type']
        if typ == 'B' or typ == 'Initial' or typ == 'FM':
            weather_data[n]['modified_range'] = modified_range.pop(0)
        else:
            weather_data[n]['modified_range'] = t_r

    ref('QQQ')
    if settings.printing_active:
        print(prBoxed('weather_data - after adding modified_range')), \
        print_list(weather_data)


#############
    initial_start = weather_data[1]['time_range'][0]
    initial_end = weather_data[1]['time_range'][1] - 1

    ### FUNCTION CALL ###
    significant_time_range_data = Tdf.getting_significant_time_range(initial_end, initial_start,
                                                                     start_hour,
                                                                     end_hour, settings)


    significant_time = significant_time_range_data[0]
    start_hour = significant_time_range_data[1]
    end_hour = significant_time_range_data[2]


##############
    ref('significant_time')
    if settings.printing_active:
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
        elif d == 'ITR':
            weather_data[n]['group_type_long'] = 'INTER'

        elif d == 'P40 T':
            weather_data[n]['group_type_long'] = 'PROB40 TEMPO'
        elif d == 'P40 ITR':
            weather_data[n]['group_type_long'] = 'PROB40 INTER'

        elif d == 'P30 T':
            weather_data[n]['group_type_long'] = 'PROB30 TEMPO'
        elif d == 'P30 ITR':
            weather_data[n]['group_type_long'] = 'PROB30 INTER'

        elif d == 'P30':
            weather_data[n]['group_type_long'] = 'PROB30'
        elif d == 'P40':
            weather_data[n]['group_type_long'] = 'PROB40'
        elif d == 'FM':
            weather_data[n]['group_type_long'] = 'FM'
            weather_data[n]['time_group'] += ' '
            """ adding space at the end of time_group if group tyep is FM"""
        else:
            weather_data[n]['group_type_long'] = 'ukn_1'

        if settings.gap_active:
            weather_data[n]['gap'] = settings.gap_symbol * \
                                     (13 - len(weather_data[n]['group_type_long']))
        else:
            weather_data[n]['gap']= settings.time_group_type__symbol_BEFORE
    # printing weather for selected time
    # creating function based on above which creates

    ref('copy of weather data')

    weather_data_copy = copy.deepcopy(weather_data)
    if settings.printing_active:
       print(prBoxed('weather_data_copy'))
       print_list(weather_data_copy)


    ref('ppppppp')
    if settings.printing_active:
        print_list(weather_data)
    # testing adding colour to hazardous weather
    becmg_time_group_coloring_list = []

    ### FUNCTION CALL ###
    # colouring each weather item - using colouring.py
    Tdf.colouring_each_weather_item(becmg_time_group_coloring_list, weather_data)

    ref('--- weather_for_selected_time function -----')


    init_stack = []  # do not remove - in use

    wind_ranges = []
    vis_ranges = []
    weather_ranges = []
    clouds_ranges = []

    tempo_line_n = []

    Tdf.weather_for_selected_time_RIGHT('wind',settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack)
    Tdf.weather_for_selected_time_RIGHT('vis',settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack)
    Tdf.weather_for_selected_time_RIGHT('clouds',settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack)
    Tdf.weather_for_selected_time_RIGHT('weather',settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack)
    Tdf.weather_for_selected_time('time_group',settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack)
    Tdf.weather_for_selected_time('group_type_long',settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack)

    ref('Print weather again')
    if settings.printing_active:
        print_list(weather_data)

    if settings.print_TAF_without_colouring:
        print(TAF)

    # print('-------- RAW TAF -------------')
    if settings.print_TAF_without_colouring:
        print_dicts(gr_data, 'groups_strings')
        print(' ')

    # changing colour of not significant weather data to light grey

    for n in range(1, len(weather_data)):
        for key, value in weather_data[n].items():
            if key == 'weather' or key == 'clouds' or key == 'vis' or key == 'wind':
                # if key == 'group_type_long': pass

                Tdf.colouring_outside_sgignificant('wind', wind_ranges,  key, becmg_time_group_coloring_list, weather_data_copy,  n, weather_data)
                Tdf.colouring_outside_sgignificant('vis', vis_ranges,  key, becmg_time_group_coloring_list, weather_data_copy,  n, weather_data)
                Tdf.colouring_outside_sgignificant('weather', weather_ranges,  key, becmg_time_group_coloring_list, weather_data_copy,  n, weather_data)
                Tdf.colouring_outside_sgignificant('clouds', clouds_ranges,  key, becmg_time_group_coloring_list, weather_data_copy,  n, weather_data)

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
                    if settings.becmg_time_group_coloring == 'y':
                        if not sum(becmg_time_group_coloring_list[n - 1]) > 0:
                            value = grayed_area_left(value)
                            weather_data[n][key] = value
                        elif sum(becmg_time_group_coloring_list[n - 1]) > 0:
                            value = BECMG_non_significant_color(value)
                            weather_data[n][key] = value
                    elif settings.becmg_time_group_coloring == 'n':
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
    thr_lvl_data =Tdf.create_thr_lvl_data_list(weather_data, weather_data_copy, settings)

    # creating copy of thr_lvl_data - required depending on settings to change colour of type and time_group
    thr_lvl_data_copy = copy.deepcopy(thr_lvl_data)

    # adding relevance part to data in 'type' and 'time_group'

    try:
        Tdf.add_relevance_to__type__and__time_group(BECMG_color, TEMPO_color, INTER_color, grayed_area_right, thr_lvl_data)
    except:
        print('fatal error - T_d.252')
        return_raw__error_detected =True

    ### finding and colouring the highest level o threat for an airport ###
    # finding max threat level in one_line of TAF
    try:
        max_threat_level_in_one_line = Tdf.find_max_threat_level_in_one_line(thr_lvl_data)


        # 'type' and time_group' data - adding threat level of one_line
        Tdf.adding_threat_level_data_of__type__and_time_group__to__thr_lvl_data(max_threat_level_in_one_line, thr_lvl_data)


        # finding max threat level at the airport

        max_threat_level_at_airport = Tdf.finding_max_threat_level_at_the_airport(max_threat_level_in_one_line)

        # adding threat level to airport name data
        thr_lvl_data[0]['wind'] = max_threat_level_at_airport + thr_lvl_data[0]['wind']
    except:
        print('FATAL ERROR - T_d.maxddd')
        return_raw__error_detected =True

    if not return_raw__error_detected:
        Tdf.colouring_airport_in_thr_lvl_data(thr_lvl_data, thr_lvl_data_copy, grayed_area_right)

        Tdf.change_colour_of__type__and__time_group_to_match_max_thr_lvl_in__one_line(thr_lvl_data, thr_lvl_data_copy, settings)

        # crating list of hazardpus weather- ready to print
        all_lines, wind_lines = Tdf.create_list_of_thr_lvl_weather(thr_lvl_data, settings, settings.print_type, settings.print_time_group)
        # adding coloured station name - required for later printing of data
        colored_station_name = Tdf.adding_coloured_station_name(thr_lvl_data)

        # Suplementary print outs
        if not error_found == []:
            err_msg = error_added("Errors found:")
            print('\nLegend:' + "\033[94m {}\033[00m".format('TEMPO'),
                  "\033[95m {}\033[00m".format('Initial/BECMG') + ' ' + err_msg)
            print(error_found)
            print(error_type_of_group)

            print_dicts(gr_data, 'groups_strings')
        if settings.print_colouring_logic:
            print('wind_ranges'), print_list(wind_ranges)
            print()
            print_list(vis_ranges)
            print('')
            print_list(weather_ranges)
            print('')
            print_list(clouds_ranges)
            print(becmg_time_group_coloring_list)
        # print_all_data(gr_data, time_gr_data, weather_data, weather_data_copy)


        ##### PRINTING FINAL ##########

        apt_code = weather_data_copy[0]['wind'][0]

        # Generating data and adding it into the dictionary
        decoded_TAF_dict = {
            "station_name": station_name[0],
            "selected_time_info":Tdf.generate_selected_time_info(significant_time, weather_data_copy, colored_station_name, start_hour, end_hour, TAF),
            "decoded_TAF":Tdf.generate_decoded_TAF(settings,BECMG_color, error_added, error_found, grayed_area_right, weather_data, gr_data),
            "runways_length":Tdf.avaliable_rwys(apt_code, settings),
            "station_threats":Tdf.convert_data_lists_to_single_string(all_lines, settings),
            "appr_data":Tdf.generate_appr_info(TAF, settings),
            "time_range": time_range,
            "max_threat_level_at_airport": max_threat_level_at_airport,
            "wind_profile": Tdf.convert_data_lists_to_single_string(wind_lines,settings)
        }
    # ERROR DETECTED IN DECODING --- RETURNING RAW TAF
    else:
        print('T_d. printing raw')
        decoded_TAF_dict = {
            "station_name": station_name[0],
            "selected_time_info": 'errA',
            "decoded_TAF": TAF,
            "runways_length": 'errB',
            "station_threats": station_name[0],
            "appr_data": 'errD',
            "time_range": time_range,
            "max_threat_level_at_airport": ['not-relevant'],
            "wind_profile": 'errF',
        }
    return decoded_TAF_dict


