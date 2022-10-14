"""function which are not required in a core file"""
from colouring import SignificantColouring
import colouring
import json
from colouring import prGreen, prYellow, prRed, prPurple

import math

import TAF_decoder__helper_functions as Td_helpers



def out_of_validity_perriod_error_generator(initial_start, initial_end):

    out_of_r_error_msg = 'Out of range. Try:'
    ending=''
    if initial_end >= 72:
        print('\nERROR: TAF range too long - check if it is correct\n')
        pass

    elif initial_end >= 48 and initial_end < 71:
        initial_end_day2 = 47
        print(out_of_r_error_msg,f' 1: {initial_start} - 23{ending}, 2:  0 - 23{ending}, 3:  0 - {initial_end - 48}{ending}')

    elif initial_end >= 24 and initial_end < 48:
        print(out_of_r_error_msg,f' 1: {initial_start} - 23{ending}, 2:  0 - {initial_end - 24}{ending}')

    elif initial_end < 24:
        print(out_of_r_error_msg,f' 1: {initial_start} - {initial_end - 1}{ending}')

def getting_significant_time_range(initial_end,initial_start, significant_start_hour,  significant_end_hour, settings):
    """function which checks if provided significant time range is corrextand also generates significant time list"""
    cancel_out_of_range_msg = settings.cancel_out_of_range_msg
    if not cancel_out_of_range_msg:
        if significant_start_hour < initial_start or significant_end_hour > initial_end:
            out_of_validity_perriod_error_generator(initial_start,
                                                       initial_end)
        significant_time = []
        for n in range(significant_start_hour, significant_end_hour):

            if initial_start <= n <= initial_end:
                significant_time.append(n)
        return [significant_time,significant_start_hour,significant_end_hour]

    elif cancel_out_of_range_msg:
        significant_time = []
        for n in range(significant_start_hour, significant_end_hour):

            if initial_start <= n <= initial_end:
                significant_time.append(n)
        return [significant_time, significant_start_hour,
                significant_end_hour]

# functions required for function:  apt_thr_lvl
def colouring_each_weather_item(becmg_time_group_coloring_list, weather_data): ###, thr_lvl_clouds, thr_lvl_vis, thr_lvl_weather, thr_lvl_wind):
    """function colours each item of weather RIGHT of dash depending on in weach thereat category it belongs
    This function uses colouring.py/ SignificantColouring  class"""

    for n in range(1, len(weather_data)):
        becmg_time_group_coloring_list.append([])
        wind = weather_data[n]['wind']
        wind = SignificantColouring(wind)
        weather_data[n]['wind'] = wind.colour_wind_list()[1]
        #thr_lvl_wind.append(wind.colour_wind_list()[1])

        vis = weather_data[n]['vis']
        vis = SignificantColouring(vis)
        weather_data[n]['vis'] = vis.colour_vis_list()[1] #[1] because it contains ther lvl and value of wx
        #thr_lvl_vis.append(vis.colour_vis_list()[1])

        weather = weather_data[n]['weather']
        weather = SignificantColouring(weather)
        weather_data[n]['weather'] = weather.colour_weather_list()[1]
        #thr_lvl_weather.append(weather.colour_weather_list()[1])

        clouds = weather_data[n]['clouds']
        clouds = SignificantColouring(clouds)
        weather_data[n]['clouds'] = clouds.colour_cloud_list()[1]
        #thr_lvl_clouds.append(clouds.colour_cloud_list()[1])

#########
def create_thr_lvl_data_list(weather_data,weather_data_copy, settings):
    """extracting data from 'weather_data' to create 'thr_lvl_data' list"""
    thr_lvl_data =[]
    for n in range(len(weather_data)):
        thr_lvl_data.append({
            #'n': weather_data[n]['n'],
            'type': weather_data[n]['type'],
            'time_group': weather_data_copy[n]['time_group'], #copy is used to get not coloured data. 'time_group' has to be coloured from the start as parts of weather which are green may indicate that this part is significatn however for threat it is not
            'wind': weather_data[n]['wind'],
            'vis': weather_data[n]['vis'],
            'weather': weather_data[n]['weather'],
            'clouds': weather_data[n]['clouds'],

        })
        if thr_lvl_data[n]['type'] == 'Initial':
            thr_lvl_data[n]['type'] = settings.initial_type_rename
    return thr_lvl_data
###############################################################12start
#LEVEL 1#
def add_relevance_to__type__and__time_group(BECMG_color, TEMPO_color, grayed_area_right, thr_lvl_data):
    for n in range(len(thr_lvl_data)):
        # adding extra data to 'type' key
        line_status = set([])  # stores data relevant for colouring of type - is any item relevant or not and if it is TEMPO or BCMG or Init
            # using  set() to avoid duplicates
        # relevance flag - is line relevant TEMPO, relevant BECMG or not-relevant
        if n > 0:
            check_relevance_of_items_in_line(line_status, n, thr_lvl_data)
            add_relevance_to_time_group(line_status, n, thr_lvl_data)
            colour_change_base_on_relevance__type(BECMG_color, TEMPO_color, grayed_area_right, n, thr_lvl_data)
            colour_change_base_on_relevance__time_group(BECMG_color, TEMPO_color, grayed_area_right, n, thr_lvl_data)

