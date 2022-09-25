from TAF_decoder import TAF_decoder_function
from settings import Settings
stgs = Settings()



import avwx
import taf_database_program_functions as tdpf
import json
import colouring
import program_functions as pf



#prompt at the beginning of a program
prompt = """
#####################################################
Write "1 12" or "1 12 1 20" or "1 12 3 or q to quit
"""

def get_tafs_for_all_apts_in_db():
    all_avlb_apts = []
    avlb_apprs_data = pf.load_avlb_apprs_datra()
    for appr_data in avlb_apprs_data:
        all_avlb_apts.append(appr_data[0])
    return all_avlb_apts

def get_and_dump_real_time_tafs(all_airports,missing_apts, taf_update, filename):
    """gets real time tafs for selected airports and dump them into a file"""
    #global TAFs, filename, f_obj
    TAFs = get_TAF_for_apt(all_airports,missing_apts, taf_update)
    with open(filename, 'w') as f_obj:
        json.dump(TAFs, f_obj)
    return TAFs

def dump_special_case_tafs():
    global TAFs
    # Loading list of special TAFs from json file
    json_file = open("Data_new/TAFs__special_cases.json","r")
    TAFs__special_cases = json.load(json_file)
    json_file.close()

    TAFs = TAFs__special_cases["taf1"]

    print("Printing each special TAF in the list (fpf)")
    for TAF in TAFs:
        print(TAF)

    # Saving TAFs so they can be used in the main program
    filename = 'Data/temp_TAFs.json'
    with open(filename, 'w') as f_obj:
        json.dump(TAFs, f_obj)


def load_json_TAF():
    """load TAFs from JSON file created in first run"""
    filename = 'Data/temp_TAFs.json'
    try:
        with open(filename) as f_obj:
            TAFs = json.load(f_obj)
    except FileNotFoundError:
        print('*** temp_TAFs.json file not found (fpf) ***')
        print('*** Write any airport code next time you restart program ***')
    else:
        return TAFs



def store_an_answer(answer):
    """stores an answer given in final_program"""
    filename = 'Data_new/answer.json'
    with open(filename, 'w') as f_obj:
        json.dump(answer, f_obj)

def load_an_answer():
    """loads an answer given in final_program"""
    filename = 'Data_new/answer.json'
    with open(filename) as f_obj:
        loaded_answer = json.load(f_obj)
    return loaded_answer

def print_coloured_apt_list(apt_threat_level):
    """prints list of coloured airport ICAO code and threats - FINAL PROGRAM goal"""
    global apt
    print('')
    for apt in apt_threat_level:
        print(apt)
def append_threat_level(apt_threat_level, final_line, runway_string, end_string):
    if stgs.rwy_data == 0:
        apt_threat_level.append(final_line) #+ '\t\t' + runway_string)
    elif stgs.rwy_data == 1:
        apt_threat_level.append(final_line + '\t\t' + runway_string)
    elif stgs.rwy_data == 2:
        apt_threat_level.append(final_line + '\n\n' + end_string + '\n')


def print_weather_in_whole_range(cancel_out_of_range_msg, significant_range_active,settings):
    """prints weather and ICAO apts list in whole time range of each airport"""
    # when answer remain empty - whole validity of TAF will be diplayed
    global significant_start_hour, significant_end_hour, significant_start_day, significant_end_day,apt_threat_level, TAFs

    significant_start_hour = 1
    significant_end_hour = 24
    significant_start_day = 1
    significant_end_day = 3
    print_type = settings.print_type
    print_time_group = settings.print_time_group
    # list to store apt threat level and values of threats
    apt_threat_level = []
    TAFs = load_json_TAF()

    for TAF in TAFs:
        # running TAF decoder function - this prints decoded,coloured TAFs
        # in the same time storing apt threat level in [] (from RETURN of TAF decoder)
        final_coloured_taf_string,final_line, runway_string, end_string = TAF_decoder_function(TAF,
                                                     significant_start_hour=significant_start_hour,
                                                     significant_end_hour=significant_end_hour,
                                                     significant_start_day=significant_start_day,
                                                     significant_end_day=significant_end_day,
                                                     cancel_out_of_range_msg=cancel_out_of_range_msg,
                                                     significant_range_active=significant_range_active,
                                                     print_type=print_type,
                                                     print_time_group=print_time_group,
                                                     )
        append_threat_level(apt_threat_level, final_line, runway_string, end_string)
    # printing list af apt data in condensed way (apt_thr_lvl + all threats gennerating weather

    print_coloured_apt_list(apt_threat_level)

