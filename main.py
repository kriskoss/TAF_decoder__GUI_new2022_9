## General use modules
import TAF_decoder__helper_functions as Td_helpers
import final_program_functions as fpf
from settings import Settings

import json
import math
import threading
import datetime
import pickle
import colouring


from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.window import Window
from dateutil.parser import parse   # check https://stackabuse.com/converting-strings-to-datetime-in-python/
                                    # module which automatically converts time string into the datetime format


from kivy_garden.mapview import MapView, MapMarker, MapSource

settings = Settings()

from kivy.lang import Builder
# Builder.load_file('TheTAF.kv')
Builder.load_file('page1.kv')
Builder.load_file('page2.kv')
Builder.load_file('page3.kv')
Builder.load_file('page4.kv')
Builder.load_file('page5.kv')
Builder.load_file('map.kv')


## Kivy modules
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

## TESTING
from TAF_decoder__functions import Airport

class MapControls:
    """This class is used to control the map"""
    def __init__(self):
        self.g_group_mapMarkers = []
        self.pts_btwn_apts_mapMarkers = []


    def add_current_g_group_markers(self, _app):
        """Adds markers to the map for all stations in the current g_group"""
        # Getting mapView widget
        mapView_my = _app.root.ids['map'].ids['id__MapView_my']

        # Clearing map of the previous g_group markers
        for mkr in self.g_group_mapMarkers:
            mapView_my.remove_marker(mkr)

        # This is pre-annotation syntax for type hinting
        stationObject: SingleStation

        for stationObject in app.stationsList:
            # Adding marker to the map
            mkr = MapMarker(lat=stationObject.apt_coordinates[0],
                            lon=stationObject.apt_coordinates[1])
            mapView_my.add_marker(mkr)

            # Adding marker to the list of markers - to be able to remove them later
            self.g_group_mapMarkers.append(mkr)

    def pts_btwn_apts(self, _app):
        apt1 = Airport()    # Creates empty Airport objrct
        apt1.get_airport_data_by_apt_code('EPWA')   # Populates Airport object with data

        apt2 = Airport()
        apt2.get_airport_data_by_apt_code('LEMD')

        # Getting mapView widget
        mapView_my = _app.root.ids['map'].ids['id__MapView_my']

        # Clearing map of the previous g_group markers
        for mkr in self.pts_btwn_apts_mapMarkers:
            mapView_my.remove_marker(mkr)

        # Adding DEP/DEST markers
        dep_apt = apt1
        dest_apt = apt2
        dep_mkr = MapMarker(lat=dep_apt.lat, lon=dep_apt.lon)
        dest_mkr = MapMarker(lat=dest_apt.lat, lon=dest_apt.lon)

        mapView_my.add_marker(dep_mkr)
        mapView_my.add_marker(dest_mkr)

        ### Adding markers at interpolated coordinates ###

        steps = 10
        lat_step = (dest_apt.lat - dep_apt.lat)/steps
        lon_step = (dest_apt.lon - dep_apt.lon)/steps

        for i in range(10):
            lat_mkr = dep_apt.lat + i*lat_step  # Calculates the marker coordinates
            lon_mkr = dep_apt.lon + i*lon_step

            mkr = MapMarker(lat = lat_mkr, lon= lon_mkr)    # Creates marker object
            mkr.source= "Resources/MapMarkers/inter_mkr.png"
            mapView_my.add_marker(mkr)  # Adds marker to the map
            self.pts_btwn_apts_mapMarkers.append(mkr) # Add markers to the list - this enables removal of the markers later