#LEVEL 2#
def check_relevance_of_items_in_line(line_status, n, thr_lvl_data):
    """checks if wind, vis, weather or clouds are revlevant or not-relevant
    and based on this gives relvant or not-relevant 'line_status'"""
    for k, v in thr_lvl_data[n].items():
        if k == 'wind' or k == 'vis' or k == 'weather' or k == 'clouds':
            if v != []:
                for item in v:
                    if 'not-relevant TEMPO' in item or 'not-relevant BECMG' in item:
                        line_status.add('not-relevant')
                    elif 'relevant TEMPO' in item:
                        line_status.add('relevant TEMPO')
                    elif 'relevant BECMG' in item:
                        line_status.add('relevant BECMG')
                    else:
                        print('error 141')
                        quit()

def colour_change_base_on_relevance__time_group(BECMG_color, TEMPO_color, grayed_area_right, n, thr_lvl_data):
    """changing colour of 'time_group' group depending on relevance flag"""
    t_g = thr_lvl_data[n]['time_group']

    if t_g[1] == 'not-relevant':
        thr_lvl_data[n]['time_group'][0] = grayed_area_right(t_g[0])
    elif t_g[1] == 'relevant BECMG':
        thr_lvl_data[n]['time_group'][0] = BECMG_color(t_g[0])
    elif t_g[1] == 'relevant TEMPO':
        thr_lvl_data[n]['time_group'][0] = TEMPO_color(t_g[0])
    else:
        print('T_d.error 1231-3 -check code here')
        quit()

def colour_change_base_on_relevance__type(BECMG_color, TEMPO_color, grayed_area_right, n, thr_lvl_data):
    """changing colour of 'type' group depending on relevance flag"""
    t = thr_lvl_data[n]['type']
    if t[1] == 'not-relevant':
        thr_lvl_data[n]['type'][0] = grayed_area_right(t[0])
    elif t[1] == 'relevant BECMG':
        thr_lvl_data[n]['type'][0] = BECMG_color(t[0])
    elif t[1] == 'relevant TEMPO':
        thr_lvl_data[n]['type'][0] = TEMPO_color(t[0])
    else:
        print('T_d.error 1231-2 -check code here')
        quit()

def add_relevance_to_time_group(line_status, n,thr_lvl_data):
    ## adding 'relevant' data to 'time_group' (##)
    t = thr_lvl_data[n]['type']
    t_g = thr_lvl_data[n]['time_group']

    if 'relevant BECMG' in line_status:
        thr_lvl_data[n]['type'] = [t, 'relevant BECMG']
        thr_lvl_data[n]['time_group'] = [t_g, 'relevant BECMG']  ##
    elif 'relevant TEMPO' in line_status:
        thr_lvl_data[n]['type'] = [t, 'relevant TEMPO']
        thr_lvl_data[n]['time_group'] = [t_g, 'relevant TEMPO']  ##
    elif ('relevant BECMG' not in  line_status or 'relevant TEMPO' not in line_status) and 'not-relevant' in line_status:
        thr_lvl_data[n]['type'] = [t, 'not-relevant']
        thr_lvl_data[n]['time_group'] = [t_g, 'not-relevant']
    else:
        print('T_d.error 1231-1 check code here - conflicting codes in  linestatus')
        print(line_status)
        quit()
    # if line_status == {'not-relevant'}:
    #     thr_lvl_data[n]['type'] = [t, 'not-relevant']
    #     thr_lvl_data[n]['time_group'] = [t_g, 'not-relevant']  ##
    # elif line_status == {'relevant BECMG'}:
    #     thr_lvl_data[n]['type'] = [t, 'relevant BECMG']
    #     thr_lvl_data[n]['time_group'] = [t_g, 'relevant BECMG']  ##
    # elif line_status == {'relevant TEMPO'}:
    #     thr_lvl_data[n]['type'] = [t, 'relevant TEMPO']
    #     thr_lvl_data[n]['time_group'] = [t_g, 'relevant TEMPO']  ##
    # else:
    #     print('T_d.error 1231-1 check code here')
    #     print(line_status)
    #     quit()

def create_list_of_thr_lvl_weather(thr_lvl_data, settings,print_type, print_time_group):
    all_lines = []
    for n in range(len(thr_lvl_data)):
        # creating one line print
        one_line = []
        if n == 0:
            if len(thr_lvl_data[n]['wind']) > 1:
                one_line.append(thr_lvl_data[n]['wind'][1])
            elif len(thr_lvl_data[n]['wind']) == 1:
                one_line.append(thr_lvl_data[n]['wind'][0] + '- selected time out of TAF range')
            else:
                print('error 3144 - check code here')
                quit()
        elif n > 0:
            for k in thr_lvl_data[n].keys():
                data_for_key = thr_lvl_data[n][k]
                #adding data to one_line depending if relevant and depending which is line threat level
                if (k == 'type' and print_time_group) or (k == 'time_group' and print_type):
                    if data_for_key[1] == 'not-relevant' and settings.print_grayed_out:
                        one_line.append(data_for_key[1])
                    elif data_for_key[1] != 'not-relevant':
                        if settings.print_severe and data_for_key[0] == 'severe':
                            one_line.append(data_for_key[1])
                        if settings.print_warnings and data_for_key[0] == 'warning':
                            one_line.append(data_for_key[1])
                        if settings.print_cautions and data_for_key[0] == 'caution':
                            one_line.append(data_for_key[1])
                        if settings.print_green and data_for_key[0] == 'green':
                            one_line.append(data_for_key[1])

                elif k == 'wind' or k == 'vis' or k == 'weather' or k == 'clouds':
                    if data_for_key != []:
                        for i in data_for_key:
                            if (i[3] == 'not-relevant TEMPO' or i[3] == 'not-relevant BECMG') and settings.print_grayed_out:
                                one_line.append(i[1])
                            elif i[3] != 'not-relevant TEMPO' and i[3] != 'not-relevant BECMG':
                                if settings.print_green and i[0] == 'green':
                                    one_line.append(i[1])
                                if settings.print_cautions and i[0] == 'caution':
                                    one_line.append(i[1])
                                if settings.print_warnings and i[0] == 'warning':
                                    one_line.append(i[1])
                                if settings.print_severe and i[0] == 'severe':
                                    one_line.append(i[1])
        all_lines.append(one_line)
    return all_lines

