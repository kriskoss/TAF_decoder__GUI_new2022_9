class Settings:
    def __init__(self):
        self.becmg_cancelling_wind = 'n'  # all (y/n) - if 'y': wind/vis/weather/clouds before BECMG will be grayed out
        self.becmg_cancelling_vis = 'n'
        self.becmg_cancelling_weather = 'n'
        self.becmg_cancelling_clouds = 'n'

        self.becmg_time_group_coloring = 'y'

        self.fm_canceling = 'y'  # (y/n) if "y" than FM group is like new Initial - it cancels everything what was before
        # if "n" than it colours something more -- but this probably does not work correctly
        self.print_ranges_legend = True  # prints significant hours near final TAF
        self.print_TAF_without_colouring = False  # prins raw TAF divided in lines

        self.printing_active = False      # all print comands becomes active

        # useful in finfding errors in colouring vs siginificant tim
        self.print_colouring_logic = False # prints final dictionary/list containing logic when specific wx part is significant in terms of time
        self.no_publication_time_not_an_error = True # If True than TAF pun;ished without publication time is does not generate an error

        self.gap_symbol = ' '

        self.significant_range_active = True   # if True significatn range is based on plus/minus specific value
                                                #  if False - beginning and end of significant period is manually selected
        #if significant_range_active = True
        self.day = 1
        self.hour = 19
        self.significant_range = 3  # hours before and after selected time where weather is

        # if significant_range_active = False
        self.significant_start_day = 1
        self.significant_start_hour = 16

        self.significant_end_day = 1
        self.significant_end_hour = 18

    #######
        # Selection if use real time TAF or special case TAFs (check Data_new/TAFs__special_cases.json)
        self.real_time_taf_active = True
            # tafs are uploade real time

        self.special_case_taf_active = not self.real_time_taf_active
            # tafs are being taken from taf_special_cases.py


    ############
        # Flag used in some fucntion
        self.cancel_out_of_range_msg = False


        ### Threat weather printing settings
        self.print_in_one_line = True
        self.print_in_multiple_lines = False
        self.print_grayed_out = False

        self.print_type = False
        self.print_time_group = False
        self.type_coloured_max_thr_lvl_in_line = False
        self.time_group_coloured_max_thr_lvl_in_line = False

        self.print_green= False
        self.print_cautions= True
        self.print_warnings= True
        self.print_severe = True

        self.initial_type_rename = 'Init'
        self.t_switch = -1

        ### COLOURING THRESHOLDS
        # WX colouring thresholds
        self.severe_wx =  ['+TSGR', '+SN', 'GR']

        self.warning_wx = ['+SHSN', 'SHSN', 'SN', 'TS', '-TS', 'GR', 'FZ', 'FG',
                           'BLSN', 'IC', 'GS','FC', 'SQ', 'VA', 'SS', 'DS', ]

        self.exceptions_from_warning_and_severe = ['MIFG', '-SHSNRA', '-SHRASN', '-SN', 'RASN', 'SNRA','-SHSN']

        self.caution_wx = ['+', '-SHSN', '-SHSNRA', '-SHRASN', '-SN', 'BR', 'RA',
                           'BL', 'DR', 'SHRA', 'SG','BR', 'DU', 'FU', 'SA', 'PO',
                           'HZ', 'DZ', 'SH', 'PR', 'BC', 'MI']

        # CLOUDS colouring thresholds
        self.cloud_caution = 5
        self.cloud_warning = 3
        self.cloud_lvo_warning = 2
        self.few_caution = self.cloud_warning

        self.vv_severe = 2
        self.vv_warning = 3
        self.vv_caution = 5

        # WINDS colouring thresholds
        self.wind_caution = 15
        self.wind_warning = 30
        self.wind_severe = 40
        self.wind_gusts_caution = self.wind_caution
        self.wind_gusts_warning = self.wind_warning
        self.wind_gusts_severe = self.wind_severe

        self.vrb_caution = 7
        self.vrb_warning = 15
        self.vrb_severe = 30
        self.vrb_gusts_caution = 10
        self.vrb_gusts_warning = 25
        self.vrb_gusts_severe = 40

        # VIS colouring thresholds
        self.caution_vis = 3000
        self.warning_vis = 1500
        self.lvo = 800
        ###

        ### RUNWAY PARAMETERS
        self.very_long_runway = 3000
        self.long_runway = 2500
        self.medium_runway = 2200
        self.short_runway = 1800

        self.normal_width_runway = 45
        self.narrow_runway = 30
        ###

        ### Runway data print out
        self.print_all_rwys_data_below_taf = True
        self.rwy_data = 1
                        # 0 = no rwy data
                        # 1 = simple rwy data
                        # 2 = all rwy data
    def reset_type_and_time_group(self):
        self.print_type = False
        self.print_time_group = False

    def onoff_type_and_time_group(self):
        """Turn ON or OFF for ANY number of cycles the display of time and type data"""
        self.t_switch *= -1
        if self.t_switch == -1:
            self.print_type = False
            self.print_time_group = False

        elif self.t_switch == 1:
            self.print_type = True
            self.print_time_group = True


    def on_type_and_time_group(self):
        """turns ON type and time group display only for ONE cycle"""
        self.print_type = True
        self.print_time_group = True




