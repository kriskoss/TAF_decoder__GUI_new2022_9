from TAF_decoder import TAF_decoder_function
from settings import Settings
import program_functions as pf
import final_program_functions as fpf
import taf_database_program_functions as tdpf
import json
import colouring
import sys
settings = Settings()


ro=False

### STARTS program for real_time TAFs
if settings.special_case_taf_active:
    TAFs =fpf.dump_special_case_tafs()
    pf.print_list(TAFs)

elif settings.real_time_taf_active:
    #requested_airports_taf = tdpf.select_airports__use_apts_in_code().split()
        ### use this line to use code stored in code, not in json

    ## Download latest AIRPORT database?
    if input("Reload AIRPORT database? (press 'yy' for YES)") =='yy':
        fpf.download_airports_database()

    ## Download latest TAFs database?
    if input("Download latest TAFs database?") == 'y':
        fpf.download_taf_database()


    ## LOADING last requested stations form JSON file
    fpf.printing_last_requested_apts()

    ## Use last requested stations?
    answer = input('Continue(enter) or Write new airports\n')

    if answer == '':
        # Load last time requested stations
        requested_airports_taf = fpf.load_last_requested_apts()
        # TAFs = fpf.airport_selection_and_TAF_download(requested_airports_taf) -
        #   DELETED!!

    else:
        # Store new airports given
        answer = fpf.store_an_answer(answer)
        ro=True


# Running program for TAF special cases:

#  significant_range_active becomes true or false based on input
# switches:
t_once_switch = False
t_always_switch = False
m=True
def run_logic_of_type_and_time_group_display():
    """function controlling the logic of time and type group display """
    global answer, t_once_switch, m, ro
    if not t_once_switch and not t_always_switch:
        # resets the type and time group display to OFF
        settings.reset_type_and_time_group()
    ### LOGIC behind turning on or off display of time and type group
    if t_once_switch:
        answer = fpf.load_an_answer()
        t_once_switch = False

    elif t_always_switch:
        if not m:
            answer = input(fpf.prompt)
            m = True
        elif m:
            answer = fpf.load_an_answer()
            m = False

        if answer == 't' or answer == 'T':
            pass
        else:
            fpf.store_an_answer(answer)

    elif not t_always_switch and not t_once_switch:
        if ro:
            answer = fpf.load_an_answer()
            ro = False
        else:
            answer = input(fpf.prompt)

        if answer == 't' or answer == 'T':
            pass
        else:
            fpf.store_an_answer(answer)

    else:
        print('fp.check here')
        sys.exit()
    ###END

