import final_program_functions as fpf
from TAF_decoder import TAF_decoder_function
from settings import Settings
settings = Settings()
import json

######################### FUNCTIONS ######################
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


######################### PROGRAM ######################
# INPUT data
my_group = "gTEST" ## just for DEVELOPMENTS
start_time = 12
end_time = 18

# CODE
# g_group key is used to extract stations in the value part
requested_stations = extract_stations_from_g_group(my_group)

# Getting TAFs for stations
TAFs = fpf.get_TAF_for_all_requested_stations(requested_stations)

# FOR DEVELOPMNET ONLY - priniting TAFs
# for TAF in TAFs:
#     print(TAF)

# Core of the app - TAF is being coloured
stations__threat_level = []

for TAF in TAFs:
    # Checking for invalid station - if true then skip current iteration
    if fpf.no_station_msg in TAF:
        print(TAF, 'ref.yyy')
        continue

    # Decoding TAF
    decoded_TAF_dict = TAF_decoder_function(settings, TAF,start_time,end_time)

    # Extracting data from the dictionary
    selected_time_info = decoded_TAF_dict["selected_time_info"]
    decoded_TAF = decoded_TAF_dict["decoded_TAF"]
    runways_length = decoded_TAF_dict["runways_length"]
    station_threats = decoded_TAF_dict["station_threats"]
    appr_data = decoded_TAF_dict["appr_data"]


    # print(selected_time_info)
    # print(decoded_TAF)
    # print(station_threats, runways_length)
    # print(appr_data)


    # Combining station data depending on the settings
    combined_station_data = fpf.combine_data(station_threats, runways_length, appr_data)

    stations__threat_level.append(combined_station_data)

# Printing list of stations threat level
combined_stations_threat_level = fpf.combine_all_stations_threat_level(stations__threat_level)

