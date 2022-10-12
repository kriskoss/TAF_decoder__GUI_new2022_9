from settings import Settings

settings = Settings()
def ref(i=''):
    if settings.printing_active:
        ref = ("\t\n# " + str(i) + " #")
        print("\033[94m {}\033[00m".format(ref))


# def prPurple(skk):
#     return "\033[95m{}\033[00m".format(skk)
def prPurple(skk):
    return f'[color=a825db]{skk}[/color]'


# def prCyan(skk):
#     return "\033[96m{}\033[00m".format(skk)
def prCyan(skk):
    return "\033[96m{}\033[00m".format(skk)


# def prGreen(skk):
#     return "\033[92m{}\033[00m".format(skk)
def prGreen(skk):
    return f'[color=117841]{skk}[/color]'


# def prLightGray(skk):
#     return "\033[57m{}\033[00m".format(skk)

# def prLightGray(skk):
#     return "\033[1;90;40m" + str(skk)
def prLightGray(skk):
    return f'[color=4a494a]{skk}[/color]'


def prYellow(skk):
    return "\033[93m{}\033[00m".format(skk)


def prUnderlined(skk):
    return ('\x1b[4;30;48m{}\x1b[0m'.format(skk))


# def prBoxed(skk):
#     return ('\x1b[52;30;48m{}\x1b[0m'.format(skk))
def prBoxed(skk):
    return f'[color=c6bdff]{skk}[/color]'

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


def add_to_dict_gr_data(lista, key, gr_data):
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


def add_to_dict_TIME_gr_data(lista, key, time_gr_data):
    # adds data to gr_data list of dictionaries, name of KEY has to be given
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


def print_keys(time_gr_data, gr_data, weather_data):
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


def print_list(lista):
    for i in lista:
        print(i)


def print_all_data(gr_data, time_gr_data, weather_data, weather_data_copy):
    ref('gr_data:')
    print_list(gr_data)
    ref('time_gr_data')
    print_list((time_gr_data))
    ref('weather_data')
    print_list(weather_data)
    ref('weather_data_copy')
    print_list(weather_data_copy)

def hours_to_ddhh(hours):
    if hours<24:
        return f'day 1: [b]{hours}[/b] UTC'
    else:
        return f'day 2: [b]{hours-24}[/b] UTC'