def print_weather_day1_only(cancel_out_of_range_msg, significant_range_active, settings):
    """prints only day 1 weather (1-24h)"""
    # global significant_start_day, significant_start_hour, significant_end_day, significant_end_hour, apt_threat_level, TAFs, TAF
    significant_start_day = 1
    significant_start_hour = 1
    significant_end_day = 1
    significant_end_hour = 24
    print('1day',settings.print_type, settings.print_time_group)
    print_type = settings.print_type
    print_time_group = settings.print_time_group

    apt_threat_level = []
    TAFs = load_json_TAF()

    for TAF in TAFs:
        final_coloured_taf_string,final_line, runway_string, end_string =TAF_decoder_function(TAF,
                                                     significant_start_hour=significant_start_hour,
                                                     significant_end_hour=significant_end_hour,
                                                     significant_start_day=significant_start_day,
                                                     significant_end_day=significant_end_day,
                                                     cancel_out_of_range_msg=cancel_out_of_range_msg,
                                                     significant_range_active=significant_range_active,
                                                     print_type=print_type,
                                                     print_time_group=print_time_group,)
        append_threat_level(apt_threat_level, final_line, runway_string, end_string)

    print_coloured_apt_list(apt_threat_level)


def print_weather_day2_only(cancel_out_of_range_msg, significant_range_active, settings):
    """prints only day 2 weather (25-48h)"""

    global significant_start_day, significant_start_hour, significant_end_day, significant_end_hour, apt_threat_level, TAFs, TAF

    significant_start_day = 2
    significant_start_hour = 1
    significant_end_day = 2
    significant_end_hour = 24
    print_type = settings.print_type
    print_time_group = settings.print_time_group

    apt_threat_level = []
    TAFs = load_json_TAF()
    for TAF in TAFs:
        final_coloured_taf_string,final_line, runway_string, end_string = TAF_decoder_function(TAF,
                                                     significant_start_hour=significant_start_hour,
                                                     significant_end_hour=significant_end_hour,
                                                     significant_start_day=significant_start_day,
                                                     significant_end_day=significant_end_day,
                                                     cancel_out_of_range_msg=cancel_out_of_range_msg,
                                                     significant_range_active=significant_range_active,
                                                     print_type=print_type,
                                                     print_time_group=print_time_group,
                                                     )
        append_threat_level(apt_threat_level, final_line, runway_string, end_string)
    print_coloured_apt_list(apt_threat_level)

def print_weather_day3_only(cancel_out_of_range_msg, significant_range_active, settings):
    """prints only day 3 weather (49-72h)"""
    global significant_start_day, significant_start_hour, significant_end_day, significant_end_hour, apt_threat_level, TAFs, TAF
    significant_start_day = 3
    significant_start_hour = 1
    significant_end_day = 3
    significant_end_hour = 24
    print_type = settings.print_type
    print_time_group = settings.print_time_group

    apt_threat_level = []
    TAFs = load_json_TAF()
    for TAF in TAFs:
        final_coloured_taf_string,final_line, runway_string, end_string = TAF_decoder_function(TAF,
                                                     significant_start_hour=significant_start_hour,
                                                     significant_end_hour=significant_end_hour,
                                                     significant_start_day=significant_start_day,
                                                     significant_end_day=significant_end_day,
                                                     cancel_out_of_range_msg=cancel_out_of_range_msg,
                                                     significant_range_active=significant_range_active,
                                                     print_type=print_type,
                                                     print_time_group=print_time_group,
                                                     )
        append_threat_level(apt_threat_level, final_line, runway_string, end_string)
    print_coloured_apt_list(apt_threat_level)


def get_TAF_for_apt(all_airports, missing_apts, taf_update):
    """downloads valid TAFs for airports in all_airport list"""

    for apt in all_airports:
        get_TAF_for_selected_apt(apt, missing_apts, taf_update)
    print('\t *** LOADING COMPLETED *** (fpf)\n')
    return  taf_update


def get_TAF_for_selected_apt(apt, missing_apts, taf_update):

    #loading json object conaining station_id and raw_text TAF
    path= "Data_new/api__tafs_cleaned.json"
    with open(path,'r') as f_obj:
        tafs_cleaned_dict = json.load(f_obj)

    # Case that station was not found
    no_station_msg = apt + '- no such station'
    apt_taf = no_station_msg

    # Seatchig for the station_id in the taf json
    for i in range(len(tafs_cleaned_dict['station_id'])):
        if tafs_cleaned_dict['station_id'][i]==apt.upper():
            apt_taf = tafs_cleaned_dict['raw_text'][i]
            break
    print(apt_taf, '(fpf--aa)')
    """Getting taf for selected airport. """

    # If TAF download successful:
    if apt_taf != no_station_msg :
        taf_update.append(apt_taf)