def find_max_threat_level_in_one_line(thr_lvl_data):
    max_threat_level_in_one_line = []
    for n in range(1, len(thr_lvl_data)):
        # creating list of threat level of each item in TAF one line
        threats_in_one_line = []
        for k in thr_lvl_data[n].keys():
            data_for_key = thr_lvl_data[n][k]
            if data_for_key != []:
                if k == 'wind' or k == 'vis' or k == 'weather' or k == 'clouds':
                    for i in data_for_key:
                        if i[3] == 'relevant TEMPO' or i[3] == 'relevant BECMG':
                            threats_in_one_line.append(i[0])
                        elif i[3] == 'not-relevant TEMPO' or i[3] == 'not-relevant BECMG':
                            pass
                        else:
                            print('error T_d 1414 - edit code here')
                            quit()

        # searching highest threat level in one line of TAF
        if 'severe' in threats_in_one_line:
            max_threat_level_in_one_line.append('severe')
        elif 'warning' in threats_in_one_line:
            max_threat_level_in_one_line.append('warning')
        elif 'caution' in threats_in_one_line:
            max_threat_level_in_one_line.append('caution')
        elif 'green' in threats_in_one_line:
            max_threat_level_in_one_line.append('green')
        elif not threats_in_one_line:
            max_threat_level_in_one_line.append('LINE not-relevant')

    return max_threat_level_in_one_line

def finding_max_threat_level_at_the_airport(max_threat_level_in_one_line):
    # finding max threat level at the airport
    max_threat_level_at_airport = []
    if 'severe' in max_threat_level_in_one_line:
        max_threat_level_at_airport.append('severe')
    elif 'warning' in max_threat_level_in_one_line:
        max_threat_level_at_airport.append('warning')
    elif 'caution' in max_threat_level_in_one_line:
        max_threat_level_at_airport.append('caution')
    elif 'green' in max_threat_level_in_one_line:
        max_threat_level_at_airport.append('green')
    elif 'LINE not-relevant' in max_threat_level_in_one_line:
        max_threat_level_at_airport.append('not-relevant')
    return max_threat_level_at_airport

def adding_threat_level_data_of__type__and_time_group__to__thr_lvl_data(max_threat_level_in_one_line, thr_lvl_data):
    for n in range(1, len(thr_lvl_data)):
        for k in thr_lvl_data[n].keys():
            data_for_key = thr_lvl_data[n][k]

            if k == 'type' or k == 'time_group':
                data_for_key = [max_threat_level_in_one_line[n - 1]] + data_for_key
                thr_lvl_data[n][k] = data_for_key

def change_colour_of__type__and__time_group_to_match_max_thr_lvl_in__one_line(thr_lvl_data, thr_lvl_data_copy, settings):
    # changing colour of 'type' and 'time_group' to mach max threat level in one line
    for n in range(1, len(thr_lvl_data)):
        for k in thr_lvl_data[n].keys():
            data_for_key = thr_lvl_data[n][k]
            if (k == 'type' and settings.type_coloured_max_thr_lvl_in_line) or \
                    (k == 'time_group' and settings.time_group_coloured_max_thr_lvl_in_line):
                if data_for_key[0] == 'severe':
                    data_for_key[1] = colouring.severe_colour(thr_lvl_data_copy[n][k])
                elif data_for_key[0] == 'warning':
                    data_for_key[1] = colouring.warning_colour(thr_lvl_data_copy[n][k])
                elif data_for_key[0] == 'caution':
                    data_for_key[1] = colouring.caution_colour(thr_lvl_data_copy[n][k])
                elif data_for_key[0] == 'green':
                    data_for_key[1] = colouring.green_color(thr_lvl_data_copy[n][k])

