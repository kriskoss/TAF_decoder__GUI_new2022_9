import final_program_functions as fpf
from TAF_decoder import TAF_decoder_function
from settings import Settings
settings = Settings()
import json


my_group = "gTEST" ## just for DEVELOPMENTS

def decode_TAFs(TAFs, start_time, end_time):


    significant_range_active = False

    # Converting START TIME in hours into days and hours
    if start_time<24:
        start_day = 1
        start_hour = start_time
    else:
        """start_time>=24"""
        start_day = 2
        start_hour = start_time-24

    # Converting END TIME in hours into days and hours
    if end_time<24:
        end_day = 1
        end_hour = end_time
    else:
        """end_time>=24"""
        end_day = 2
        end_hour = end_time-24

    apt_threat_level = []

    # TAFs = fpf.load_json_TAF()
    for TAF in TAFs:
        # Checking for invalid station - if true then skip current iteration
        if fpf.no_station_msg in TAF:
            print(TAF)
            continue

        # Decoding TAF
        final_coloured_taf_string,final_line,runway_string,end_string \
            = TAF_decoder_function(TAF,
               my_day=1,
               my_time=12,
               significant_start_day= start_day ,
               significant_start_hour= start_hour,
               significant_end_day= end_day,
               significant_end_hour= end_hour,
               significant_range_active = significant_range_active,
               print_type=settings.print_type,
               print_time_group=settings.print_time_group,
        )

        fpf.append_threat_level(
            apt_threat_level,
            final_line,
            runway_string,
            end_string)

    fpf.print_coloured_apt_list(apt_threat_level)

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

# Extracting stations for selected g_group
requested_stations = extract_stations_from_g_group(my_group)

# Getting TAFs for stations
TAFs = fpf.get_TAF_for_all_requested_stations(requested_stations)

# Dumping TAFs for requested stations  -- is it necessary??
with open('Data/temp_TAFs.json', 'w') as f_obj:
    json.dump(TAFs, f_obj)


decode_TAFs(TAFs,12,24)
