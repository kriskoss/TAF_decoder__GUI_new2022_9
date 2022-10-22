import pprint

from TAF_decoder import TAF_decoder_function
import TAF_decoder__helper_functions as Td_helpers
import json
import requests
import gzip
import csv

no_station_msg = '- no such station'
#prompt at the beginning of a program
prompt = """
#####################################################
Write "1 12" or "1 12 1 20" or "1 12 3 or q to quit
"""


def combine_all_stations_threat_level(apt_threat_level):
    """prints list of coloured airport ICAO code and threats - FINAL PROGRAM goal"""
    combined_stations_threat_level = []

    for apt in apt_threat_level:
        combined_stations_threat_level.append(apt)

    return '\n'.join(combined_stations_threat_level)

def combine_data(settings,station_threats, wind_profile,runways_length,appr_data):
    """VERY IMPORTATNT PARR - responsible for generating INITIAL PART of the final display
    GENERATES FINAL STRING of stations (do not include detailed TAFS)

    :param settings:
    :param station_threats: LIST - Tdf.all_lines - list containing relevant weather for time periods for single statio
    :param wind_profile: LIST - Tdf.wind_lines - same as above but for wind
    :param runways_length:
    :param appr_data:
    :return: STRING - ready to be displayed!!!!!!!
    """
    final_display_string__UPPER=''
    if settings.show_wind_profile:
        final_display_string__UPPER = wind_profile + '\n   ' + runways_length + '\n'

    else:
        if settings.rwy_data == 0:
            final_display_string__UPPER= station_threats
        elif settings.rwy_data == 1:
            final_display_string__UPPER= station_threats + '\n   ' + runways_length +'\n'
        elif settings.rwy_data == 2:
            final_display_string__UPPER= station_threats + '\n\n' + appr_data + '\n'


    return final_display_string__UPPER

def download_metars_database(parse):
    url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv.gz'
    response = requests.get(url)
    path__compresed = "Data_new/api__metars_downloaded.csv.gz"

    # SAVING database
    open(path__compresed, "wb").write(response.content)

    # Extracting csv.gz and saving csv
    path__extracted = 'Data_new/api__metars_extracted.csv'
    with gzip.open(path__compresed, 'rt', newline='', encoding='utf-8') as csv_file:
        csv_data = csv_file.read()
        with open(path__extracted, 'wt') as out_file:
            out_file.write(csv_data)

    # methode 2 - using csv module https://www.youtube.com/watch?v=Xi52tx6phRU&t=114s
    file = open(path__extracted, newline='')  # newline='' -  depending on the system strings may end in differene t way - this prowides that all works correctly across all systems
    reader = csv.reader(file)
    # Skipping 5 first lines down to the header - specific to each file
    for x in range(5):
        next(reader)

    header = (next(reader))
    print(header, 'fpf.metars')



    # Parsing the data and converting some of it into a proper type
    data = []
    for row in reader:
        # row = ['raw_text', 'station_id', 'observation_time', 'latitude', 'longitude', 'temp_c', 'dewpoint_c', 'wind_dir_degrees', 'wind_speed_kt', 'wind_gust_kt', 'visibility_statute_mi', 'altim_in_hg', 'sea_level_pressure_mb', 'corrected', 'auto', 'auto_station', 'maintenance_indicator_on', 'no_signal', 'lightning_sensor_off', 'freezing_rain_sensor_off', 'present_weather_sensor_off', 'wx_string', 'sky_cover', 'cloud_base_ft_agl', 'sky_cover', 'cloud_base_ft_agl', 'sky_cover', 'cloud_base_ft_agl', 'sky_cover', 'cloud_base_ft_agl', 'flight_category', 'three_hr_pressure_tendency_mb', 'maxT_c', 'minT_c', 'maxT24hr_c', 'minT24hr_c', 'precip_in', 'pcp3hr_in', 'pcp6hr_in', 'pcp24hr_in', 'snow_in', 'vert_vis_ft', 'metar_type', 'elevation_m']

        raw_text = str(row[0])
        station_id = str(row[1])
        observation_time = str(row[2])
        data.append([raw_text, station_id, observation_time])

    # Sorting API TAFs based on the station_id
    data__sorted = sorted(data, key=lambda x: x[1])  # column 1 is station_id in the data object

    # Store parsed data in CSV file - just for reference
    path__data_cleaned = "Data_new/api__metars_cleaned.csv"
    file = open(path__data_cleaned, 'w', newline='', encoding='utf-8')
    writer = csv.writer(file)

    #Storing HEADER
    writer.writerow(['station_id',' observation_time', 'raw_text'])

    # Storing selected data
    # for i in range(len(data__sorted)):
    for i in range(len(data__sorted)):
        row = data__sorted[i]
        station_id = row[1]
        observation_time= row[2]
        raw_text = row[0]
        print([station_id, observation_time, raw_text])
        writer.writerow([station_id, observation_time, raw_text])

    # Converting data_sorted into a dictionary
    metars_cleaned_dict = {'station_id': [], 'observation_time':[],'raw_text': []}
    for i in range(len(data__sorted)):
        metars_cleaned_dict['station_id'].append(data__sorted[i][1])
        metars_cleaned_dict['observation_time'].append(data__sorted[i][2])
        metars_cleaned_dict['raw_text'].append(data__sorted[i][0])

    # Store tafs_cleanded_dict as json
    # Check this video: https://www.youtube.com/watch?v=pTT7HMqDnJw
    import json

    path = "Data_new/api__metars_cleaned.json"
    with open(path, "w") as f_obj:
        json.dump(metars_cleaned_dict, f_obj)


