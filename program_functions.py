"""function which are not required in a core file"""
from colouring import SignificantColouring
import colouring
import json
from colouring import prGreen, prYellow, prRed, prPurple
from settings import Settings
settings = Settings()


from avwx import Station

def print_list(lista):
    for i in lista:
        print(i)

def day_to_hours(day, hour):
    # modyfing my_time depending which day is selected
    if day == 1:
        return hour
    elif day == 2:
        return hour + 24
    elif day == 3:
        return hour + 48
    else:
        print('My day should be 1, 2 or 3.'
              'Setting default number 1')
        return hour

def out_of_validity_perriod_error_generator(initial_start, initial_end):
    out_of_r_error_msg = '----------------------------------------------------\
    \nOut of range. Try:'
    ending='(:59)'
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

def getting_significant_time_range(settings,my_day,my_time,initial_end,initial_start,significant_start_day, significant_start_hour, significant_end_day, significant_end_hour,significant_range,significant_range_active, cancel_out_of_range_msg):
    """function which checks if provided significant time range is corrextand also generates significant time list"""
    if significant_range_active:
        my_time = day_to_hours(my_day,my_time)
        print('pf.dddd', my_time)
        if my_time > initial_end or my_time < initial_start:
            out_of_validity_perriod_error_generator(initial_start, initial_end)
        significant_start = -significant_range
        significant_end = significant_range + 1

        significant_time = []

        for n in range(significant_start, significant_end):
            t = my_time + n
            if initial_start <= t <= initial_end:
                significant_time.append(t)
        return [significant_time,significant_start,significant_end]

    elif not significant_range_active:
        significant_start_hour = day_to_hours(significant_start_day,significant_start_hour)
        significant_end_hour = day_to_hours(significant_end_day, significant_end_hour)
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


def print_final_all_lines_data(all_lines,settings):
    final_line =''
    if settings.print_in_one_line:
        s = ''
        for l in all_lines:
            for i in l:
                s = s + ' ' + i
        final_line += s
    if settings.print_in_one_line and settings.print_in_multiple_lines:
        final_line+= '\n\n'

    if settings.print_in_multiple_lines:
        for l in all_lines:
            s = ''
            if l != []:  # skip printing of line if line is empty
                for i in l:
                    s = s + ' ' + i
                final_line += s + '\n'

    return final_line
###############################################################12end

# add new functions here
def prLightGray(skk):
    return "\033[1;90;40m" + str(skk)

def avaliable_rwys(apt_code):
    """ CORE FUNCTION - adds runway idents and runway length to the final data"""
    station = Station.from_icao(apt_code)
    #print(epwa.type, epwa.city,epwa.country, epwa.runways)

    min_rwy_len = settings.short_runway
    min_rwy_width = settings.narrow_runway

    runways =[]
    for runway in station.runways:
        r_length = round(runway.length_ft*0.3048)
        r_width = round(runway.width_ft*.3048)
        r_idents = [runway.ident1, runway.ident2]
        rwy_name = '|'.join(r_idents)

        s_rwy = settings.short_runway
        m_rwy = settings.medium_runway
        l_rwy = settings.long_runway
        vl_rwy = settings.very_long_runway

        # RUNWAY LENGHT COLOURING
        if r_length < s_rwy:
            rwy_len_str = prLightGray(str(r_length))
        elif r_length < m_rwy:
            rwy_len_str = prRed(str(r_length))
        elif r_length < l_rwy:
            rwy_len_str = prYellow(str(r_length))
        elif r_length >= l_rwy:
            rwy_len_str = prGreen(str(r_length))

        # RUNWAY NAME COLOURIG
        if r_length < s_rwy:
            rwy_name = prLightGray(rwy_name)

        runways.append(rwy_name + ' ' + str(rwy_len_str))


    runway_string = ' '.join(runways)
    return runway_string

def load_avlb_apprs_datra():
    # Load the database containing all airports APPROACH DATA.
    # This data was generated using external python program!

    filename = "Data/avlb_apprs_data.json"

    with open(filename,"r") as f_obj:
        avlb_apprs_data = json.load(f_obj)

    return avlb_apprs_data



def final_coloured_TAF_printout(BECMG_color, error_added, error_found, grayed_area_right, weather_data, gr_data):
    """Final print out of coloured TAF"""
    # IMPORTANT!!! first line of coloured TAF
    airport_time_line = gr_data[0]['groups_strings']
    final_coloured_taf_list = [BECMG_color(airport_time_line)]

    # Printing out coloured TAF line by line
    for n in range(1, len(weather_data)):

        def print_coloured(key):
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

            # for pair in w:
            #     print('\tpair',pair)
            #     ('pair',pair)
            #     if type(pair) == list:
            #         print('pair[1]', pair[1])
            #         return pair[1]
            #
            #

        vis = print_coloured('vis')
        wind = print_coloured('wind')
        clouds = print_coloured('clouds')
        weather = print_coloured('weather')

        typ = weather_data[n]['group_type_long']
        gap = weather_data[n]['gap']
        time = weather_data[n]['time_group']

        s = typ + ' ' + time
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
    print('\nffff\n',final_coloured_taf_string)
    return  final_coloured_taf_string

def runway_data_below_TAF_printout(TAF):
    """Generating runway data below coloured TAF and printing out"""
    end_string = ''
    avlb_apprs_data = load_avlb_apprs_datra()
    for appr_data in avlb_apprs_data:
        if appr_data[0] in TAF:
            end_string = appr_data[1]
    if settings.print_all_rwys_data_below_taf:
        print('              . . .')
        if end_string:
            print(end_string)
        else:
            end_string = '                   ---- no rwy data ---'
            print(end_string)
    else:
        end_string = '-- RWY DATA OFF --'
    return end_string