while True:
    run_logic_of_type_and_time_group_display()

    print('f_p.answer: ', answer)
    # splitting each sentence to words
    answer_split = answer.split()

        #settings.reset_type_and_time_group()
    # avaliable
    if answer == 'q':
        # if q pressed - going out of the loop
        break

    elif answer == '':
        cancel_out_of_range_msg = True
        significant_range_active = False

        fpf.print_weather_in_whole_range(cancel_out_of_range_msg, significant_range_active,settings)

    elif answer == ' ':
        print(colouring.prGreen('TO DO - print type and time_group on that was printed before'))

    elif answer == 't':
        settings.on_type_and_time_group()
        t_once_switch=True

    elif answer == 'T':
        print(' T == run')
        if not t_always_switch:
            settings.onoff_type_and_time_group()
            t_always_switch = True
        elif t_always_switch:
            settings.onoff_type_and_time_group()
            t_always_switch = False
            ro = True
        answer=fpf.load_an_answer()

    elif answer == 'show':
        """prints all airport groups stored"""
        for key,value in tdpf.apt_groups.items():
            print(key, value)

    elif all(x.isdigit() or x.isspace() for x in answer):
        """ONLY NUMBERs and spaces
            **** TAF DECODER ***"""
        if len(answer_split) == 1:
            # if 1 or 2 or 3 selected than only that day is displayed

            cancel_out_of_range_msg = True
            significant_range_active = False

            if int(answer_split[0]) == 1:
                # if answer "1" - only day 1 weather will be displayed (1-24h)
                fpf.print_weather_day1_only(cancel_out_of_range_msg, significant_range_active, settings)

            elif int(answer_split[0]) == 2:
                # if answer "2" - only day 2 weather will be displayed (25-48h)
                fpf.print_weather_day2_only(cancel_out_of_range_msg, significant_range_active, settings)

            elif int(answer_split[0]) == 3:
                # if answer "3" - only day 3 weather will be displayed (49-72h)
                fpf.print_weather_day3_only(cancel_out_of_range_msg, significant_range_active, settings)

        elif len(answer_split) == 2 \
            and (int(answer_split[0]) == 1 or int(answer_split[0]) == 2 or int(answer_split[0]) == 3) \
            and 0<= int(answer_split[1])<=24:
            significant_range_active = True
            my_day =int(answer_split[0])
            my_time = int(answer_split[1])

            apt_threat_level = []

            TAFs = fpf.load_json_TAF()
            for TAF in TAFs:
                final_coloured_taf_string,final_line, runway_string, end_string = TAF_decoder_function(TAF, my_day=my_day, my_time=my_time,
                                 significant_range=settings.significant_range,
                                 significant_range_active=significant_range_active,
                                                             print_type=settings.print_type,
                                                             print_time_group= settings.print_time_group,
                                                             )
                fpf.append_threat_level(apt_threat_level, final_line, runway_string, end_string)
            fpf.print_coloured_apt_list(apt_threat_level)

        elif len(answer_split) == 3\
            and (int(answer_split[0]) == 1 or int(answer_split[0]) == 2 or int(answer_split[0]) == 3) \
            and 0<= int(answer_split[1])<=24 \
            and 0 < int(answer_split[2]) <20:
            significant_range_active = True

            my_day =int(answer_split[0])
            my_time = int(answer_split[1])
            significant_range = int(answer_split[2])

            apt_threat_level = []

            TAFs = fpf.load_json_TAF()
            for TAF in TAFs:
                final_line, runway_string, end_string = TAF_decoder_function(TAF, my_day=my_day, my_time=my_time,
                                     significant_range=significant_range,
                                     significant_range_active=significant_range_active,
                                                             print_type=settings.print_type,
                                                             print_time_group=settings.print_time_group,
                                                             )
                fpf.append_threat_level(apt_threat_level, final_line, runway_string, end_string)
            fpf.print_coloured_apt_list(apt_threat_level)

        elif answer.isdigit and len(answer_split) == 4 \
            and (int(answer_split[0]) == 1 or int(answer_split[0]) == 2 or int(answer_split[0]) == 3) \
            and 0<= int(answer_split[1])<=24 \
            and (int(answer_split[2]) == 1 or int(answer_split[2]) == 2 or int(answer_split[2]) == 3) \
            and 0 <= int(answer_split[3]) <= 24:
                significant_range_active = False

                significant_start_day = int(answer_split[0])
                significant_start_hour = int(answer_split[1])

                significant_end_day = int(answer_split[2])
                significant_end_hour = int(answer_split[3])

                apt_threat_level = []

                TAFs = fpf.load_json_TAF()
                for TAF in TAFs:
                    final_coloured_taf_string,final_line, runway_string, end_string = TAF_decoder_function(TAF,my_day=1, my_time=12,
                                     significant_start_day=significant_start_day ,
                                     significant_start_hour=significant_start_hour,
                                     significant_end_day=significant_end_day,
                                     significant_end_hour=significant_end_hour,
                                     significant_range_active = significant_range_active,
                                                                 print_type=settings.print_type,
                                                                 print_time_group=settings.print_time_group,
                                                                 )
                    fpf.append_threat_level(apt_threat_level, final_line, runway_string, end_string)
                fpf.print_coloured_apt_list(apt_threat_level)

    else:
        print('error - wrong format')
        continue

