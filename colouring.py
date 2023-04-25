import re
from Classes.settings import Settings
settings = Settings()


# def prRed(skk):         return ("\033[91m{}\033[00m".format(skk))
# def prYellow(skk):      return ("\033[93m{}\033[00m".format(skk))
# def prLightPurple(skk): return ("\033[97m{}\033[00m".format(skk))
# def prPurple(skk):      return ("\033[95m{}\033[00m".format(skk))
# def prUnderlined(skk):  return ('\x1b[4;30;48m{}\x1b[0m'.format(skk))
# def prRedUnderlined(skk):  return ('\x1b[21;31;48m{}\x1b[0m'.format(skk))
# def prGreen(skk):         return ("\033[92m{}\033[00m".format(skk))
# def colour_Inverse(string):         return "\033[07m{}\033[00m".format(string)
# def bold_text(string):         return "\033[01m{}\033[00m".format(string)
def prLightGray(skk):    return f'[color=545454]{skk}[/color]'

def prRed(skk):         return f'[color=d6321c]{skk}[/color]'
def prYellow(skk):      return f'[color=d9a930]{skk}[/color]'
def prLightPurple(skk): return f'[color=ff75fd]{skk}[/color]'
def prPurple(skk):      return f'[color=8f068d]{skk}[/color]'
def prUnderlined(skk):  return f'[color=e8f1fc]{skk}[/color]'
def prRedUnderlined(skk):  return f'[u][color=940f5f]{skk}[/color][/u]'
def prGreen(skk):         return f'[color=117841]{skk}[/color]'
path = "Resources/Fonts/Consolas-Bold.ttf"
# def colour_Inverse(string):         return f'[size=30dp][font=Resources/Fonts/Consolas-Bold.ttf]{string}[/font][/size]'
def colour_Inverse(string):         return f'[size=26dp]{string}[/size]'
# def colour_Inverse(string):         return f'[ref=station]{string}[/re qf]'
def bold_text(string):         return f'[b]{string}[/b]'



weather = ['+SHSNRA', '+TS', 'DD', '+TSGR', 'NSW']
clouds = ['BN007', 'OVC004', 'OVC002', 'SCT003', 'VV001', "BKO002", 'BKN010CB',
          'SCT003TCU', 'BKN007', 'VV002', 'VV02', 'VV003', 'VV005', 'VV010']
winds = ['CALM', '92015MPS', '23012G40KT', '22005G26KT', '34011G12MPS',
         '13009G16KT', '21004G06MPS']
vis = ['5000', '3000', '0100', '////', 'CAVOK', '1 1/16SM', '1/16SM',
       '1/8SM', '2 1/4SM', 'P6SM', '5SM']


def error_color(string):
    """ error generated by SignificantCOlouring class"""
    string = prUnderlined(string)
    return string


def severe_colour(string):
    string = prRedUnderlined(string)
    return string


def warning_colour(string):
    string = prRed(string)
    return string


def caution_colour(string):
    string = prYellow(string)
    return string

def green_color(string):
    string = prGreen(string)
    return string


green = 'green'
caution = 'caution'
warning = 'warning'
magenta = 'severe'
error = 'error'

# string which will be added to weather value like threat level
clouds_ref = 'clouds'
vis_ref = 'vis'
wx_ref = 'weather'
wind_ref = 'wind'



def colour_station_name(station_name, thr_lvl):
    """colour station_name depending on what is threat_level """
    if thr_lvl == 'error':
        station_name = error_color(station_name)
        return colour_Inverse(station_name)
    elif thr_lvl == 'severe':
        station_name = severe_colour(station_name)
        return bold_text(colour_Inverse(station_name))
    elif thr_lvl == 'warning':
        station_name = warning_colour(station_name)
        return bold_text(colour_Inverse(station_name))
    elif thr_lvl == 'caution':
        station_name = caution_colour(station_name)
        return bold_text(colour_Inverse(station_name))
    elif thr_lvl == 'green':
        station_name = green_color(station_name)
        return bold_text(colour_Inverse(station_name))

    elif thr_lvl == 'green-else':
        station_name = error_color(station_name)
        return station_name