def if_update_unsuccessful_try_again(apt_taf):
    taf =''
    n = 1
    no_connection = False
    while not apt_taf.raw:
        if n == 10:
            print('          -- error - 10x attempts unsuccessful')
            no_connection = True
            break

        try:apt_taf.update(timeout=1000)
        except:
            pass
        else:
            if apt_taf.raw is None:
                pass
            else:
                print('raw',apt_taf.raw)
                taf = apt_taf.raw
        n += 1
    if no_connection:
        filename= 'Data/all_tafs.json'
        with open(filename) as f_obj:
            all_tafs = json.load(f_obj)
            print('          ... loaded stored TAF')
            for loaded_taf in all_tafs:
                if apt_taf.icao in loaded_taf:
                    taf  =  loaded_taf
    return taf

def moving_all_airports_into_one_list_from__taf_list(taf_list):
    """Moving all airports into one list."""
    all_airports = []
    taf_update = []
    missing_apts = []
    for item in taf_list:
        if type(item) == list:
            for apt in item:
                all_airports.append(apt)
        elif type(item) == str:
            all_airports.append(item)
        else:
            print('error 1')
    return all_airports, missing_apts, taf_update

def load_all_saved_apt_groups_data_from_data_folder():
    """load all saved apt_groups data from data folder"""
    filename = 'data/g_groups_apts_db.json'
    with open(filename) as f_obj:
        apt_groups = json.load(f_obj)
    return apt_groups

def airport_selection_and_TAF_download(requested_airports_taf):
    """Downloads TAFs for reqested airports and saves data in json"""
    # Load database of airports groups.
    apt_groups = load_all_saved_apt_groups_data_from_data_folder()

    # Creating list of airports of which TAF will be downloaded.
    taf_list = tdpf.create_list_of_apts_to_get_TAF__convertg_group_into_list \
        (apt_groups, requested_airports_taf)

    # Moving all airports into one list.
    all_airports, missing_apts, taf_update = moving_all_airports_into_one_list_from__taf_list \
        (taf_list)

    # Printing list of airports which TAF download was not possible.
    if missing_apts:
        print('\nmissing_apts', missing_apts, '\n')

    # Loading updated TAFs and storing json file
    TAFs = get_and_dump_real_time_tafs(all_airports, missing_apts, taf_update , 'Data/temp_TAFs.json')

    return TAFs

def promp_for_apt_selection():
    """Prompts user to write what airports TAFs should be taken"""
    prompt = ' What airports you want?'
    requested_airports_taf = input(prompt)
    correct_apt =[]
    incorrect_apt =[]
    requested_airports_taf = requested_airports_taf.split()
    for word in requested_airports_taf:
        if word.isalpha() and len(word) == 4 or \
            word.isalpha() and word.split()[0] == 'g' and (len(word) == 5 or len(word) == 5):
            correct_apt.append(word)
        else:
            incorrect_apt.append(word)
            print(colouring.prYellow('Incorrect apt name "') + colouring.prRed(word) + colouring.prYellow('" use: XXXX or gXXXX or gXXXXb'))
    requested_airports_taf = correct_apt
    print(correct_apt)

    return requested_airports_taf


def save_last_requested_apts(requested_airports_taf):
    filename = 'DATA/last_requested_apts.json'
    with open(filename, 'w') as f_obj:
        json.dump(requested_airports_taf, f_obj)


def load_last_requested_apts():
    """Loads string of last requested airports. If no file, than prompts for airports"""
    filename = 'DATA/last_requested_apts.json'
    try:
        with open(filename) as f_obj:
            requested_airports_taf = json.load(f_obj)
        return requested_airports_taf
    except FileNotFoundError:
        print('ff not f')




        requested_airports_taf = promp_for_apt_selection()
        return requested_airports_taf

def answer_is_airports_only(answer_split):
    requested_airports_taf = []
    for word in answer_split:
        if  (len(word) == 4) or \
            (word[0] == 'g' and (len(word) == 5 or len(word) == 6)):
            requested_airports_taf.append(word)
        else:
            print('fpf - else 1243')
    return requested_airports_taf


def check_if_last_requested_apts_avlb():
    """Checks if file storing last airports requests exists"""
    filename = 'Data/last_requested_apts.json'
    try:
        with open(filename) as f_obj:
            last_requested_apts = json.load(f_obj)

    except FileNotFoundError:
        return False
    else:
        s = ''
        for i in last_requested_apts:
            s += i + ' '
        print('Last request: ' + s)
        return [True, s]