# BUTTON function - Update TAFs
def download_taf_database(parse):
    # Downloading the file  - https://www.codingem.com/python-download-file-from-url/

    url = 'https://www.aviationweather.gov/adds/dataserver_current/current/tafs.cache.csv.gz'
    response = requests.get(url)
    path__compresed = "Data_new/api__tafs_downloaded.csv.gz"

    ##  FOR DEVELOPMENT ONLY!! - -SWITCHED OFF TO AVOID LOADING from the Internet DATA EVERYTIME
    open(path__compresed, "wb").write(response.content)

    # Extracting csv.gz to csv
    path__extracted = 'Data_new/api__tafs_extracted.csv'
    with gzip.open(path__compresed, 'rt', newline='', encoding='utf-8') as csv_file:
        csv_data = csv_file.read()
        with open(path__extracted, 'wt') as out_file:
            out_file.write(csv_data)

    # Methode 1 you tube video Socratica on csv -- this methode has many problems so skip it
    lines = [line for line in open(path__extracted)]

    # methode 2 - using csv module https://www.youtube.com/watch?v=Xi52tx6phRU&t=114s
    # print(dir(csv))  # prints available methodes for csv module

    file = open(path__extracted, newline='')  # newline='' -  depending on the system strings may end in differene t way - this prowides that all works correctly across all systems
    reader = csv.reader(file)
    # Skipping 5 first lines down to the header - specific to each file
    for x in range(5):
        next(reader)
    header = (next(reader))

    # Parsing the data and converting some of it into a proper type
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

            return f'{g_key} exists!\n' \
                    f'Replaced with:\n' \
                   f'{answer_split}'

# Button functions - get decoded TAF for selected group
def load_single_METAR( station_id):
    """

    :param station_id: 4-letter STRING - station id
    :return: STRING - station METAR
    """
    path = "Data_new/api__metars_cleaned.json"

    with open(path, 'r') as f_obj:
        metars_cleaned_dict = json.load(f_obj)

    # Find METARS index based on station_id
    for i in range(len(metars_cleaned_dict['station_id'])):

        if station_id.upper() == metars_cleaned_dict['station_id'][i].upper():
            station_METAR = metars_cleaned_dict['raw_text'][i].upper()
            return station_METAR


def get_METARS_for_requested_stations(settings, requested_stations):
    """Gets metars for selecred stations.

    :param settings: class
    :param requested_stations: LIST of stations_id
    :return: LIST of STRINGS - METARs
    """
    METARs=[]
    for station in requested_stations:
        station_METAR = load_single_METAR(station)
        METARs.append(station_METAR)

    return METARs


def get_TAF_for_all_requested_stations(settings,requested_stations):
    """
    Downloads valid TAFs for airports in all_airport list
    :param settings:
    :param requested_stations: LIST of stations
    :return: LIST of TAFs
    """
    # Initializing list of TAFs for requested stations
    requested_stations_TAFs=[]

    # Getting TAFs for each station and appending it to single list
    for station in requested_stations:

        # Getting TAF for the station
        station_TAF = get_single_stations_TAF(settings,station)


        # Appending TAF
        requested_stations_TAFs.append(station_TAF)

    # Load complete message
    # print(f'   *** LOADING COMPLETED *** (fpf)  ')

    return  requested_stations_TAFs