def colouring_airport_in_thr_lvl_data(thr_lvl_data, thr_lvl_data_copy, grayed_area_right):
    '''colouring airport name in thr_lvl_data'''
    n = 0
    data_for_key = thr_lvl_data[n]['wind']
    if data_for_key[0] == 'severe':
        data_for_key[1] = colouring.severe_colour(thr_lvl_data_copy[n]['wind'][0])
    elif data_for_key[0] == 'warning':
        data_for_key[1] = colouring.warning_colour(thr_lvl_data_copy[n]['wind'][0])
    elif data_for_key[0] == 'caution':
        data_for_key[1] = colouring.caution_colour(thr_lvl_data_copy[n]['wind'][0])
    elif data_for_key[0] == 'green':
        data_for_key[1] = colouring.green_color(thr_lvl_data_copy[n]['wind'][0])
    elif data_for_key[0] == 'not-relevant':
        data_for_key[1] = grayed_area_right(thr_lvl_data_copy[n]['wind'][0])
    else:
        print('error - 575')

    # airport name - making text bold and inverting colours
    if len(data_for_key) > 1:
        data_for_key[1] = colouring.bold_text(data_for_key[1])
        data_for_key[1] = colouring.colour_Inverse(data_for_key[1])

def adding_threat_level_data_of__type__and_t_ime_group__to__thr_lvl_data(max_threat_level_in_one_line, thr_lvl_data):
    for n in range(1, len(thr_lvl_data)):
        for k in thr_lvl_data[n].keys():
            data_for_key = thr_lvl_data[n][k]
            if k == 'type' or k == 'time_group':
                data_for_key = [max_threat_level_in_one_line[n - 1]] + data_for_key
                thr_lvl_data[n][k] = data_for_key

def adding_coloured_station_name(thr_lvl_data):
    # adding coloured station name - required for later printing of data
    if len(thr_lvl_data[0]['wind']) > 1:
        colored_station_name = thr_lvl_data[0]['wind'][1]
        return colored_station_name
    elif len(thr_lvl_data[0]['wind']) == 1:
        colored_station_name = thr_lvl_data[0]['wind'][0]
        return colored_station_name
    else:
        print('error 5326 - check code here')
        quit()

def     generate_station_threats(all_lines,settings):
    station_threats =''
    if settings.print_in_one_line:
        s = ''
        for l in all_lines:
            for i in l:
                s = s + ' ' + i
        station_threats += s
    if settings.print_in_one_line and settings.print_in_multiple_lines:
        station_threats+= '\n\n'

    if settings.print_in_multiple_lines:
        for l in all_lines:
            s = ''
            if l != []:  # skip printing of line if line is empty
                for i in l:
                    s = s + ' ' + i
                station_threats += s + '\n'

    return station_threats
###############################################################12end

# add new functions here
def prLightGray(skk):
    return "\033[1;90;40m" + str(skk)

def avaliable_rwys(apt_code, settings):
    """ CORE FUNCTION - adds runway idents and runway length to the final data"""

    # Loading json object containing data regarding runways
    path = "Data_new/airports_cleaned.json"
    with open(path, 'r') as f_obj:
        airport_cleaned = json.load(f_obj)


    # Collecting all runway info in one list - each runway is in separate file in json file
    runways=[]
    for i in range(len(airport_cleaned["airport_ident"])):
        # Searching for selected airport identification
        if airport_cleaned["airport_ident"][i]==apt_code:

            # Collecting runway low_end / high end runway data in one dictionary
            runways.append({
                "le_runway":{
                    "length__meters": airport_cleaned["length__meters"][i] - airport_cleaned["le_displaced_threshold__meters"][i],
                    "width__meters": airport_cleaned["width__meters"][i],
                    "ident": airport_cleaned["le_ident"][i],
                    "heading_degT": airport_cleaned["le_heading_degT"][i],
                    "displaced_threshold__meters": airport_cleaned["le_displaced_threshold__meters"][i],
                },

                "he_runway":{
                    "length__meters": airport_cleaned["length__meters"][i] - airport_cleaned["he_displaced_threshold__meters"][i],
                    "width__meters": airport_cleaned["width__meters"][i],
                    "ident":        airport_cleaned["he_ident"][i],
                    "heading_degT": airport_cleaned["he_heading_degT"][i],
                    "displaced_threshold__meters":   airport_cleaned["he_displaced_threshold__meters"][i],}
                })

    # Making runway information ready for display
    runway_info_for_display=[]
    for runway in runways:
        # Extracting data from dictionary
        le_len = runway["le_runway"]["length__meters"]
        le_width = runway["le_runway"]["width__meters"]

        he_len = runway["he_runway"]["length__meters"]
        he_width = runway["he_runway"]["width__meters"]

        le_name = runway["le_runway"]["ident"]
        he_name = runway["he_runway"]["ident"]

        # Rounding runway length
        le_len = math.floor(le_len/ 100) * 100
        he_len = math.floor(he_len / 100) * 100


        # Getting color changeover thresholds from settings
        s_rwy = settings.short_runway
        m_rwy = settings.medium_runway
        l_rwy = settings.long_runway
        vl_rwy = settings.very_long_runway



        # RUNWAY LENGTH string recolouring depending on its LENGTH
           # Initializing variables
        le_len_str = 'xx'
        he_len_str = 'xx'

          # recolouring LOW END threshold
        if le_len < s_rwy:
            le_len_str = prLightGray(str(le_len))
        elif le_len < m_rwy:
            le_len_str = prRed(str(le_len))
        elif le_len < l_rwy:
            le_len_str = prYellow(str(le_len))
        elif le_len >= l_rwy:
            le_len_str = prGreen(str(le_len))

            # Recoloring of HI END threshold
        if he_len < s_rwy:
            he_len_str = prLightGray(str(he_len))
        elif he_len < m_rwy:
            he_len_str = prRed(str(he_len))
        elif he_len < l_rwy:
            he_len_str = prYellow(str(he_len))
        elif he_len >= l_rwy:
            he_len_str = prGreen(str(he_len))

        # RUNWAY NAME recolouring - it becomes gray for VERY SHORT runway
        if le_len < s_rwy:
            le_name = prLightGray(le_name)
        if he_len < s_rwy:
            he_name = prLightGray(he_name)

            # If runway is narrow then width becomes RED
        if le_width<settings.normal_width_runway:
            le_width = prRed(le_width)

        # Concatenating single runway data into one string
        if le_len == he_len:
            # Runway is same length for both landing direction
            runway_info_for_display.append(
                f"{le_name}|{he_name} {le_len_str}({le_width})")
        else:
            # Different lengths for both ends
            runway_info_for_display.append(
                f"{le_name}|{he_name} {le_len_str}({le_width}){he_len_str}")

    ## COMBINING RUNWAY INFO INTO ONE STRING
    runways_info_for_display = '   '.join(runway_info_for_display)
    return runways_info_for_display

