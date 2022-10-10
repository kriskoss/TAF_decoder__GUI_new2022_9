import final_program_functions as fpf
from TAF_decoder import TAF_decoder_function
from settings import Settings
settings = Settings()
import json


my_group = "gTEST" ## just for DEVELOPMENTS


def extract_stations_from_g_group(selected_g_group):
    """Returns listo of stations related to selected g_group"""

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


def decode_TAFs(TAFs, start_time, end_time):

    stations__threat_level = []

    # TAFs = fpf.load_json_TAF()
    for TAF in TAFs:
        # Checking for invalid station - if true then skip current iteration
        if fpf.no_station_msg in TAF:
            print(TAF)
            continue

        # Decoding TAF
        decoded_TAF,\
        station_threats,\
        runways_length,\
        appr_data \
            = TAF_decoder_function(settings, TAF,start_time,end_time)

        # print(final_line,'AAAAAAAAAAAA')

        # Combining station data depending on the settings
        combined_station_data = fpf.combine_data(station_threats, runways_length, appr_data)

        stations__threat_level.append(combined_station_data)

    # Printing list of stations threat level
    fpf.print_coloured_apt_list(stations__threat_level)

# Extracting stations for selected g_group
requested_stations = extract_stations_from_g_group(my_group)

# Getting TAFs for stations
TAFs = fpf.get_TAF_for_all_requested_stations(requested_stations)

# Dumping TAFs for requested stations  -- is it necessary??
with open('Data/temp_TAFs.json', 'w') as f_obj:
    json.dump(TAFs, f_obj)


decode_TAFs(TAFs,12,18)
