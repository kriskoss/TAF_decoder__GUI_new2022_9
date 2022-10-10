from TAF_decoder import TAF_decoder_function
from settings import Settings
stgs = Settings()



import taf_database_program_functions as tdpf
import json
import colouring
import program_functions as pf


no_station_msg = '- no such station'
#prompt at the beginning of a program
prompt = """
#####################################################
Write "1 12" or "1 12 1 20" or "1 12 3 or q to quit
"""


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


def printing_last_requested_apts():
    """Checks if file storing last airports requests exists"""
    filename = 'Data/last_requested_apts.json'
    try:
        with open(filename) as f_obj:
            last_requested_apts = json.load(f_obj)

    except FileNotFoundError:
        # No last requested airports -  prompt for new
        print('\n\tNo reqested aiports stored. Write requested airports.')
        return False
    else:
        s = ''
        for item in last_requested_apts:
            s += item.upper() + ' '
        print('Last request: ' + s)
        return [True, s]


######## 2022.09 ###############

# BUTTON function - Update TAFs
def download_taf_database():
    # Downloading the file  - https://www.codingem.com/python-download-file-from-url/
    import requests
    url = 'https://www.aviationweather.gov/adds/dataserver_current/current/tafs.cache.csv.gz'
    response = requests.get(url)
    path__compresed = "Data_new/api__tafs_downloaded.csv.gz"

    ##  FOR DEVELOPMENT ONLY!! - -SWITCHED OFF TO AVOID LOADING from the Internet DATA EVERYTIME
    open(path__compresed, "wb").write(response.content)

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

    print('TAF DOWNLOAD COMPLETE - fpf')