def load_avlb_apprs_datra():
    # Load the database containing all airports APPROACH DATA.
    # This data was generated using external python program!

    filename = "Data/avlb_apprs_data.json"

    with open(filename,"r") as f_obj:
        avlb_apprs_data = json.load(f_obj)

    return avlb_apprs_data


def generate_coloured(key, weather_data, n):
    """internal fucntion"""
    w = weather_data[n][key]
    if w == []:
        return ''

    elif w != []:
        string = ''
        for i in w:
            string += ' ' + str(i[1])
        return string

    else:
        print('error - 352')
        quit()

def generate_decoded_TAF(settings,BECMG_color, error_added, error_found, grayed_area_right, weather_data, gr_data):
    """Final print out of coloured TAF"""
    # IMPORTANT!!! first line of coloured TAF
    airport_time_line = gr_data[0]['groups_strings']
    final_coloured_taf_list = [BECMG_color(airport_time_line)]

    # Generating coloured TAF line by line
    for n in range(1, len(weather_data)):
        vis = generate_coloured('vis', weather_data, n)
        wind = generate_coloured('wind', weather_data, n)
        clouds = generate_coloured('clouds', weather_data, n)
        weather = generate_coloured('weather', weather_data, n)

        typ = weather_data[n]['group_type_long']
        gap = weather_data[n]['gap']
        time = weather_data[n]['time_group']

        # Introduces line separation after type of the time group (2022.10)
        if not settings.gap_active:
            s = f'space.Tdf{typ} newlinee.Tdf{time}' # has to newlinee.Tdf - is a placeholder for new line symbol - it is being escaped otherwise. It is being replaced in the main.py file
        else:
            s = f'{typ} {time}'

        s = s.replace(grayed_area_right([]), '')
        s = ' '.join(s.split())
        s = gap + s

        ss = ''
        """this part is checking if max and min temp is entered to TAF
        in case this generates error - leave only 
        ss = ' ' + wind + ' ' + vis + ' ' + weather + ' ' + clouds"""

        try:
            temp_max = weather_data[n]['temp_max']
        except KeyError:
            try:
                temp_min = weather_data[n]['temp_min']
            except KeyError:
                ss = ' ' + wind + ' ' + vis + ' ' + weather + ' ' + clouds
            else:
                ss = ' ' + wind + ' ' + vis + ' ' + weather + ' ' + clouds + ' ' + ' ' + BECMG_color(
                    temp_min)
        else:
            try:
                temp_min = weather_data[n]['temp_min']
            except KeyError:
                ss = ' ' + wind + ' ' + vis + ' ' + weather + ' ' + clouds + ' ' + BECMG_color(
                    temp_max)
            else:
                ss = ' ' + wind + ' ' + vis + ' ' + weather + ' ' + clouds + ' ' + BECMG_color(
                    temp_max) + ' ' + BECMG_color(temp_min)
        ss = ss.replace(grayed_area_right([]), '')  ##  removes empty lists
        ss = ' '.join(ss.split())  # important line! removes unnecessary spaces
        final_string = s + ' ' + ss

        # adding  words to a coloured TAF which are not recognised durig whole process
        split_l = final_string.split()  # splitting into a list of strings
        for s in error_found:  # adding
            if s[0] == n and n != 1:

                split_l.insert(s[1], error_added(s[2]))

            elif s[0] == n and n == 1:
                #special case for n =1, number has to be added one spot further than n suggests

                split_l.insert(s[1] + 1, error_added(s[2]))
        sss = ' '.join(split_l)  # once error words added to list it is joined
        # back to a string
        sss = gap + sss  # has to be added again because it was removed in the

        final_coloured_taf_list.append(sss)

    # Converting list to string
    final_coloured_taf_string = '\n'.join(final_coloured_taf_list)

    return  final_coloured_taf_string

def generate_appr_info(TAF, settings):
    """Generating available approaches info and also LDAs """
    end_string = ''
    avlb_apprs_data = load_avlb_apprs_datra()
    for appr_data in avlb_apprs_data:
        if appr_data[0] in TAF:
            end_string = appr_data[1]

    if settings.print_all_rwys_data_below_taf:
        if not end_string:
            end_string = '                   ---- no rwy data ---'

    else:
        end_string = '-- RWY DATA OFF --'
    return end_string

