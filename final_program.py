from TAF_decoder import TAF_decoder_function
from settings import Settings
import TAF_decoder__functions as pf
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


    else:
        print('error - wrong format')
        continue