# Button function - Update Airports
def download_airports_database():
    """Function downloads all data related to the runways and makes it available for use"""
    import csv
    import requests

    # Downloading data file from - https://davidmegginson.github.io/ourairports-data/runways.csv
    url = 'https://davidmegginson.github.io/ourairports-data/runways.csv'
    response = requests.get(url)
    # Saving csv file
    csv_path = "Data_new/runway_data_download.csv"
    open(csv_path, "wb").write(response.content)

    # Reading csv file

    file = open(csv_path, newline='')  # newline='' -  depending on the system strings may end in differene t way - this prowides that all works correctly across all systems
    reader = csv.reader(file)

    # Getting header
    header = (next(reader))
    print(header)

    # Extracting data from csv file
    data = []
    counter__all_apts = 0
    counter__good_apts = 0

    for row in reader:
        # row = ['id', 'airport_ref', 'airport_ident', 'length_ft', 'width_ft', 'surface', 'lighted', 'closed', 'le_ident', 'le_latitude_deg', 'le_longitude_deg', 'le_elevation_ft', 'le_heading_degT', 'le_displaced_threshold_ft', 'he_ident', 'he_latitude_deg', 'he_longitude_deg', 'he_elevation_ft', 'he_heading_degT', 'he_displaced_threshold_ft']

        counter__all_apts += 1
        # if counter__good_apts >10:
        #     break

        for i in range(len(row)):
            # Checking if node is empty
            if row[i] == '':
                row[i] = -1
            # Assigning variables to each column of the row
            if i == 0:
                id = str(row[i])
            elif i == 1:
                airport_ref = str(row[i])
            elif i == 2:
                airport_ident = str(row[i])
            elif i == 3:
                length_ft = int(row[i])
                # Skipping all airports which length is not sufficient
                if length_ft < 1750 / 0.3048:
                    break

            elif i == 4:
                width_ft = int(row[i])
                if width_ft < 30 / 0.3048:
                    break
            elif i == 5:
                # Skipping all airports which surface is improper
                surface = str(row[i])
                bad_surf = ["GRASS", "TURF", "DIRT", "WATER", "GRAVEL", "GRVL", "GVL"]
                reject = False
                for item in bad_surf:
                    if item in surface.upper():
                        reject = True
                if reject:
                    break

            elif i == 6:
                lighted = int(row[i])
                # Skipping all airports which have no lightning
                if lighted == 0:
                    break
            elif i == 7:
                closed = int(row[i])
                # Skipping all closed airports
                if closed == 1:
                    break
            elif i == 8:
                le_ident = str(row[i])
            elif i == 9:
                le_latitude_deg = float(row[i])
            elif i == 10:
                le_longitude_deg = float(row[i])
            elif i == 11:
                le_elevation_ft = int(row[i])
            elif i == 12:
                le_heading_degT = float(row[i])
            elif i == 13:
                le_displaced_threshold_ft = int(row[i])
            elif i == 14:
                he_ident = str(row[i])
            elif i == 15:
                he_latitude_deg = float(row[i])
            elif i == 16:
                he_longitude_deg = float(row[i])
            elif i == 17:
                he_elevation_ft = int(row[i])
            elif i == 18:
                he_heading_degT = float(row[i])
            elif i == 19:
                he_displaced_threshold_ft = str(row[i])

                # Append data only if all items of a row are fulfill the conditions
                counter__good_apts += 1
                print(counter__good_apts, counter__all_apts, row)
                data.append([
                    id,
                    airport_ref,
                    airport_ident,
                    length_ft,
                    width_ft,
                    surface,
                    lighted,
                    closed,
                    le_ident,
                    le_latitude_deg,
                    le_longitude_deg,
                    le_elevation_ft,
                    le_heading_degT,
                    le_displaced_threshold_ft,
                    he_ident,
                    he_latitude_deg,
                    he_longitude_deg,
                    he_elevation_ft,
                    he_heading_degT,
                    he_displaced_threshold_ft
                ])

    # Sorting RWY DATA based on the airport_ident
    data__sorted = sorted(data, key=lambda x: x[2])

    # Store parsed data in CSV file - just for reference
    path__data_cleaned = "Data_new/airports_cleaned.csv"
    file = open(path__data_cleaned, 'w', newline='', encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow([
        'airport_ident',
        'length__meters',
        'width__meters',
        'le_ident',
        'le_heading_degT',
        'le_displaced_threshold__meters',
        'he_ident',
        'he_heading_degT',
        'he_displaced_threshold__meters'
    ])  # storing only selected columns

    # Getting columns from sorted data list and conveting units
    import math
    for i in range(len(data__sorted)):
        row = data__sorted[i]
        airport_ident = row[2]
        length__meters = round(float(row[3]) * 0.3048)
        width__meters = round(float(row[4]) * 0.3048)
        le_ident = row[8]
        le_heading_degT = round(float(row[12]))
        le_displaced_threshold__meters = round(float(row[13]) * 0.3048)
        he_ident = row[14]
        he_heading_degT = round(float(row[18]))
        he_displaced_threshold__meters = round(float(row[19]) * 0.3048)

        # Writing to csv file only selected columnss
        writer.writerow([
            airport_ident,
            length__meters,
            width__meters,
            le_ident,
            le_heading_degT,
            le_displaced_threshold__meters,
            he_ident,
            he_heading_degT,
            he_displaced_threshold__meters])

    # Converting data_sorted into a dictionary
    airports_dict = {
        'airport_ident': [],
        'length__meters': [],
        'width__meters': [],
        'le_ident': [],
        'le_heading_degT': [],
        'le_displaced_threshold__meters': [],
        'he_ident': [],
        'he_heading_degT': [],
        'he_displaced_threshold__meters': [],
    }
    for i in range(len(data__sorted)):
        airports_dict['airport_ident'].append(data__sorted[i][2])
        airports_dict['length__meters'].append(round(float(data__sorted[i][3]) * 0.3048))
        airports_dict['width__meters'].append(round(float(data__sorted[i][4]) * 0.3048))
        airports_dict['le_ident'].append(data__sorted[i][8])
        airports_dict['le_heading_degT'].append(round(float(data__sorted[i][12])))
        airports_dict['le_displaced_threshold__meters'].append(round(float(data__sorted[i][13]) * 0.3048))
        airports_dict['he_ident'].append(data__sorted[i][14])
        airports_dict['he_heading_degT'].append(round(float(data__sorted[i][18])))
        airports_dict['he_displaced_threshold__meters'].append(round(float(data__sorted[i][19]) * 0.3048))

    # Store tafs_cleanded_dict as json
    # Check this video: https://www.youtube.com/watch?v=pTT7HMqDnJw
    import json

    path = "Data_new/airports_cleaned.json"
    with open(path, "w") as f_obj:
        json.dump(airports_dict, f_obj)

# Button function - Add new group
def add_new_group(answer_split):
    """Adding new g_group or updating existing one in JSON database"""

    import copy
    filename = 'Data/g_groups_apts_db.json'
    with open(filename) as f_obj:
        g_groups_db = json.load(f_obj)

        # Creating KEY form the first STATION ID to be stored in JSON
        g_key = 'g' + str(answer_split[0])

        # Checking if g_group exists in JSON database
        g_group_found = False
        for g_group in g_groups_db.keys():
            if g_key.upper() == g_group.upper():
                # Adding FOUND flag
                g_group_found = True

                # Making copy of the GROUP BEFORE update
                g_group__before_update = copy.deepcopy(g_groups_db[g_group])

                # UPDATING GROUP
                g_groups_db[g_group] = answer_split

        # Adding all XXXX STATIONS IDs into list to be stored in JSON
        if not g_group_found:
            g_groups_db[str(g_key)] = answer_split

        # SAVING=DUMPING complete g_group
        with open(filename, 'w') as f_obj:
            json.dump(g_groups_db, f_obj, indent=2)

        ### RETURNING MESSAGES to be used in the TERMINAL LABEL in the KIVY APP
        if not g_group_found:
            return f"Added group: {g_key} ({', '.join(answer_split)})."
        else:
            return f'{g_key} existed in the database!' \
                   f'{g_group__before_update} replaced with: {answer_split}'

# Button functions - get decoded TAF for selected group
def get_TAF_for_all_requested_stations(requested_stations):
    """downloads valid TAFs for airports in all_airport list"""
    # Initializing list of TAFs for requested stations
    requested_stations_TAFs=[]

    # Getting TAFs for each station and appending it to single list
    for station in requested_stations:

        # Getting TAF for the station
        station_TAF = get_single_stations_TAF(station)

        # Appending TAF
        requested_stations_TAFs.append(station_TAF)

    # Load complete message
    print(f'   *** LOADING COMPLETED *** (fpf)  ')

    return  requested_stations_TAFs

def get_single_stations_TAF(station):
    """Gets raw TAF string from TAFs json DATABASE for single station"""
    #loading json object conaining station_id and raw_text TAF

    path= "Data_new/api__tafs_cleaned.json"
    with open(path,'r') as f_obj:
        tafs_cleaned_dict = json.load(f_obj)

    # Initial value that the station is not found.
    station_TAF = colouring.prRed(station + no_station_msg)

    # Traversing TAFs database for station
    for i in range(len(tafs_cleaned_dict['station_id'])):

        # Station found in TAFs database - overrides initial station TAF value
        if tafs_cleaned_dict['station_id'][i]== station.upper():
            station_TAF = tafs_cleaned_dict['raw_text'][i]
            break
    print(station_TAF, colouring.prYellow("(---source: (fpf.get_single_stations_TAF))\n"))
    return station_TAF

#