def creating_start_end_times_dates(settings,time_group_list, Tdf, time_gr_data):
    # ref('extracting time range in hours')
    # ref('[start_date, start_hour, end_date,end_hour, diff]')
    hours_list = []
    for n in range(len(time_group_list)):
        fm_in = False
        if 'FM' in time_group_list[n]:
            fm_in = True
        if settings.printing_active:
            print(fm_in)

        sliced_word = Td_helpers.string_to_list(time_group_list[n])
        if settings.printing_active:
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
            # if settings.printing_active:
            #     print('digit', sum(digit))
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
    Td_helpers.add_to_dict_TIME_gr_data(hours_list, 'hours_list', time_gr_data)

def creating_type_of_group(settings,time_string_uncorrected, TAF_split, station_name, time_gr_data):
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
        elif settings.no_publication_time_not_an_error == True \
                and (len(one_before) == 4 and one_before.isalpha()):
            type_of_group.append('Initial')
        elif settings.no_publication_time_not_an_error == False \
                and 'Z' in one_before and one_before.isalpha() == False:
            type_of_group.append('Initial')
        elif 'Z' in one_before and one_before.isalpha() == False :
            type_of_group.append('Initial')
        else:
            type_of_group.append('error type')

    Td_helpers.add_to_dict_TIME_gr_data(type_of_group, "type_of_group", time_gr_data)

def creating_weather_data_list(settings,gr_data, type_of_group, reference, score):
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
                vis_list = Td_helpers.string_to_list(p)
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
                    if settings.printing_active:
                        print(p, 'wwwwwwwwwwwww')
                    weather_data_dict['wind'].append(p)
                    score.append([n, l])
            clouds = ['SKC', 'NSC', 'VV', 'FEW', 'SCT', 'BKN', 'OVC', ]

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

def transferring_group_type_from_time_gr_data_to_weather_data(time_gr_data, weather_data):

    typ = ['none']
    for n in range(len(time_gr_data)):
        gr_type = time_gr_data[n]['type_of_group']
        typ.append(gr_type)
    for n in range(len(typ)):
        weather_data[n]['type'] = typ[n]

def add_to_dict_weather_data(lista,key, weather_data):
    # adds data to gr_data list of dictionaries, name of KEY has to be given
    if len(lista) == len(weather_data):
        for n in range(len(lista)):
            weather_data[n][key] = lista[n]
    else:
        print('\nERROR\n(3)Lenght of list do not match. Difference: '
              + str(len(weather_data) - len(lista)))
        exit()

