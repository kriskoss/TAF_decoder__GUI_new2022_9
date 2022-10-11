import final_program_functions as fpf
from TAF_decoder import TAF_decoder_function
import TAF_decoder__helper_functions as Td_helpers
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

invalid_stations =[]
decoded_TAFs_data_list =[]
stations__threat_level = []
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
    combined_station_data = fpf.combine_data(
        decoded_TAF_dict["station_threats"],
        decoded_TAF_dict["runways_length"],
        decoded_TAF_dict["appr_data"])

    stations__threat_level.append(combined_station_data)

# Combinig stations threat and runways into single list
combined_stations_threat_level = fpf.combine_all_stations_threat_level(stations__threat_level)


for decoded_TAF_dict in decoded_TAFs_data_list:
    station_name = decoded_TAF_dict["station_name"]
    selected_time_info = decoded_TAF_dict["selected_time_info"]
    decoded_TAF = decoded_TAF_dict["decoded_TAF"]
    runways_length = decoded_TAF_dict["runways_length"]
    station_threats = decoded_TAF_dict["station_threats"]
    appr_data = decoded_TAF_dict["appr_data"]

    # print(station_name)
    # print(selected_time_info)
    print(decoded_TAF)
    print(station_threats, runways_length)
    print(appr_data)

print(combined_stations_threat_level)