def get_single_stations_TAF(settings,station):
    """Gets raw TAF string from TAFs json DATABASE for single station"""
    #loading json object conaining station_id and raw_text TAF

    path= "Data_new/api__tafs_cleaned.json"

    if settings.testing_decoder:
        path = "Data_new/For testing/api__tafs_cleaned.json"
        print("LOADING SPECIAL CASES!! fpf.rrrrrrrr")

    with open(path,'r') as f_obj:
        tafs_cleaned_dict = json.load(f_obj)

    # Initial value that the station is not found.

    station_TAF = [False, station] # Station INVALID - unless OVERRIDEN

    # Traversing TAFs database for station
    for i in range(len(tafs_cleaned_dict['station_id'])):

        # Station found in TAFs database - overrides initial station TAF value
        if tafs_cleaned_dict['station_id'][i]== station.upper():
            station_TAF = tafs_cleaned_dict['raw_text'][i]
            break
    if type(station_TAF)==list:
        print(station_TAF[1].upper(), " - station invalid", "(---source: (fpf.get_single_stations_TAF))\n")

    return station_TAF

### FUNCTIONS RELATED TO THE TAF DECODE



######################### FUNCTIONS ######################
def extract_stations_from_g_group(selected_g_group):
    """Returns list of stations stored in to selected g_group"""

    # Loading g_group database
    filename = 'Data/g_groups_apts_db.json'
    with open(filename) as f_obj:
        g_groups_db= json.load(f_obj)


    # Searching for selected g_group in the g_group database
    stations = []
    for k, v in g_groups_db.items():
        # If g_group found, stations in that group are appended to the list
        if k.lower() == selected_g_group.lower():
            for i in v:
                stations.append(i)

    return stations

def analise_stations(settings, requested_stations, start_time, end_time):

    # Getting TAFs for stations

    TAFs = get_TAF_for_all_requested_stations(settings,requested_stations)

    METARs_list =[]
    # if settings.on_staion_button_press_flag:
    METARs_list = get_METARS_for_requested_stations(settings,requested_stations)
        # settings.on_staion_button_press_flag= False



    # Core of the app - TAF is being coloured

    invalid_stations =[]

    decoded_TAFs_data_list =[] # Stores all stations decoded_TAFs data
    final_display__UPPER_COMBINED_threat_levels_and_winds = [] # Stores line related to threat level and runway length for SINGLE station
    for TAF in TAFs:
        # Checking if station is valid
        if type(TAF) == list: # if it is a LIST then it is not valid, so it can be processed as INVALID STATION
            valid_station = TAF[0]
            station_id = TAF[1]
            if not valid_station:
                # NOT VALID station is added to the INVALID STATION list
                print(Td_helpers.prYellow(station_id + " - invalid station"), 'ref.yyy')
                invalid_stations.append(station_id)
                continue

        # Decoding TAF
        decoded_TAF_dict = TAF_decoder_function(settings, TAF,start_time,end_time)
        decoded_TAFs_data_list.append(decoded_TAF_dict)

        # Combining station data depending on the settings
        combined_station_data = combine_data(
            settings,
            decoded_TAF_dict["station_threats"],
            decoded_TAF_dict["wind_profile"],
            decoded_TAF_dict["runways_length"],
            decoded_TAF_dict["appr_data"])

        final_display__UPPER_COMBINED_threat_levels_and_winds.append(combined_station_data)



    # Combinig stations threat and runways into single list
    combined_stations_threat_level = combine_all_stations_threat_level(final_display__UPPER_COMBINED_threat_levels_and_winds)


    return [decoded_TAFs_data_list, combined_stations_threat_level, METARs_list]





import pickle
def store_requested_station_or_group(settings, request):
    path = "Data_new/last_requested_station_or_group.json"

    # https://stackoverflow.com/questions/27745500/how-to-save-a-list-to-a-file-and-read-it-as-a-list-type

    # LOADS A LIST
    with open(path, "rb") as fp:  # Unpickling
        last_requests_list = pickle.load(fp)[0:settings.num_of_last_reqested_stations_or_groups]
        last_requests_list.insert(0,request)

    # STORES A LIST
    with open(path, "wb") as fp:  # Pickling
        pickle.dump(last_requests_list, fp)

# Extracting data from the the list of dictionaries

import math
def min_to_hours_and_days(min):
    """Converts minutes to hours and days if necessary. RETURNS STING"""
    min = int(min)
    if 0<=min<60:
        return f'{min} min'
    elif min>60:
        hours = math.floor(min/60)
        min = min%60
        if hours<24:
            if hours == 1:
                return f'{hours} hour'
            else:
                return f'{hours} hours'
        else:
            days = math.floor(hours/24)
            hours= hours%24
            if days == 1:
                return f'{days} day'
            else:
                return f'{days} days'