def weather_for_selected_time_RIGHT(key_,settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack):
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
                                tempo_text = Td_helpers.TEMPO_color(skk)
                                i = tempo_text
                                weather_data[n][key_][m][1] = i
                                weather_data[n][key_][m].append('relevant TEMPO')

                            elif str('\x1b') in i[1]:
                                weather_data[n][key_][m].append('relevant TEMPO')

                            else:
                                print('error -121 - update code ')
                                quit()
                                skk = wx_key
                                tempo_text = Td_helpers.TEMPO_color(skk)
                                wx_key = tempo_text
                                weather_data[n][key_] = wx_key
                            m += 1

                elif typ == 'Initial' or typ == 'B' or typ == 'FM':
                    pass
                else:
                    print('unknown format\n', wx_key)

                    skk = wx_key
                    tempo_text = Td_helpers.TEMPO_color(skk)
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
            if settings.printing_active:
                print('filled', 'n=', n, 'typ', typ, key_, wx_key,
                      '\ntemp_range', temp_range, )
            ##print('IF',temp_range)

        elif settings.fm_canceling == 'y' and (
                typ == 'Initial' or typ == 'B') and wx_key == []:
            """fm canceling engine - description at INPUTS """
            if len(wx_key_bcmg) > 0:
                temp_range[-1] = \
                    [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                     weather_data[n]['modified_range'][1]]
                ##print('elif', temp_range)
        elif settings.fm_canceling == 'n' and (
                typ == 'Initial' or typ == 'B' or typ == 'FM') and wx_key == []:
            if len(wx_key_bcmg) > 0:
                temp_range[-1] = \
                    [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                     weather_data[n]['modified_range'][1]]

            if settings.printing_active:
                print('empty', 'n=', n, 'typ', typ, wx_key, '\ntemp_range',
                      temp_range, )

    if settings.printing_active:
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
        if settings.print_colouring_logic:
            print('ranges_data', ranges_data)

        if settings.becmg_cancelling_wind == 'n' and key_ == 'wind':
            wind_ranges.append(ranges_data)
        if settings.becmg_cancelling_wind == 'y' and key_ == 'time_group':
            wind_ranges.append(ranges_data)

        if settings.becmg_cancelling_vis == 'n' and key_ == 'vis':
            vis_ranges.append(ranges_data)
        if settings.becmg_cancelling_vis == 'y' and key_ == 'time_group':
            vis_ranges.append(ranges_data)

        if settings.becmg_cancelling_weather == 'n' and key_ == 'weather':
            weather_ranges.append(ranges_data)
        if settings.becmg_cancelling_weather == 'y' and key_ == 'time_group':
            weather_ranges.append(ranges_data)

        if settings.becmg_cancelling_clouds == 'n' and key_ == 'clouds':
            clouds_ranges.append(ranges_data)
        if settings.becmg_cancelling_clouds == 'y' and key_ == 'time_group':
            clouds_ranges.append(ranges_data)

        if len(stack2) > 0:  # significant time in range of temp range
            """part responsible for colouring BECMG Initial and FM group
            stack2 - indicattes that  part is in significant time"""

            if not (wx_key_bcmg[nn] == 1 and key_ == 'time_group'):
                """ wind, BECMG_colour, except Initial  """
                if type(wx_key) == list:
                    m = 0
                    for i in wx_key:

                        if settings.printing_active:
                            print(i, 'list L')

                        if str('\x1b') not in i[1]:
                            becmg_text = i[1]
                            i = Td_helpers.BECMG_color(becmg_text)
                            weather_data[wx_key_bcmg[nn]][key_][m][1] = i

                        m += 1

                elif type(wx_key) == str:
                    print('error 542 - update code here')
                    quit()
                    if settings.printing_active:
                        print(wx_key, 'string S')
                    becmg_text = wx_key
                    wx_key = Td_helpers.BECMG_color(becmg_text)
                    weather_data[wx_key_bcmg[nn]][key_] = wx_key

            if wx_key_bcmg[nn] == 1 and sum(
                    init_stack) == 0:  # if segment necessary to colour the time_group of Initial. Whithout this line Initial time_group will never be painted because time_group is never empty, so BECMG never fall back on initial group whenever ther is any BECMG group
                """ colouring of Initial - to be checked for selective fall back"""
                if settings.printing_active:
                    print('nn==1', key_)
                weather_data[1]['time_group'] = \
                    Td_helpers.BECMG_color(weather_data[1]['time_group'])
                init_stack.append(1)
            if not wx_key_bcmg[nn] == 1 and key_ == 'time_group':
                becmg_text = wx_key
                wx_key = Td_helpers.BECMG_color(becmg_text)
                weather_data[wx_key_bcmg[nn]][key_] = wx_key

        elif len(stack2) == 0 and key_ == 'time_group':
            if settings.becmg_cancelling_wind == 'n' \
                    or settings.becmg_cancelling_vis == 'n' \
                    or settings.becmg_cancelling_weather == 'n' \
                    or settings.becmg_cancelling_clouds == 'n':
                for l in weather_ranges:
                    if l[2] == n:
                        if settings.printing_active:
                            print('sssssss', weather_ranges)
                        becmg_text = wx_key
                        wx_key = Td_helpers.BECMG_color(becmg_text)
                        weather_data[n][key_] = wx_key
                        if settings.printing_active:
                            print('vvvvvv', n, weather_data[n][key_])