class MapView_my(MapView):
    """Class for the mapview widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lat = 50
        self.lon = 11

class TAF_StackLayout(BoxLayout):
    #### FOR TESTING!!
    def __init__(self,**kwargs):
        super(TAF_StackLayout, self).__init__(**kwargs)

        lbl = Label(
            text=app.single_decoded_TAF,
            # size_hint=(1, None),
            # height=dp(40),
            font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
            font_size='20dp'
        )

        self.add_widget(lbl)

        # Adding buttons to the layout

        print(app.global_decoded_TAFs_data_list, 'main.ssssssssss')
        for decoded_TAF_dict in app.global_decoded_TAFs_data_list:
            decoded_TAF = decoded_TAF_dict["decoded_TAF"]
            decoded_TAF = decoded_TAF.replace('space.Tdf', '   ')
            app.global_decoded_TAF= decoded_TAF

            lbl = Label(
                text='decoded_TAF',
                # size_hint=(1, None),
                # height=dp(40),
                font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                font_size='20dp'
            )

            self.add_widget(lbl)

class TAF_groups_Stack(StackLayout):

    def __init__(self, **kwargs):  # __init__ is the constructor, ** kwargs is required for internal working of KIVY
        super(TAF_groups_Stack, self).__init__(**kwargs)

        # Creates first set of g_group buttons
        app.create_g_group_buttons(self)
        app.create_SINGLE_station_buttons(self, False)

class Last_requests(StackLayout):
    def __init__(self, **kwargs):
        super(Last_requests, self).__init__(**kwargs)
        app.create_last_requests_buttons(self,settings)

class Add_Group(BoxLayout):
    """ Methods used to Add and Edit new g_group"""

    # Adds new g-group in to the database
    new_group_str =StringProperty("")
    time_now = datetime.datetime.utcnow()

    terminal_answer=StringProperty('')
    terminal_answer=StringProperty('')

    def on_text_validate(self,widget):
        # Storing ANY input as UPPERCASE string
        self.new_group_str = widget.text.upper()


    def call_add_new_group(self):
        answer_split = self.new_group_str.split()
        for item in answer_split:
            item.upper()

        # Counting how many XXXX strings are in the TextInput answer
        counter = 0
        for item in answer_split:
            if len(item) == 4 and item.isalpha():
                counter += 1

        # CONTINUE only if all splits of the answer are of lngth XXXX
        if counter == len(answer_split) and counter>0:

            # Correct format -  ADDED new g_group
            self.terminal_answer = fpf.add_new_group(answer_split)
        else:
            # Wrong format - NOT STORED
            self.terminal_answer = "Try format: XXXX XXXX XXXX etc. "

class TheTAFApp(App):

    ### OBJECTS ###
    mapControls = MapControls()

    ### GLOBAL VARIABLES ###

    requested_stations ='none'
    # Sets the initial value of the time sliders

    time_now =datetime.datetime.utcnow()
    value__start_slider = StringProperty(str(time_now.strftime("%H")))
    value__end_slider = StringProperty('48')


    # STRINGPROPERTY and BOOLEAN PROPERTY realtime update of the string!!
    start_ddhh = StringProperty(str(Td_helpers.hours_to_ddhh(int(time_now.strftime("%H")))))
    end_ddhh = StringProperty('dd')

    # Lable which display the decoded TAF
    label__stations_threat_levels = StringProperty('label__stations_threat_levels')
    # label__decoded_TAFs = StringProperty('label__decoded_TAFs')

    # Initializin for fina display
    display_TOP = StringProperty('display_TOP')
    display_METARs = StringProperty('display_METARs')
    display_TAFs = StringProperty('display_TAFs')
    extended_TAFs_display =StringProperty('extended_TAFs_display')

    ## SINGLE TAF (page 5)
    station_name = StringProperty('sation_name')
    station_TAF =StringProperty('station_TAF')
    station_METAR =StringProperty('station_METAR')
    station_APPRs = StringProperty('station_APPRs')

    font_counter = 2
    font_step = 3

    TAF_display_font_size = StringProperty(str( 14+ font_counter * font_step) + 'dp')
    search_input = StringProperty('')


    TAFs_validity__earliers_start_txt = StringProperty('7') # Initial sting inside has to be number
    TAFs_validity__latest_end_txt = StringProperty('12')    # Initial sting inside has to be number

    time_label_txt = terminal_answer=StringProperty(time_now.strftime("%H:%M")+'UTC +' + str(settings.SINGLE_station_time_range) + 'h for THR LEVEL' )

    search_hint = StringProperty("Search")

    current_time_str = StringProperty("current_time_str")
    color_on__t_range = StringProperty(str(settings.SINGLE_station_time_range))

    # FOR TESTING
    global_decoded_TAFs_data_list = []
    global_decoded_TAF = ''
    single_decoded_TAF = StringProperty('')
    num_TAFs_downloaded = StringProperty('0')

    reload_status=StringProperty("#935999")
    reload_button_msg = StringProperty("Reload TAFs")
    current_time_str = StringProperty(current_time_str)
    PAGE1_time_range = StringProperty('fffffff')

    need_to_update_TAFS = False
    need_to_update_TAFS_for_buttons = False
    max_thrts_at_apts = []
    ready_for_colouring_of_single_station_buttons = False

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # YouTube reference:  https://stackoverflow.com/questions/73079260/kivy-how-to-access-global-variables-in-kv-file
        # Initializing global variables --- (__init__ above required!!)
        self.selected_g_group = ''  # Just to avoid pycharm caution display

        # Renaming self to app to enable direct the Main App object in other classes
        global app
        app = self
                ### END of youtube reference
        self.g_groups_db = self.load_g_groups_db()

        # self.call_TAFs_reload()
        self.update_clock() # SIDE EFFECT of this function is the last RELOAD time displayed correctyly



    def build(self):
        # Schedule the self.update_clock function to be called once a second
            # REFERENCE: https://stackoverflow.com/questions/54426193/how-to-have-an-updating-time-in-kivy
        Clock.schedule_interval(self.update_clock, 0.2) # called every X seconds

    # Initializig
    time_delta_minutes = StringProperty('-1')
    reload_TAFs_msg = StringProperty('reload_TAFs_msg')
    last_reload_failed = False

    def update_clock(self, *args):

        # Called once a second using the kivy.clock module
        self.utc_now = datetime.datetime.utcnow()
        self.current_time_str = self.utc_now.strftime('%H:%M:%S')

        # Loading LAST UPDATE TIME
        path = "Data_new/last_reload_time.json"
        with open(path) as f_obj:
            last_update_time = json.load(f_obj)
            # create DATETIME object from STRING of the following format
            last_update__object = datetime.datetime.strptime(last_update_time, "%H:%M'%S UTC  %d-%m-%Y")

            time_delta__object = self.utc_now - last_update__object

            self.time_delta_minutes = str(math.floor(time_delta__object.total_seconds() / 60))

            self.reload_TAFs_msg = f'Last reload  {last_update__object.strftime("%H:%M UTC ,%d-%m-%Y ")},  {fpf.min_to_hours_and_days(self.time_delta_minutes)} ago, {self.num_TAFs_downloaded} TAFs'
            if self.last_reload_failed:
                self.reload_TAFs_msg  = f'Reload FAILED. Last reload {fpf.min_to_hours_and_days(self.time_delta_minutes)} ago. {self.num_TAFs_downloaded} TAFs'

            if self.find_thread("Preparing_MaxThreatLevels_THREAD"):
                self.reload_TAFs_msg  = "LOADING..."

        # UPDATES decoded TAFs only when flag true - CASE FOR PAGE2 SLIDER MOVEMENT
        if self.need_to_update_TAFS:
            self.need_to_update_TAFS = False

            self.update_TAFs(settings,
                             self.requested_stations,
                             self.value__start_slider,
                             self.value__end_slider)

        # UPDATE BUTTONS - COLOUR ADDED - runs only when THREAD complete
        if (not self.find_thread("Preparing_MaxThreatLevels_THREAD")) and self.ready_for_colouring_of_single_station_buttons:
            self.ready_for_colouring_of_single_station_buttons = False

            widget = self.root.ids.id__Page1.ids.id__TAF_groups__scroll.ids.id__TAF_groups_Stack
            # widget = self.root.ids.id__Page1.ids.id__TAF_groups__scroll.ids['id__TAF_groups_Stack']

            # Removes all GRAY buttons and replace them with COLOURED ones
            widget.clear_widgets()
            self.create_g_group_buttons(widget)
            self.generate_single_station_buttons(widget)


    def find_thread(self,name):
        """Checks if THREAD of specific name exists
        REURNS: bool"""
        for thread in threading.enumerate():
            if thread.name == name:
                return True
        return False

    def update_TAFs(self, settings, stations_, start, end):

        ### RECREATING LAST REQUESTED airports list
        # GETTING AN ITEM by ID!!!
        id__Last_requests = app.root.ids.id__Page1.ids.id__Last_requests__scroll.ids.id__Last_requests  #### DIRECT PATH!!!!!

        # CLEAR LAST REQUESTED buttons
        id__Last_requests.clear_widgets()

        # RECREATING the LAST REQUESTED buttons
        ### BLOCKED to prevent doubling of the LAST REQUESTED BUTTONS list
        app.create_last_requests_buttons(id__Last_requests, settings)
        ### END

        decoded_TAFs_data_list, stationsList ,combined_stations_threat_level, METARs_list= \
            fpf.analise_stations(settings, stations_,
                                   int(start), int(end))

        # Converting LISTs to be GLOBAL
        self.stationsList= stationsList
        self.METARs_list = METARs_list


        decoded_TAFs = []
        TAFs_validity_start_times =[]
        TAFs_validity_end_times =[]
        max_threat_level_at_airports =[]

        # Making DECODED TAFs data available in the whole APP
        app.global_decoded_TAFs_data_list = decoded_TAFs_data_list

        for decoded_TAF_dict in decoded_TAFs_data_list:
            # Looping throughout all STATIONS

            station_name = decoded_TAF_dict["station_name"]
            #SEPARATOR between STATION TAFs
            station_name=f'\n\n_________________________\n' \
                         f'   ******* {station_name} ******* '

            # Adding STATION NAME to TAF label
            decoded_TAFs.append(station_name)
            # selected_time_info = decoded_TAF_dict["selected_time_info"]

            # REPLACING PLACEHOLDERS (2022.10)
            decoded_TAF = decoded_TAF_dict["decoded_TAF"]
            decoded_TAF=decoded_TAF.replace('space.Tdf', '   ')
            decoded_TAFs.append(decoded_TAF)  ## APPEND - VERY IMPORTATN!!! - here it is being decided what is being printed out

            runways_length = decoded_TAF_dict["runways_length"]
            station_threats = decoded_TAF_dict["station_threats"]
            appr_data = decoded_TAF_dict["appr_data"]

            max_threat_level_at_airport =decoded_TAF_dict['max_threat_level_at_airport']
            max_threat_level_at_airports.append((station_name,max_threat_level_at_airport))
                        ### Getting MAX THREAT LEVEL for the single station


            ### FINDING VALID TAFs range ###
            # Selecting TAFs validity period among time ranges of TEMPO, PROB, etc
            TAFs_validity_period = decoded_TAF_dict["time_range"]
            TAFs_validity_start_times.append(TAFs_validity_period[1][0])
            TAFs_validity_end_times.append(TAFs_validity_period[1][1])


            # ADDING APPR DATA to the decoded TAF string
            if settings.print_appr_info:
                decoded_TAFs.append('\n      ----------RWY & APPR------------\n'+
                                    appr_data+
                                    '\n      ----------RWY & APPR------------')
            ## TESTING
            self.single_decoded_TAF='decoded_TAFs'


        # FINDING earliest TAF validity START hour and LATEST end HOUR
        try:
            self.TAFs_validity__earliers_start_txt = str(min(TAFs_validity_start_times))
            self.TAFs_validity__latest_end_txt = str(max(TAFs_validity_end_times))
            print(TAFs_validity_start_times, TAFs_validity_end_times, "main.ddddddd")
        except ValueError:
            ### If g_group exists, BUT all g_group stations are missing in the latest TAFs
            print('No stations available!! - main.py')
            ## UPDATING PAGE 2 label
            app.display_TOP = colouring.prRed(" STATIONS NOT AVAILABE!" ) \
                              + "[size=14dp] \n- try to refresh TAFs in a few minutes " \
                                "\n- check g_group stations[/size]"

            app.display_METARs=''
            app.display_TAFs=''
            app.extended_TAFs_display=''
        #### UPDATING FINAL DISPLAY!!!!! -- START HERE TO MODIFY ANYTHING
        else:
            self.update_FINAL_DISPLAY(combined_stations_threat_level, decoded_TAFs, METARs_list, settings)
        return max_threat_level_at_airports

    def get_max_threat_level_for_selected_airports(self, settings, stations_, start, end):
        """
        BASED ON: update_TAFs => Gets the max threat level for selected airports -
        but it can be PROBABLY run in separate THREAD because it do NOT change the GUI graphics part"""

        decoded_TAFs_data_list, stationsList ,combined_stations_threat_level, METARs_list= \
            fpf.analise_stations(settings, stations_,
                                   int(start), int(end))

        # Converting LISTs to be GLOBAL
        self.stationsList= stationsList
        # self.METARs_list = METARs_list

        decoded_TAFs = []
        max_threat_level_at_airports =[]

        # Making DECODED TAFs data available in the whole APP
        app.global_decoded_TAFs_data_list = decoded_TAFs_data_list

        for decoded_TAF_dict in decoded_TAFs_data_list:
            # Looping throughout all STATIONS

            station_name = decoded_TAF_dict["station_name"]
            #SEPARATOR between STATION TAFs
            station_name=f'\n\n_________________________\n' \
                         f'   ******* {station_name} ******* '

            # Adding STATION NAME to TAF label
            decoded_TAFs.append(station_name)
            # selected_time_info = decoded_TAF_dict["selected_time_info"]

            # REPLACING PLACEHOLDERS (2022.10)
            decoded_TAF = decoded_TAF_dict["decoded_TAF"]
            decoded_TAF=decoded_TAF.replace('space.Tdf', '   ')
            decoded_TAFs.append(decoded_TAF)  ## APPEND - VERY IMPORTATN!!! - here it is being decided what is being printed out

            max_threat_level_at_airport =decoded_TAF_dict['max_threat_level_at_airport']
            max_threat_level_at_airports.append((station_name,max_threat_level_at_airport))

        return max_threat_level_at_airports



    initial_difference_str = StringProperty("0")
    current_difference_str = StringProperty("993")

    def update_FINAL_DISPLAY(self,combined_stations_threat_level,decoded_TAFs, METARs_list,settings):
        """ FINAL DISPLAY STRUCTURE
        1.  UPPER displa - threat levels, threats and wind profile
        2. METARS
        3. Detailed TAFs"""

        METARs_final_string = ''
        if settings.display_METARs_on_page2:
            METARs_list = ["\n ####### METARS ###########"] + METARs_list

            for item in METARs_list:
                if item:
                    METARs_final_string = METARs_final_string + '\n\n' + item

        ### CREATOING DATA for MAIN LABELS : TOP, METARS, TAFS, and insering new line
        combined_stations_threat_level = combined_stations_threat_level.replace("newlinee.Tdf", '\n')
        self.display_TOP = combined_stations_threat_level

        self.display_METARs = METARs_final_string
        middle = round(len(decoded_TAFs)/2)
        # 1st HALF of TAFs
        decoded_TAFs__string_top = '\n\n'.join(decoded_TAFs[:middle])
        decoded_TAFs__string_top = decoded_TAFs__string_top.replace("newlinee.Tdf", '\n')

        self.display_TAFs = decoded_TAFs__string_top

        # 2nd HALF of TAFs
        decoded_TAFs__string_bottom = '\n\n'.join(decoded_TAFs[middle:])
        decoded_TAFs__string_bottom = decoded_TAFs__string_bottom.replace("newlinee.Tdf", '\n')
        self.extended_TAFs_display = decoded_TAFs__string_bottom

        #### REPLACED by ABOVE CODE
        # # Decoding symbols - adding NEW LINE symbol
        # self.label__decoded_TAFs = self.label__decoded_TAFs.replace("newlinee.Tdf", '\n')

    def record_difference(self):
        # ON TOUCH moment ONLY - calculating time difference between START and END SLIDERS
        self.initial_difference_str = str(int(self.value__end_slider) - int(self.value__start_slider))
        """It is necessary to KEEP the distance between START and END sliders - only when START SLIDER is used"""

    def calculating_current_difference(self):
        self.current_difference_str =str(int(self.value__end_slider)-int(self.value__start_slider))

    def on_time_slider__touch_up(self):

        if not settings.update_TAFs_in_real_time_when_slider_moved:
            print('main.suspect4')
            self.update_TAFs(settings,
                self.requested_stations,
                self.value__start_slider,
                self.value__end_slider)
        else:
            pass
    def on_slider_value__start(self, widget):
        # Runs only PAGE2 is being displayed

        if app.root.current == "second":
            if int(self.trend)!=0:
                # Getting START SLIDER value
                self.value__start_slider = str(int(widget.value))
                self.calculate_trend__start_slider()


                # Updates END slider value to keep consant DIFFERNECE - SLIDERS move TOGETHER
                self.value__end_slider = str(int(self.value__start_slider) + int(self.initial_difference_str))

                self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.value__start_slider, self.value__end_slider)

                if settings.update_TAFs_in_real_time_when_slider_moved:
                    print('main.suspect4')
                    # self.update_TAFs(settings,
                    #     self.requested_stations,
                    #     self.value__start_slider,
                    #     self.value__end_slider)

                    # self.need_to_update_TAFS=True

                # Just to make display of day:hh

                self.start_ddhh = Td_helpers.hours_to_ddhh(int(widget.value))

                self.prev_start_slider_value= self.value__start_slider
    def on_slider_value__start_RELEASED(self):
        self.need_to_update_TAFS = True

    def on_slider_value__end_RELEASED(self):
        self.need_to_update_TAFS = True

    prev_end_slider_value = 0
    prev_start_slider_value = 0
    trend = StringProperty('994')

    # def on_slider_value__end(self,widget):
    #     thr = threading.Thread(target=self.on_slider_value__end_IN_THREAD, args = [widget])
    #     thr.start()
    def on_slider_value__end(self, widget):
        ## It runs only when PAGE2 is displayed
        if app.root.current == "second":
            if int(self.trend) != 0:
                self.value__end_slider = str(int(widget.value))

                self.calculate_trend__end_slider()

                # SLIDER BEHAVIOUR - prevents END slider TO MOVE before RIGHT
                if int(self.trend) < 0 and int(self.current_difference_str) <= 0:
                    # IF END slider is moving LEFT and reaches the START slider then they MOVE TOGETHER
                    self.initial_difference_str = "0"  ## MUST BE HERE!!! - prevents from erratic movement!!

                    self.value__start_slider = self.value__end_slider

                self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.value__start_slider, self.value__end_slider)

                ## Update TAFs in real time
                if settings.update_TAFs_in_real_time_when_slider_moved:
                    print('main.suspect1', self.value__start_slider, self.value__end_slider)

                    """Updating TAF at each step of slider movement - real time"""
                    # self.update_TAFs(settings,
                    #                  self.requested_stations,
                    #                  self.value__start_slider,
                    #                  self.value__end_slider)

                    """Updating only at the main clock interval 1 sec"""
                    # self.need_to_update_TAFS = True

                # Just to make display of day:hh
                self.end_ddhh = Td_helpers.hours_to_ddhh(int(widget.value))
                self.prev_end_slider_value = self.value__end_slider


    def calculate_trend__end_slider(self):
        self.trend = str(-int(self.prev_end_slider_value) + int(self.value__end_slider))

    def calculate_trend__start_slider(self):
        self.trend = str(-int(self.prev_start_slider_value) + int(self.value__start_slider))


    def update_scroll_height(self):

        # MyLabel = app.root.ids.id__Page2.ids.MyLabel

        # Resizing window to make scroll size work correctly -- TO BE TESTED ON THE CELL PHONE
        if Window.size[0]%2 == 0:
            Window.size=(Window.size[0]+1,Window.size[1])
        else:
            Window.size=(Window.size[0]-1,Window.size[1])

    def update_TAFs_display_labels(self):
        """ Labels are updated on function activation - used to update TAF display (VERY IMPORTANT!!!)"""
        # https://www.youtube.com/watch?v=TEpHeuH7wNw&list=WL&index=3

        # Getting elements (using IDs)
        # label__test = app.root.ids.id__Page1.ids.label__test
        # label__taf_display = app.root.ids.id__Page2.ids.lebel__taf_display



        # Updating elements
        self.TAF_decoder__input_data = self.combine_data(self.selected_g_group,self.value__start_slider,self.value__end_slider)
        self.label__stations_threat_levels  = self.TAF_decoder__input_data

    def combine_data(self, data1, data2, data3):
        """Just combines data into one element - to avoid repeating the code"""

        return str([data1, data2, data3])



    period_counter= int(datetime.datetime.utcnow().strftime("%H"))
    def update_range(self,direction):
        """ Changes the value of the period that wil be selected at each BUTTON click"""
        self.record_difference()
        # Decrase/increase selected period
        if direction == "increase":
            self.period_counter += settings.on_click__time_jump
        if direction == "decrease":
            self.period_counter -= settings.on_click__time_jump


        # Resets counter when the max value reached
        ##### LIMITS OF THE SLIDERS
        # if self.period_counter > int(self.TAFs_validity__latest_end_txt) - int(self.initial_difference_str):
        #     self.period_counter = int(datetime.datetime.utcnow().strftime("%H"))
        # if self.period_counter < int(datetime.datetime.utcnow().strftime("%H")):
        #     self.period_counter = int(self.TAFs_validity__latest_end_txt)-int(self.initial_difference_str)
        # Updates BUTTON description

        self.value__start_slider = str(self.period_counter)

        self.value__end_slider = str(self.period_counter + int(self.initial_difference_str))

    def call_AIRPORTS_reload(self):
        fpf.download_airports_database()

    def load_g_groups_db(self):
        filename = 'Data/g_groups_database_ONLY/g_groups_apts_db.json'
        with open(filename) as f_obj:
            g_groups_db = json.load(f_obj)
        return g_groups_db

    """Methodes related to TOP BAR"""

    def call_TAFs_reload(self):
        def reload_TAFsMETARS():
            self.num_TAFs_downloaded = str(fpf.download_taf_database(parse))
            fpf.download_metars_database(parse)

        # TRYING to UPDATE TAFs
        try:
            reload_TAFsMETARS()
        # UPDATE FAILED
        except:
            # set FLAG to TRUE
            self.num_TAFs_downloaded = '--'
            self.last_reload_failed = True
            print(" ########## UPDATE FAILED ############")
            self.reload_status = "#ff0015"
            self.reload_button_msg = "TAFs Reload - FAILED!"

        # UPDATE SUCCESSFUL
        else:
            # set FLAG to FALSE
            self.last_reload_failed = False

            # create STRING from DATETIME object using the following format
            reload_time = datetime.datetime.utcnow().strftime("%H:%M'%S UTC  %d-%m-%Y")

            # Saving last update time
            path = "Data_new/last_reload_time.json"
            with open(path, "w") as f_obj:
                json.dump(reload_time, f_obj)

            # Updating button and label
            self.reload_status = "#00ff59"
            self.reload_button_msg = "TAFs Reload - SUCCESSFUL"
            print("MAIN.py -- RELAOD COMPLETE")

    def call_TAFs_reload_THREAD(self):
        """This funciton first defines function that then will be run in the THREAD
        --->>may need to be refactored """

        """Runs RELOAD in separate thread """
        t1 = threading.Thread(target=self.call_TAFs_reload, args=[])
        t1.start()



    def show_T_time_toggle(self, widget):
        # Toggle to show TIME range of any wx at or above CAUTION level
        init_label = "T:"
        if widget.state == "normal":
            # OFF
            widget.text = init_label + "OFF"

            settings.onoff_type_and_time_group()
        else:
            # ON
            widget.text = init_label + "ON"

            settings.onoff_type_and_time_group()
            # settings.print_time_group = True

        print('main.suspect2')
        self.update_TAFs(settings,
            app.requested_stations,
            app.value__start_slider,
            app.value__end_slider)

        self.update_TAFs_display_labels()


    def print_appr_info__toggle(self, widget):
        if widget.state == "normal":
            # OFF
            settings.print_appr_info = False
        else:
            # ON
            settings.print_appr_info = True
            # settings.print_time_group = True


        self.update_TAFs(settings,
            app.requested_stations,
            app.value__start_slider,
            app.value__end_slider)

        self.update_TAFs_display_labels()
    def update_search_input(self,widget):
        self.search_input = widget.text
        print(self.search_input, "main.search_input")

        self.refresh_station_buttons(False)


    def create_g_group_buttons(self,widget):
        """Creates the g_group buttons in the widget element (has to be LAYOUT element?) """
        # Loading g_groups data from .json
        g_groups_db = app.load_g_groups_db()
        # Creating g_groups buttons

        search = app.search_input
        for g_group_key, v in g_groups_db.items():

            # Skips all buttns which do not met search results
            if not search.upper() in g_group_key.upper():
                continue

            btn = Button(
                text=f'{g_group_key[0].lower()+g_group_key[1:].upper()}',
                size_hint=(1, None),
                height=dp(40),
                font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                font_size='20dp'
            )

            # ADDING buttons IDs dictionary
            # https://stackoverflow.com/questions/50099151/python-how-to-set-id-of-button
            widget.ids[g_group_key] = btn  # CORRECT WAY based on the above

            # BINDING event with method - VERY IMPORTANT!
            btn.bind(on_press=self.on_press_g_group)

            # Adding buttons to the layout
            widget.add_widget(btn)

    def change_colour_depending_on_threat_level(self, threat_level):
        """Changes b_colour depending on the threat level
        INPUT: threat level string (severe, warning, green, caution)
        OUTPUT: COLOR STRING to be used
        """
        b_colour='#454545'
        if threat_level == "severe":
            b_colour = '#370557'  # MAGENTA
        elif threat_level == "warning":
            b_colour = '#961509'  # RED
        elif threat_level == "caution":
            b_colour = '#967a09'  # YELLOW
        elif threat_level == "green":
            b_colour = '#0a6932'  # GREEN
        return b_colour


    def create_SINGLE_station_buttons(self,widget,change_time_range):
        """Creates single station BUTTONS
        INPUT: change_time_range IF:
            FALSE - first GRAY buttons will be created, then once MAX_THREAT THREAD will be complete the buttons will be removed and COLOURED ONES created instead
            TRUE - then GRAY buttions will not be created first before colouring"""
        TheTAFApp.get_stations_that_match_search()


        t1 = threading.Thread(name="Preparing_MaxThreatLevels_THREAD",target=self.get_max_threat_level_for_selected_stations)
        t1.start()

        self.ready_for_colouring_of_single_station_buttons = True

        # Adding GRAY buttons - to be repalced by COLOURED buttions when THREAD complete
        if not change_time_range:
            self.generate_single_station_buttons_GRAY(widget)


    @staticmethod
    def get_stations_that_match_search():
        search_input = app.search_input

        # Opening TAF vs station database
        path = "Data_new/api__tafs_cleaned.json"

        with open(path, 'r') as f_obj:
            tafs_cleaned_dict = json.load(f_obj)

        ######### Getting stations to show ##############
        stations_to_show=[]

        # Look for stations in the database only if search input 2-4 letters long
        if 1 < len(search_input) < 5:
            for station in tafs_cleaned_dict['station_id']:

                # Check if search input is in any station_id
                if search_input.upper() in station.upper():

                    # If search input in station_id, the store the station
                    stations_to_show.append(station)

        # Updating requested_stations so it is more efficient as UPDATE TAF runs 5x times (FIXED)
        app.requested_stations = stations_to_show

    def get_max_threat_level_for_selected_stations(self):
        if len(self.search_input)>=settings.min_num_of_char:
            if len(self.requested_stations)> 0:
                # Has to callit self so sliders_values use the same value ()
                app.requested_stations= app.requested_stations[:settings.max_num_of_colored]
                print("suspect3", 'main.333333')
                # self.max_thrts_at_apts = self.update_TAFs(settings, app.requested_stations, int(self.value__start_slider), int(self.value__start_slider) + settings.SINGLE_station_time_range)
                self.max_thrts_at_apts = self.get_max_threat_level_for_selected_airports(settings, app.requested_stations, int(self.value__start_slider), int(self.value__start_slider) + settings.SINGLE_station_time_range)
                # self.need_to_update_TAFS_for_buttons= True

    def generate_single_station_buttons(self,widget):
        ####### GENERATIN BUTTONS ?? ##########
        if len(app.requested_stations) > 0:
            i=0
            for station in app.requested_stations:
                b_colour = '#474747'    # GRAY-BLUE
                # if i<len(max_threat_level_at_airports):
                if i<len(self.max_thrts_at_apts):
                    # THREAT LEVEL at SINGLE STATION
                    # station_threat_level =max_threat_level_at_airports[i][1][0]
                    station_threat_level =self.max_thrts_at_apts[i][1][0]

                    # Get colour depending on the threat level
                    b_colour=self.change_colour_depending_on_threat_level(station_threat_level)


                i+=1
                btn = Button(
                    text=station.upper(),
                    size_hint=(0.33, None),
                    height=dp(40),
                    # width=dp(100),
                    font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                    font_size='20dp',

                    background_color = b_colour,
                    background_normal='' #MODIIES HOW COLOR ARE BEING DISPLAYED
                )

                widget.ids[station] = btn  # CORRECT WAY based on the above

                # BINDING event with method - VERY IMPORTANT!
                btn.bind(on_press=self.load_single_TAF)

                # Adding buttons to the layout
                widget.add_widget(btn)


    def generate_single_station_buttons_GRAY(self,widget):
        ####### GENERATIN BUTTONS ?? ##########
        if len(app.requested_stations) > 0:
            i=0
            for station in app.requested_stations:
                b_colour = '#474747'    # GRAY-BLUE
                # if i<len(max_threat_level_at_airports):


                i+=1
                btn = Button(
                    text=station.upper(),
                    size_hint=(0.33, None),
                    height=dp(40),
                    # width=dp(100),
                    font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                    font_size='20dp',

                    background_color = b_colour,
                    background_normal='' #MODIIES HOW COLOR ARE BEING DISPLAYED
                )

                widget.ids[station] = btn  # CORRECT WAY based on the above

                # BINDING event with method - VERY IMPORTANT!
                btn.bind(on_press=self.load_single_TAF)

                # Adding buttons to the layout
                widget.add_widget(btn)

    def getting_decoded_TAF_data_for_SINGLE_STATION(self,station_name):
        """getting ALL data returned by TAF_decoder (station_name, max_threat_level, ect) for SINGLE STATION
        INPUT: station_name STRING (do not mistake with LIST for similar function)"""

        ## GETTING THREAT LEVEL FOR THE STATION
        input_text = station_name

        # Opening TAF vs station database
        path = "Data_new/api__tafs_cleaned.json"

        with open(path, 'r') as f_obj:
            tafs_cleaned_dict = json.load(f_obj)
        # Checking if TAF in database
        if input_text.upper() in tafs_cleaned_dict['station_id']:

            # print(int(self.value__start_slider),
            #       int(self.value__start_slider) + settings.SINGLE_station_time_range,'main.oooooooo')
            dispalyed_start = int(self.value__start_slider)
            dispalyed_end = int(self.value__start_slider) + settings.SINGLE_station_time_range
            app.PAGE1_time_range = f'[b]{app.color_on__t_range}h[/b] COLOR RANGE,     {Td_helpers.hours_to_ddhh(dispalyed_start)} -  {Td_helpers.hours_to_ddhh(dispalyed_end)}  '
            ## GETTING THREAT LEVEL FOR SINGLE STATION
            station_name = [station_name]  ## ONLY ONE STATION - nested functions require LIST not STRING
            decoded_TAFs_data_list, stationsList, _NOT_USED ,_NOT_USED= fpf.analise_stations(
                 settings,
                 station_name,
                 int(self.value__start_slider),
                 int(self.value__start_slider) + settings.SINGLE_station_time_range)
            if len(decoded_TAFs_data_list) > 0:
                return decoded_TAFs_data_list[0] # [0] because there is onlyu one station and usually data is returned for multiple stations
            else:
                print('main.errror 21144')

    def create_last_requests_buttons(self,widget,settings):
        path = "Data_new/last_requested_station_or_group.json"
        with open(path, "rb") as fp:  # Unpickling
            last_requests_list = pickle.load(fp)[0:settings.num_of_last_reqested_stations_or_groups]

            #REMOVING DUPLICATES
            last_requests_list = list(dict.fromkeys(last_requests_list))


            # Spliting into SINGLE STATION and g_group
            for item in last_requests_list:
                if len(item) == 4:

                    decoded_single_TAF_dict = self.getting_decoded_TAF_data_for_SINGLE_STATION(item)

                    single_station__max_threat_level=-1 # not sure if necessary - ADDED to prevent errors but not sure why the error comes at the first place

                    if decoded_single_TAF_dict:
                        #single_station__name = decoded_single_TAF_dict['station_name']
                        single_station__max_threat_level = decoded_single_TAF_dict['max_threat_level_at_airport'][0]

                    ### Colours the LAST REQUESTED AIRPORTS buttons
                    # COLOR_ON
                    if settings.min_num_of_char != 5:
                        last_req_single_station__b_colour = self.change_colour_depending_on_threat_level(single_station__max_threat_level)
                    # COLOR OFF
                    else:
                        last_req_single_station__b_colour ="#312f42"


                    # SINGLE STATION
                    btn = Button(
                        text=item.upper(),
                        size_hint=(1, None),
                        height=dp(40),
                        # width=dp(100),
                        font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                        font_size='20dp',
                        background_color=last_req_single_station__b_colour,
                        background_normal = ''  # MODIIES HOW COLOR ARE BEING DISPLAYED
                    )

                    widget.ids[item] = btn  # CORRECT WAY based on the above

                    # BINDING event with method - VERY IMPORTANT!
                    btn.bind(on_press=self.load_single_TAF)

                    # Adding buttons to the layout
                    widget.add_widget(btn)

                else:
                    # g_group
                    btn = Button(
                        text=f'{item[0].lower() + item[1:].upper()}',
                        size_hint=(1, None),
                        height=dp(40),
                        font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                        font_size='20dp',
                        background_color = "#7ca4e6"
                    )

                    # ADDING buttons IDs dictionary
                    # https://stackoverflow.com/questions/50099151/python-how-to-set-id-of-button
                    widget.ids[item] = btn  # CORRECT WAY based on the above

                    # BINDING event with method - VERY IMPORTANT!
                    btn.bind(on_press=self.on_press_g_group)

                    # Adding buttons to the layout
                    widget.add_widget(btn)

    def on_press_g_group(self, instance):
        """Defines what happens when any g_group button is pressed"""

        settings.on_staion_button_press_flag = True
        # Updating app variable - VERY IMPORTANT!

        app.selected_g_group = instance.text

        # Storing selected g_group key
        fpf.store_requested_station_or_group(settings, app.selected_g_group)

        app.requested_stations = fpf.extract_stations_from_g_group(app.selected_g_group)

        print(app.selected_g_group, app.requested_stations, 'main.kkkkk')

        self.generate_TAFs_at_page2_and_show()

        # Adding markers to the map
        # self.add_current_g_group_markers(self.requested_stations)
        self.mapControls.add_current_g_group_markers(self)


    def generate_TAFs_at_page2_and_show(self):
        # Updates decoded TAF on press
        self.update_TAFs(settings,
            self.requested_stations,
            self.value__start_slider,
            self.value__end_slider)

        # Running app function on button press
        # app.update_TAFs_display_labels()

        self.update_scroll_height()

        # Moves to the 2nd screen
        self.root.current = "second"
        self.root.transition.direction = "left"

        # Resets parameters - setting inital START and END times
        self.single_counter= 0
        self.period_counter = int(self.time_now.strftime("%H"))
        self.value__start_slider = self.time_now.strftime("%H")

        # If time now exeeds validity end time then we set the end period as the current time
        if int(self.time_now.strftime("%H")) > int(self.TAFs_validity__latest_end_txt):
            self.value__end_slider = self.time_now.strftime("%H")
        else:
            self.value__end_slider = self.TAFs_validity__latest_end_txt



    slider_variable_boolean = BooleanProperty(False)

    both_sliders_visible__slider_height= '60dp'
    slider_opacity__visible = '1'
    slider_height =StringProperty(both_sliders_visible__slider_height)
    slider_opacity = StringProperty(slider_opacity__visible)


    def change_font_size(self):
        """Changes the decoded TAF font"""



        f_size = str(str( 14+ self.font_counter* self.font_step) + 'dp')

        self.TAF_display_font_size = f_size
        print(self.TAF_display_font_size , 'main.font')
        self.font_counter += 1

        if self.font_counter ==4:
            self.font_counter=0

        self.update_TAFs(settings,
                         app.requested_stations,
                         app.value__start_slider,
                         app.value__end_slider)
        self.update_TAFs_display_labels()




    def load_single_TAF(self,widget):
        input_text= str(widget.text)

        # Opening TAF vs station database
        path = "Data_new/api__tafs_cleaned.json"

        with open(path, 'r') as f_obj:
            tafs_cleaned_dict = json.load(f_obj)

        # Checking if TAF in database
        if input_text.upper() in tafs_cleaned_dict['station_id']:
            self.requested_stations = [input_text] ### AAA in

            # STORING LAST REQUESTED AIRPORT
            fpf.store_requested_station_or_group(settings, self.requested_stations[0])  # AAA out  - convertis list into string

            # UPDATING TAFs DISPLAY
            self.generate_TAFs_at_page2_and_show()

            #Stores the lase SINGLE STATION selected

        else:

            if not len(input_text) ==4:
                widget.text = ''
                self.search_hint ='Has to be 4 letter/numbers'
            else:
                widget.text = ''
                self.search_hint= 'No TAF for such station'

    def next_nh(self, n):
        """Next n hours for PAGE2"""
        # 12h, 4h


        self.value__start_slider = str(int(self.time_now.strftime("%H"))+1)
        # + 1 to start counting from the next full hour

        self.value__end_slider = str(int(self.value__start_slider) + n)
        self.period_counter = int(self.time_now.strftime("%H"))


    def next_nh_PAGE1(self,n):
        #3h,6h,12h,
        settings.SINGLE_station_time_range = n
        self.color_on__t_range= str(settings.SINGLE_station_time_range)

        # Updating slider values
        self.value__start_slider = str(int(self.time_now.strftime("%H"))+1)
        # + 1 to start counting from the next full hour

        self.value__end_slider = str(int(self.value__start_slider) + n)

        self.refresh_station_buttons(True)

    ### SETTINGS BINDING
    def single_station_color_on(self, widget):
        if widget.state == "normal":
            settings.min_num_of_char = 5
        else:
            #DOWN
            settings.min_num_of_char = 2
        # Last requested stations NEED TO BE CLEARED
        id__Last_requests = app.root.ids.id__Page1.ids.id__Last_requests__scroll.ids.id__Last_requests  #### DIRECT PATH!!!!!
        id__Last_requests.clear_widgets()
        self.refresh_station_buttons(False)

    def reset_time_all_day(self):
        self.value__start_slider = self.time_now.strftime("%H")
        self.value__end_slider = self.TAFs_validity__latest_end_txt

    def toggle_gap_active(self,widget):
        if widget.state == "down":
            settings.gap_active = True
        else:
            #OFF - normal
            settings.gap_active = False

    def testing_tafs_toggle(self, widget):

        if widget.state == "normal":
            settings.testing_decoder = False
        else:
            # DOWN
            settings.testing_decoder = True

    def time_slider_TAFs_update_real_time__toggle(self, widget):
        if widget.state == "normal":
            settings.update_TAFs_in_real_time_when_slider_moved = False
        else:
            # DOWN
            settings.update_TAFs_in_real_time_when_slider_moved = True

    def oneline_threats__toggle(self, widget):
        if widget.state == "normal":
            settings.print_in_one_line = True
            settings.print_in_multiple_lines = False

        else:
            # DOWN
            settings.print_in_one_line = False
            settings.print_in_multiple_lines = True

        # UPDATING DISPLAY OF TAFs
        self.update_TAFs(settings,
                            app.requested_stations,
                         app.value__start_slider,
                         app.value__end_slider)
        self.update_TAFs_display_labels()

    def show_threats__togle(self, widget):
        """
        Turns on display of THREATS for each station - COLOURED STATION name always remain
        :param widget: toggle button
        :return: None
        """
        if widget.state == "down":
            settings.show_threats = False

        else:
            # OFF - normal
            settings.show_threats = True


        # UPDATING DISPLAY OF TAFs
        self.update_TAFs(settings,
                         app.requested_stations,
                         app.value__start_slider,
                         app.value__end_slider)
        self.update_TAFs_display_labels()

    def show_winds__toggle(self, widget):
        if widget.state == "normal":
            settings.show_wind_profile = False
            settings.show_threats = False
        else:
            # DOWN
            settings.show_wind_profile = True
            # TREATS need to be active to show the WIND
            settings.show_threats = True

        # UPDATING DISPLAY OF TAFs
        self.update_TAFs(settings,
            app.requested_stations,
             app.value__start_slider,
             app.value__end_slider)
        self.update_TAFs_display_labels()



    def refresh_station_buttons(self, change_time_range):

        """VERY IMPORTANT FUNCTION -- updates all buttons in the PAGE1 when parameters changes
        INPUT: change_time_range - FALSE at all cases, TRUE only when new itme period buttons are pressed - this is to make change to new period without generating temporarly the GRAY buttons
        """

        window_manager = app.root
        id__TAF_groups_Stack = app.root.ids.id__Page1.ids.id__TAF_groups__scroll.ids.id__TAF_groups_Stack

        id__Last_requests = app.root.ids.id__Page1.ids.id__Last_requests__scroll.ids.id__Last_requests

        # REMOVES ALL BUTTONS
        id__Last_requests.clear_widgets()
        if not change_time_range: # Not called when changing time range on PAGE1 - prevents from GRAY buttons to appear temporarely
            id__TAF_groups_Stack.clear_widgets()

        # REBUILD ALL BUTTONS with new parameters
        if not change_time_range:
            self.create_g_group_buttons(id__TAF_groups_Stack)
        self.create_SINGLE_station_buttons(id__TAF_groups_Stack, change_time_range)

        self.create_last_requests_buttons(id__Last_requests, settings)


    def reloading_inprogress(self):
        self.reload_status = "#7b9fba"
        self.reload_button_msg ="Reloading"

    stationsList =[]
    METARs_list=[]
    selected_station_index=-1
    def select_station(self, args):
        self.selected_station_index= args

        ## UPDATING page 5 label dispalu - single TAF display
        for i in range(len(self.stationsList)):
            ## Searching for Station at propper index
            if i == int(app.selected_station_index):
                ## UPDATING page5 DISPLAY -
                app.station_name = self.stationsList[i].station_name__coloured

                # Replacing text by proper symbols
                self.stationsList[i].decoded_TAF = self.stationsList[i].decoded_TAF.replace("newlinee.Tdf", '\n')
                self.stationsList[i].decoded_TAF = self.stationsList[i].decoded_TAF.replace("space.Tdf", '')

                app.station_TAF = self.stationsList[i].decoded_TAF


                app.station_METAR = self.METARs_list[i]
                app.station_APPRs = self.stationsList[i].appr_data
        ## On station touch - go to page 5
        app.root.current = "fifth"
        app.root.transition.direction = "left"


        ## RESET scroll position at PAGE 5 (single TAF)
        page5_scroll = app.root.ids.id__Page5.ids.MyLabel__scroll
        page5_scroll.scroll_y = 1


    def next_station(self):
        if int(self.selected_station_index) < len(self.stationsList) - 1:
            self.selected_station_index= str(int(self.selected_station_index) + 1)

        self.select_station(self.selected_station_index)
    def prev_station(self):
        if int(self.selected_station_index) >0:
            self.selected_station_index= str(int(self.selected_station_index) - 1)

        self.select_station(self.selected_station_index)

    ### MAP page methods
    #


    #
    # def add_current_g_group_markers(self, widget):
    #     """Adds markers to the map for all stations in the current g_group"""
    #     # Getting mapView widget
    #     mapView_my = self.root.ids['map'].ids['id__MapView_my']
    #
    #     # Clearing map of the previous g_group markers
    #     for mkr in self.g_group_mapMarkers:
    #         mapView_my.remove_marker(mkr)
    #
    #     # This is pre-annotation syntax for type hinting
    #     stationObject: SingleStation
    #
    #     for stationObject in app.stationsList:
    #         # Adding marker to the map
    #         mkr = MapMarker(lat=stationObject.apt_coordinates[0],
    #                         lon=stationObject.apt_coordinates[1])
    #         mapView_my.add_marker(mkr)
    #
    #         # Adding marker to the list of markers - to be able to remove them later
    #         self.g_group_mapMarkers.append(mkr)

from TAF_decoder import SingleStation

TheTAFApp().run()  # RUNS THE KIVY!!