class SignificantColouring:
    """class which function is to colour wind, vis, weather, clouds which
    are in caution and warning range"""

    def __init__(self, wx_list):
        self.wx = wx_list

    def colour_weather_list(self):

        caution_wx = settings.caution_wx
        warning_wx = settings.warning_wx
        severe_wx = settings.severe_wx
        exceptions_from_warning_and_severe = settings.exceptions_from_warning_and_severe

        final_w = []
        thr_level =[]
        for w in self.wx:

            hazard_wx_count = []

            for cw in caution_wx:
                count = w.count(cw)
                if count > 0:
                    hazard_wx_count.append('caution')

            for ww in warning_wx:
                count = w.count(ww)
                if count > 0:
                    hazard_wx_count.append('warning')

            for mw in severe_wx:
                count = w.count(mw)
                if count > 0:
                    hazard_wx_count.append('severe')

            ###print(hazard_wx_count)
            if ('caution' in hazard_wx_count) \
                    and ('warning' not in hazard_wx_count) \
                    and ('severe' not in hazard_wx_count) \
                    or w in exceptions_from_warning_and_severe:

                w = caution_colour(w)
                final_w.append(w)
                thr_level.append([caution,w,wx_ref])

            elif 'warning' in hazard_wx_count and (
                    'severe' not in hazard_wx_count) \
                    and w not in exceptions_from_warning_and_severe:
                w = warning_colour(w)
                final_w.append(w)
                thr_level.append([warning,w,wx_ref])

            elif 'severe' in hazard_wx_count and w not in \
                    exceptions_from_warning_and_severe:

                w = severe_colour(w)
                final_w.append(w)
                thr_level.append([magenta,w,wx_ref])

            elif w == 'NSW':
                final_w.append(w)
                thr_level.append([green,w,wx_ref])

            else:
                w = error_color(w)
                final_w.append(w)
                thr_level.append([error,w,wx_ref])
            # print(final_w[0])
        ###print('WEATHER_LEN:', len(final_w), len(self.wx))
        return [final_w, thr_level]

    def colour_cloud_list(self):
        final_cloud = []
        thr_lvl =[] # threat level in line

        cloud_caution = settings.cloud_caution
        cloud_warning = settings.cloud_warning
        cloud_lvo_warning = settings.cloud_lvo_warning
        few_caution = settings.few_caution

        vv_severe = settings.vv_severe
        vv_warning = settings.vv_warning
        vv_caution = settings.vv_caution

        for cloud in self.wx:
            cloud_layer_types = ['SKC', 'NSC', 'FEW', 'SCT', 'BKN', 'OVC']

            cb_tcu = False
            if 'CB' in cloud or 'TCU' in cloud:
                cb_tcu = True

            if 'NSC' in cloud:
                final_cloud.append(cloud)
                thr_lvl.append([green,cloud,clouds_ref])


            elif cloud[0:2] == 'VV':
                if cloud[2:5] == '///':
                    """if Vertical Visibility in cloud group than immediately it 
                    is WARNING """
                    cloud = severe_colour(cloud)
                    final_cloud.append(cloud)
                    thr_lvl.append([warning,cloud,clouds_ref])
                elif cloud[2:5].isdigit() and len(cloud[2:5]) == 3:
                    vv = int(cloud[2:5])
                    if vv <= vv_severe:
                        cloud = severe_colour(cloud)
                        final_cloud.append(cloud)
                        thr_lvl.append([magenta,cloud,clouds_ref])
                    elif vv_severe < vv <= vv_warning:
                        cloud = warning_colour(cloud)
                        final_cloud.append(cloud)
                        thr_lvl.append([warning,cloud,clouds_ref])
                    elif vv_warning < vv <= vv_caution:
                        cloud = caution_colour(cloud)
                        final_cloud.append(cloud)
                        thr_lvl.append([caution,cloud,clouds_ref])
                    elif vv > vv_caution:
                        final_cloud.append(cloud)
                        thr_lvl.append([green,cloud,clouds_ref])
                else:
                    cloud = error_color(cloud)
                    final_cloud.append(cloud)
                    thr_lvl.append([error,cloud,clouds_ref])

            elif cloud[0:3] in cloud_layer_types:

                cloud_density = cloud[0:3]
                cloud_height = cloud[3:6]
                if cloud_height.isdigit():
                    if cloud_density in cloud_layer_types:
                        cloud_height = int(cloud_height)
                        if cloud_density == 'FEW' and cloud_height <= few_caution:
                            cloud = caution_colour(cloud)
                            final_cloud.append(cloud)
                            thr_lvl.append([caution,cloud,clouds_ref])
                        elif cloud_density == 'FEW' and cb_tcu:
                            cloud = caution_colour(cloud)
                            final_cloud.append(cloud)
                            thr_lvl.append([caution,cloud,clouds_ref])
                        elif (cloud_density == 'SCT' or
                              cloud_density == 'BKN' or
                              cloud_density == 'OVC'):
                            if cloud_height <= cloud_lvo_warning:
                                cloud = severe_colour(cloud)
                                final_cloud.append(cloud)
                                thr_lvl.append([magenta,cloud,clouds_ref])
                            elif cloud_height <= cloud_warning:
                                cloud = warning_colour(cloud)
                                final_cloud.append(cloud)
                                thr_lvl.append([warning,cloud,clouds_ref])
                            elif cloud_height <= cloud_caution:
                                cloud = caution_colour(cloud)
                                final_cloud.append(cloud)
                                thr_lvl.append([caution,cloud,clouds_ref])
                            elif cloud_height > cloud_caution:
                                if cb_tcu:
                                    cloud = caution_colour(cloud)
                                    final_cloud.append(cloud)
                                    thr_lvl.append([caution,cloud,clouds_ref])
                                else:
                                    final_cloud.append(cloud)
                                    thr_lvl.append([green,cloud,clouds_ref])
                        else:
                            final_cloud.append(cloud)
                            thr_lvl.append([green,cloud,clouds_ref])
                else:
                    cloud = error_color(cloud)
                    final_cloud.append(cloud)
                    thr_lvl.append([error,cloud,clouds_ref])

            else:
                cloud = error_color(cloud)
                final_cloud.append(cloud)
                thr_lvl.append([error,cloud,clouds_ref])
        ###print('CLOUD_LEN:', len(final_cloud), len(self.wx))
        return [final_cloud,thr_lvl]

    def colour_wind_list(self):
        wind_caution = settings.wind_caution
        wind_warning = settings.wind_warning
        wind_severe = settings.wind_severe
        wind_gusts_caution = settings.wind_gusts_caution
        wind_gusts_warning = settings.wind_gusts_warning
        wind_gusts_severe = settings.wind_gusts_severe

        vrb_caution = settings.vrb_caution
        vrb_warning = settings.vrb_warning
        vrb_severe = settings.vrb_severe
        vrb_gusts_caution = settings.vrb_gusts_caution
        vrb_gusts_warning = settings.vrb_gusts_warning
        vrb_gusts_severe = settings.vrb_gusts_severe

        final_wind = []
        thr_lvl = []
        for wind in self.wx:

            if wind == 'CALM':
                final_wind.append(wind)
                thr_lvl.append([green,wind, wind_ref])
            if 'WS' in wind:
                wind = warning_colour(wind)
                final_wind.append(wind)
                thr_lvl.append([warning,wind, wind_ref])

            elif 'MPS' in wind:
                if 'VRB' in wind and 'G' in wind:

                    vrb_strenght = int(wind[3:5])

                    # speed to kts from mps
                    g_index = wind.index('G')
                    gusts = int(wind[(g_index + 1):(g_index + 3)])

                    # converting mps to kts
                    vrb_strenght = vrb_strenght * 2
                    gusts = gusts * 2

                    if vrb_strenght >= vrb_severe or gusts >= \
                            vrb_gusts_severe:
                        wind = severe_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([magenta,wind, wind_ref])

                    elif vrb_strenght >= vrb_warning or gusts >= \
                            vrb_gusts_warning:
                        wind = warning_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([warning,wind, wind_ref])
                    elif vrb_strenght >= vrb_caution or gusts >= \
                            vrb_gusts_caution:
                        wind = caution_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([caution,wind, wind_ref])

                    elif vrb_strenght < vrb_caution or gusts < vrb_gusts_caution:
                        final_wind.append(wind)
                        thr_lvl.append([green,wind, wind_ref])

                elif 'VRB' in wind:
                    vrb_strenght = int(wind[3:5])
                    # converting mps tp kts
                    vrb_strenght = vrb_strenght * 2

                    if vrb_strenght >= vrb_severe:
                        wind = severe_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([magenta,wind, wind_ref])
                    elif vrb_strenght >= vrb_warning:
                        wind = warning_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([warning,wind, wind_ref])
                    elif vrb_strenght >= vrb_caution:
                        wind = caution_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([caution,wind, wind_ref])
                    elif vrb_strenght < vrb_caution:
                        final_wind.append(wind)
                        thr_lvl.append([green,wind, wind_ref])

                wind_direction = wind[0:3]
                if wind_direction.isdigit() == True:
                    wind_direction = int(wind_direction)
                    if 0 <= wind_direction <= 360:
                        if wind[3:5].isdigit():
                            wind_speed = int(wind[3:5])
                            # converting mps to kts
                            wind_speed = wind_speed * 2

                            if 'G' in wind:
                                g_index = wind.index('G')
                                gusts = int(wind[(g_index + 1):(g_index + 3)])
                                # converting mps to kts
                                gusts = gusts * 2

                                if wind_speed >= wind_severe or gusts \
                                        >= wind_gusts_severe:
                                    wind = severe_colour(wind)
                                    final_wind.append(wind)
                                    thr_lvl.append([magenta,wind, wind_ref])

                                elif wind_speed >= wind_warning or gusts \
                                        >= wind_gusts_warning:
                                    wind = warning_colour(wind)
                                    final_wind.append(wind)
                                    thr_lvl.append([warning,wind, wind_ref])

                                elif wind_speed >= wind_caution or gusts >= wind_gusts_caution:
                                    wind = caution_colour(wind)
                                    final_wind.append(wind)
                                    thr_lvl.append([caution,wind, wind_ref])

                                elif wind_speed < wind_caution or gusts < wind_gusts_caution:
                                    final_wind.append(wind)
                                    thr_lvl.append([green,wind, wind_ref])
                            else:
                                if wind_speed >= wind_severe:
                                    wind = severe_colour(wind)
                                    final_wind.append(wind)
                                    thr_lvl.append([magenta,wind, wind_ref])

                                elif wind_speed >= wind_warning:
                                    wind = warning_colour(wind)
                                    final_wind.append(wind)
                                    thr_lvl.append([warning,wind, wind_ref])

                                elif wind_speed >= wind_caution:
                                    wind = caution_colour(wind)
                                    final_wind.append(wind)
                                    thr_lvl.append([caution,wind, wind_ref])

                                elif wind_speed < wind_caution:
                                    final_wind.append(wind)
                                    thr_lvl.append([green,wind, wind_ref])
                    else:
                        wind = error_color(wind)
                        final_wind.append(wind)
                        thr_lvl.append([error,wind, wind_ref])
                else:
                    wind = error_color(wind)
                    final_wind.append(wind)
                    thr_lvl.append([error,wind, wind_ref])

            elif 'KT' in wind:
                wind_direction = wind[0:3]
                if 'VRB' in wind and 'G' in wind:

                    vrb_strenght = int(wind[3:5])
                    g_index = wind.index('G')
                    gusts = int(wind[(g_index + 1):(g_index + 3)])

                    if vrb_strenght > vrb_severe or gusts >= vrb_gusts_severe:
                        wind = severe_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([magenta,wind, wind_ref])

                    elif vrb_strenght > vrb_warning or gusts >= \
                            vrb_gusts_warning:
                        wind = warning_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([warning,wind, wind_ref])

                    elif vrb_strenght > vrb_caution or gusts >= vrb_gusts_caution:
                        wind = caution_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([caution,wind, wind_ref])

                    elif vrb_strenght <= vrb_caution or gusts < vrb_gusts_caution:
                        final_wind.append(wind)
                        thr_lvl.append([green,wind, wind_ref])

                elif 'VRB' in wind:
                    vrb_strenght = int(wind[3:5])
                    if vrb_strenght >= vrb_warning:
                        wind = warning_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([warning,wind, wind_ref])

                    elif vrb_strenght >= vrb_warning:
                        wind = warning_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([warning,wind, wind_ref])

                    elif vrb_strenght >= vrb_caution:
                        wind = caution_colour(wind)
                        final_wind.append(wind)
                        thr_lvl.append([caution,wind, wind_ref])

                    elif vrb_strenght < vrb_caution:
                        final_wind.append(wind)
                        thr_lvl.append([green,wind, wind_ref])

                elif wind_direction.isdigit():
                    wind_direction = int(wind_direction)
                    ########## QUICK FIX!!!############
                    if 0 < wind_direction <= 360:
                        if  type(wind[3:5]) != str:
                            wind_speed = int(wind[3:5])
                        else:
                            wind_speed=1
                    ###################################
                        wind_direction = int(wind[0:3])
                        if 'G' in wind:
                            g_index = wind.index('G')
                            gusts = int(wind[(g_index + 1):(g_index + 3)])

                            if wind_speed >= wind_severe or gusts \
                                    >= wind_gusts_severe:
                                wind = severe_colour(wind)
                                final_wind.append(wind)
                                thr_lvl.append([magenta,wind, wind_ref])

                            elif wind_speed >= wind_warning or gusts \
                                    >= wind_gusts_warning:
                                wind = warning_colour(wind)
                                final_wind.append(wind)
                                thr_lvl.append([warning,wind, wind_ref])

                            elif wind_speed >= wind_caution or gusts >= wind_gusts_caution:
                                wind = caution_colour(wind)
                                final_wind.append(wind)
                                thr_lvl.append([caution,wind, wind_ref])

                            elif wind_speed < wind_caution or gusts < wind_gusts_caution:
                                final_wind.append(wind)
                                thr_lvl.append([green,wind, wind_ref])
                        else:
                            if wind_speed >= wind_severe:
                                wind = severe_colour(wind)
                                final_wind.append(wind)
                                thr_lvl.append([magenta,wind, wind_ref])

                            elif wind_speed >= wind_warning:
                                wind = warning_colour(wind)
                                final_wind.append(wind)
                                thr_lvl.append([warning,wind, wind_ref])

                            elif wind_speed >= wind_caution:
                                wind = caution_colour(wind)
                                final_wind.append(wind)
                                thr_lvl.append([caution,wind, wind_ref])

                            elif wind_speed < wind_caution:
                                final_wind.append(wind)
                                thr_lvl.append([green,wind, wind_ref])
                    else:
                        wind = error_color(wind)
                        final_wind.append(wind)
                        thr_lvl.append([error,wind, wind_ref])
                else:
                    wind = error_color(wind)
                    final_wind.append(wind)
                    thr_lvl.append([error,wind, wind_ref])
            else:
                wind = error_color(wind)
                final_wind.append(wind)
                thr_lvl.append([error,wind, wind_ref])
        # print('WIND_LEN:',len(final_wind), len(self.wx))
        return [final_wind,thr_lvl]

    def colour_vis_list(self):
        caution_vis = settings.caution_vis
        warning_vis = settings.warning_vis
        lvo = settings.lvo

        def vis_caution_warning_range(vis_int, i):
            """defining function which colour ranges of caution and warning
            range of visibility"""

            if 0 <= vis_int <= lvo:
                i = severe_colour(i)
                final_vis.append(i)
                thr_lvl.append([magenta,i,vis_ref])
            elif lvo < vis_int <= warning_vis:
                i = warning_colour(i)
                final_vis.append(i)
                thr_lvl.append([warning,i,vis_ref])
            elif warning_vis < vis_int <= caution_vis:
                i = caution_colour(i)
                final_vis.append(i)
                thr_lvl.append([caution,i,vis_ref])
            elif vis_int > caution_vis:
                final_vis.append(i)
                thr_lvl.append([green,i,vis_ref])

        final_vis = []
        thr_lvl = []
        for i in self.wx:
            if i == 'CAVOK':
                final_vis.append(i)
                thr_lvl.append([green,i,vis_ref])

            elif 'SM' in i:
                if i == 'P6SM':
                    final_vis.append(i)
                    thr_lvl.append([green,i,vis_ref])
                elif i.count('/') == 1:

                    """searching numbers after '/' until SM"""
                    slash_index = i.index('/')
                    n = slash_index
                    denominator = ''
                    n = 1
                    while i[slash_index + n].isdigit():
                        denominator = denominator + i[slash_index + n]
                        n += 1
                    """ searching numbers before '/' as long as they are digits"""
                    nominator = ''
                    n = 1
                    while i[slash_index - n].isdigit():
                        nominator = i[slash_index - n] + nominator
                        n += 1
                    nominator = int(nominator)

                    whole_miles = ''
                    if i.count(' ') == 1:
                        space_index = i.index(' ')
                        n = 1
                        while i[space_index - n].isdigit():
                            whole_miles = i[space_index - n] + whole_miles
                            n += 1

                    if whole_miles == '':
                        whole_miles = 0
                    whole_miles = int(whole_miles)
                    nominator = int(nominator)
                    denominator = int(denominator)
                    sm_vis = 1600 * (whole_miles + nominator / denominator)
                    if sm_vis % 1 == 0:
                        sm_vis = int(sm_vis)
                    else:
                        sm_vis = int(sm_vis - (sm_vis % 1))

                    """function for colouring ranges"""
                    vis_caution_warning_range(sm_vis, i)

                elif i.count('/') == 0 and len(i) == 3:
                    sm_vis = 1600 * int(re.findall(r'\d+', i)[0])

                    """function for colouring ranges"""
                    vis_caution_warning_range(sm_vis, i)

                else:
                    i = error_color(i)
                    final_vis.append(i)
                    thr_lvl.append([error,i,vis_ref])

            elif i.isdigit() and len(i) == 4:
                vis_int = int(i)
                """function for colouring ranges"""
                vis_caution_warning_range(vis_int, i)

            else:
                i = error_color(i)
                final_vis.append(i)
                thr_lvl.append([error,i,vis_ref])
        return [final_vis,thr_lvl]


weather = SignificantColouring(weather)
clouds = SignificantColouring(clouds)
winds = SignificantColouring(winds)
vis = SignificantColouring(vis)


def testing():
    print('\n#### TESTING ######'
          '\n--weather--')
    for i in weather.colour_weather_list():
        print(i)

    print('\n--clouds--:')
    for i in clouds.colour_cloud_list():
        print(i)

    print('\n--wind--')
    for i in winds.colour_wind_list():
        print(i)

    print('\n---- vis ----')
    for i in vis.colour_vis_list():
        print(i)
#testing()