def weather_for_selected_time(key_, settings, weather_data, significant_time, tempo_line_n, wind_ranges, vis_ranges, weather_ranges, clouds_ranges, init_stack):
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
                                    tempo_text = Td_helpers.TEMPO_color(skk)
                                    i = tempo_text
                                    weather_data[n][key_][m] = i
                                m += 1
                        else:
                            if type(wx_key) == list:
                                m = 0
                                for i in wx_key:
                                    if str('\x1b') not in i:
                                        skk = i
                                        tempo_text = Td_helpers.TEMPO_color(skk)
                                        i = tempo_text
                                        weather_data[n][key_][m] = i
                                    m += 1

                            else:
                                skk = wx_key
                                tempo_text = Td_helpers.TEMPO_color(skk)
                                wx_key = tempo_text
                                weather_data[n][key_] = wx_key

                    elif typ == 'Initial' or typ == 'B' or typ == 'FM':
                        pass
                    else:
                        print('unknown format\n', wx_key)

                        skk = wx_key
                        tempo_text = Td_helpers.TEMPO_color(skk)
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
                if settings.printing_active:
                    print('filled', 'n=', n, 'typ', typ, key_, wx_key,
                          '\ntemp_range', temp_range, )
                ##print('IF',temp_range)

            elif settings.fm_canceling == 'y' and (
                    typ == 'Initial' or typ == 'B') and wx_key == []:
                """fm canceling engine - description at INPUTS """
                if len(wx_key_bcmg) > 0:
                    temp_range[-1] = \
                        [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                         weather_data[n]['modified_range'][1]]
                    ##print('elif', temp_range)
            elif settings.fm_canceling == 'n' and (
                    typ == 'Initial' or typ == 'B' or typ == 'FM') and wx_key == []:
                if len(wx_key_bcmg) > 0:
                    temp_range[-1] = \
                        [weather_data[wx_key_bcmg[-1]]['modified_range'][0],
                         weather_data[n]['modified_range'][1]]

                if settings.printing_active:
                    print('empty', 'n=', n, 'typ', typ, wx_key, '\ntemp_range',
                          temp_range, )

        if settings.printing_active:
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
            if settings.print_colouring_logic:
                print('ranges_data',ranges_data)

            if settings.becmg_cancelling_wind == 'n' and key_ == 'wind':
                wind_ranges.append(ranges_data)
            if settings.becmg_cancelling_wind == 'y' and key_ == 'time_group':
                wind_ranges.append(ranges_data)

            if settings.becmg_cancelling_vis == 'n' and key_ == 'vis':
                vis_ranges.append(ranges_data)
            if settings.becmg_cancelling_vis == 'y' and key_ == 'time_group':
                vis_ranges.append(ranges_data)

            if settings.becmg_cancelling_weather == 'n' and key_ == 'weather':
                weather_ranges.append(ranges_data)
            if settings.becmg_cancelling_weather == 'y' and key_ == 'time_group':
                weather_ranges.append(ranges_data)

            if settings.becmg_cancelling_clouds == 'n' and key_ == 'clouds':
                clouds_ranges.append(ranges_data)
            if settings.becmg_cancelling_clouds == 'y' and key_ == 'time_group':
                clouds_ranges.append(ranges_data)

            if len(stack2) > 0:  # significant time in range of temp range
                """part responsible for colouring BECMG Initial and FM group
                stack2 - indicattes that  part is in significant time"""

                if not (wx_key_bcmg[nn] == 1 and key_ == 'time_group'):
                    """ wind, BECMG_colour, except Initial  """
                    if type(wx_key) == list:
                        m = 0
                        for i in wx_key:
                            if settings.printing_active:
                                print(i, 'list L')

                            if str('\x1b') not in i:
                                becmg_text = i
                                i = Td_helpers.BECMG_color(becmg_text)
                                weather_data[wx_key_bcmg[nn]][key_] = i

                            m += 1

                    elif type(wx_key) == str:
                        if settings.printing_active:
                            print(wx_key, 'string S')
                        becmg_text = wx_key
                        wx_key = Td_helpers.BECMG_color(becmg_text)
                        weather_data[wx_key_bcmg[nn]][key_] = wx_key

                if wx_key_bcmg[nn] == 1 and sum(
                        init_stack) == 0:  # if segment necessary to colour the time_group of Initial. Whithout this line Initial time_group will never be painted because time_group is never empty, so BECMG never fall back on initial group whenever ther is any BECMG group
                    """ colouring of Initial - to be checked for selective fall back"""
                    if settings.printing_active:
                        print('nn==1', key_)
                    weather_data[1]['time_group'] = \
                        Td_helpers.BECMG_color(weather_data[1]['time_group'])
                    init_stack.append(1)
                if not wx_key_bcmg[nn] == 1 and key_ == 'time_group':
                    becmg_text = wx_key
                    wx_key = Td_helpers.BECMG_color(becmg_text)
                    weather_data[wx_key_bcmg[nn]][key_] = wx_key

            elif len(stack2) == 0 and key_ == 'time_group':
                if settings.becmg_cancelling_wind == 'n' \
                        or settings.becmg_cancelling_vis == 'n' \
                        or settings.becmg_cancelling_weather == 'n' \
                        or settings.becmg_cancelling_clouds == 'n':
                    for l in weather_ranges:
                        if l[2] == n:
                            if settings.printing_active:
                                print('sssssss', weather_ranges)
                            becmg_text = wx_key
                            wx_key = Td_helpers.BECMG_color(becmg_text)
                            weather_data[n][key_] = wx_key
                            if settings.printing_active:
                                print('vvvvvv', n, weather_data[n][key_])

def colouring_outside_sgignificant(key_4, list_4, key, becmg_time_group_coloring_list, weather_data_copy, n, weather_data):
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
                    w = Td_helpers.grayed_area_right(w)
                    weather_data[n][key][m][1] = w # VERY IMPORTANT - data from copy - raw wather value without threat level is being coloured gray and than stored in original weather file at correct value location wiht already added threat level
                    # adding info to weather value that this part of weather in BECMG is not relevant for selected time period
                    weather_data[n][key][m].append('not-relevant BECMG') # VERY IMPORTANT!
                    m += 1
            else:
                pass

def geting_day_start(significant_time, day_left, day_right):
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

def getting_day_end(significant_time, day_left, day_right):
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
            day_end = day_right - 1
            return day_end
    elif 48 <= significant_time[-1] < 72:
        day_end = day_right
        return day_end


def generate_selected_time_info(significant_time, weather_data_copy, colored_station_name, start_hour, end_hour, TAF) :
    """Function that generates information line about selected start and end of the period"""
    try:
        s_from = [math.floor(significant_time[0] / 24) + 1,
                  significant_time[0] % 24]
        s_to = math.floor(significant_time[-1] / 24) + 1, significant_time[
            -1] % 24
        # print('----------FINAL TAF ----------------')
        # print(f' day:{my_day} time:{my_time_copy}, '

        day_left = int(weather_data_copy[1]['time_group'][0:2])
        day_right = int(weather_data_copy[1]['time_group'][5:7])

        day_start=geting_day_start(significant_time, day_left, day_right)
        day_end = getting_day_end(significant_time, day_left, day_right)

        # Generating ICAO station name in different colour depending what is the maximum threat level of wather at the airport

        selected_period =f'{colored_station_name}     /{day_start}/ {s_from[1]}:00  -> /{day_end}/ {s_to[1]+1}:00   ({start_hour},{end_hour})'

    except IndexError:
        selected_period ='\n\t\t\t'+ TAF +'(TDf. kkk)\n'

        pass
    return selected_period