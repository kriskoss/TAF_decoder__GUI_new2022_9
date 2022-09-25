from TAF_decoder import TAF_decoder_function
from settings import Settings
import program_functions as pf
import final_program_functions as fpf
import taf_database_program_functions as tdpf
import json
import colouring
import sys

settings = Settings()

# Loading all airports in database
avlb_apprs_data = pf.load_avlb_apprs_datra()
all_avlb_apts =[]
for appr_data in avlb_apprs_data:
    all_avlb_apts.append(appr_data[0])


ro=False
refresh_all = False
refresh_selected = False

### STARTS program for real_time TAFs
if settings.real_time_taf_active:
    #requested_airports_taf = tdpf.select_airports__use_apts_in_code().split() ## use this line to use code stored in code, not in json

    ## Refreshing TAFs for every airport
    if input("Download latest TAFs database?") == 'y':
        fpf.download_taf_database()


    ## DECIDING which apts TAFs to get.
    if not fpf.check_if_last_requested_apts_avlb():
        # No last requested airports -  prompt for new
        print('\n\tNo reqested aiports stored. Write requested airports.')
    else:
        # Last requested aiports AVLB - asks if use them or write new"""
        answer = input('Continue(enter) or Write new airports\n')

        if answer == '':
            # Load last time requested airports
            requested_airports_taf = fpf.load_last_requested_apts()
            TAFs = fpf.airport_selection_and_TAF_download(requested_airports_taf)

        else:
            # Store new airports given
            answer = fpf.store_an_answer(answer)
            ro=True


# Running program for TAF special cases:
elif settings.special_case_taf_active:
    TAFs =fpf.dump_special_case_tafs()
    pf.print_list(TAFs)

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

    elif answer == 'a':
        while True:
            # Asks for requested airports
            requested_airports_taf = fpf.promp_for_apt_selection()
            fpf.save_last_requested_apts(requested_airports_taf)
            TAFs = fpf.airport_selection_and_TAF_download(requested_airports_taf)
            break

    elif all(x.isalpha() or x.isspace() for x in answer):
        """ONLY LETTERs and spaces"""
        filename = 'Data/g_groups_apts_db.json'
        with open(filename) as f_obj:
            g_groups_db= json.load(f_obj)

        switch = True
        final_answer_split =[]
        b_switch = False
        while switch:

            for word in answer_split:
                #word = word.lower()
                if len(word) == 5 and word[0] == 'g' :
                    """g_group detected in answer"""
                    count=[]
                    for k in g_groups_db.keys():
                        if k.lower() == word.lower():
                            count.append(1)

                    """g_group not in database - create new one ?"""
                    if sum(count) == 0:
                        g_key =fpf.add_new_g_group(word)
                        answer_split = g_key.split()
                        for i in answer_split:
                            final_answer_split.append(i)
                    # g_group detected - split into stations
                    elif sum(count) == 1:
                        for k,v in g_groups_db.items():
                            if k.lower() == word.lower():
                                for i in v:
                                    final_answer_split.append(i)

                    # more than one g_group detected - select which one to use
                    elif sum(count) > 1:
                        print('More than 1 groups stored')
                        sys.exit()
                    switch= False


                elif len(word)==4:
                    """ find a way to prevent BadStation error from crashing a program"""
                    final_answer_split.append(word.lower())
                    switch = False

                else:
                    print('\n' + colouring.prRed(str(word)) +': ERROR -> must start with "g" \n')



        requested_airports_taf = fpf.answer_is_airports_only(final_answer_split)
        fpf.save_last_requested_apts(requested_airports_taf)
        fpf.airport_selection_and_TAF_download(requested_airports_taf)

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