def add_new_g_group(word):
    prompt2 ='\n'+ str(word) +' NOT IN DATABASE --> Use template: XXXX XXXX XXXX ect.'
    prompt2 += '\n\t( "n" to cancel):'
    ans = input(prompt2)
    if ans == 'n':
        pass
    else:# ans =='':
        filename = 'Data/g_groups_apts_db.json'
        with open(filename) as f_obj:
            g_groups_db = json.load(f_obj)
            error_switch= False
            while True:
                if not error_switch:
                    new_key = ans#input('')
                elif error_switch:
                    new_key = input('Try again. Write only 4-letter code separated by SPACE and press ENTER:\n')

                new_key_split = new_key.split()
                counter = []
                for i in new_key_split:
                    if len(i) == 4 and i.isalpha():
                        counter.append(1)
                print()
                if sum(counter) == len(new_key_split):
                    g_key = 'g' + str(new_key_split[0])
                    g_groups_db[str(g_key)]=new_key_split
                    with open(filename, 'w') as f_obj:
                        json.dump(g_groups_db, f_obj, indent=2)
                    print('Added: '+ g_key + ': ' + str(new_key_split) )
                    break

                else:
                    error_switch = True
            return g_key

def download_taf_database():
    # Downloading the file  - https://www.codingem.com/python-download-file-from-url/
    import requests
    url = 'https://www.aviationweather.gov/adds/dataserver_current/current/tafs.cache.csv.gz'
    response = requests.get(url)
    path__compresed = "Data_new/api__tafs_downloaded.csv.gz"

    ##  FOR DEVELOPMENT ONLY!! - -SWITCHED OFF TO AVOID LOADING from the Internet DATA EVERYTIME
    # open(path__compresed, "wb").write(response.content)

    # Extracting csv.gz to csv
    import gzip

    path__extracted = 'Data_new/api__tafs_extracted.csv'
    with gzip.open(path__compresed, 'rt', newline='', encoding='utf-8') as csv_file:
        csv_data = csv_file.read()
        with open(path__extracted, 'wt') as out_file:
            out_file.write(csv_data)

    # Methode 1 you tube video Socratica on csv -- this methode has many problems so skip it
    lines = [line for line in open(path__extracted)]

    # methode 2 - using csv module https://www.youtube.com/watch?v=Xi52tx6phRU&t=114s
    import csv
    print(dir(csv))  # prints available methodes for csv module

    file = open(path__extracted, newline='')  # newline='' -  depending on the system strings may end in differene t way - this prowides that all works correctly across all systems
    reader = csv.reader(file)
    # Skipping 5 first lines down to the header - specific to each file
    for x in range(5):
        next(reader)

    header = (next(reader))
    print(header)

    # Parsing the data and converting some of it into a proper type

    from dateutil.parser import parse  # check https://stackabuse.com/converting-strings-to-datetime-in-python/
    # module which automatically converts time string into the datetime format

    data = []
    for row in reader:
        # row = ['raw_text', 'station_id', 'issue_time', 'bulletin_time', 'valid_time_from', 'valid_time_to', 'remarks', 'latitude', 'longitude', 'elevation_m', 'fcst_time_from', 'fcst_time_to']

        raw_text = str(row[0])
        station_id = str(row[1])
        issue_time = parse(row[2])
        bulletin_time = parse(row[3])
        valid_time_from = parse(row[4])
        valid_time_to = parse(row[5])
        remarks = str(row[6])
        latitude = float(row[7])
        longitude = float(row[8])
        elevation_m = float(row[9])
        fcst_time_from = parse(row[10])
        fcst_time_to = parse(row[11])
        data.append([raw_text, station_id, issue_time, bulletin_time, valid_time_from, valid_time_to, remarks, latitude, longitude, elevation_m, fcst_time_from, fcst_time_to])

    # Sorting API TAFs based on the station_id
    data__sorted = sorted(data, key=lambda x: x[1])  # column 1 is station_id in the data object

    # Store parsed data in CSV file - just for reference
    path__data_cleaned = "Data_new/api__tafs_cleaned.csv"
    file = open(path__data_cleaned, 'w', newline='', encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow(['station_id', 'raw_text'])  # storing only selected two columns

    for i in range(len(data__sorted)):
        row = data__sorted[i]
        station_id = row[1]
        raw_text = row[0]
        writer.writerow([station_id, raw_text])

    # Converting data_sorted into a dictionary
    tafs_cleaned_dict = {'station_id': [], 'raw_text': []}
    for i in range(len(data__sorted)):
        tafs_cleaned_dict['station_id'].append(data__sorted[i][1])
        tafs_cleaned_dict['raw_text'].append(data__sorted[i][0])

    # Store tafs_cleanded_dict as json
        # Check this video: https://www.youtube.com/watch?v=pTT7HMqDnJw
    import json

    path = "Data_new/api__tafs_cleaned.json"
    with open(path, "w") as f_obj:
        json.dump(tafs_cleaned_dict, f_obj)

