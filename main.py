## General use modules
import json
import requests
import pprint
import datetime


from kivy.uix.label import Label
from kivy.uix.widget import Widget

import TAF_decoder__helper_functions as Td_helpers
## My modules
from kivy.core.window import Window

import final_program_functions as fpf
from settings import Settings
settings = Settings()
from dateutil.parser import parse  # check https://stackabuse.com/converting-strings-to-datetime-in-python/
        # module which automatically converts time string into the datetime format

from kivy.lang import Builder
Builder.load_file('page1.kv')
Builder.load_file('page2.kv')
Builder.load_file('page3.kv')
# Builder.load_file('TheTAF.kv')

## Kivy modules
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

class TAF_groups_Stack(StackLayout):

    def __init__(self, **kwargs):  # __init__ is the constructor, ** kwargs is required for internal working of KIVY
        super(TAF_groups_Stack, self).__init__(**kwargs)

        # Creates first set of g_group buttons
        app.create_g_group_buttons(self)
        app.create_SINGLE_station_buttons(self)

class Add_Group(BoxLayout):
    """ Methods used to Add and Edit new g_group"""

    # Adds new g-group in to the database
    new_group_str =StringProperty("")

    time_now = datetime.datetime.utcnow()

    terminal_answer=StringProperty(time_now.strftime("%H:%M")+'UTC +' + str(settings.SINGLE_station_time_range) + 'h for THR LEVEL' )

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
    ### GLOBAL VARIABLES


    requested_stations ='none'
    # Sets the initial value of the time sliders

    time_now =datetime.datetime.utcnow()
    value__start_slider = StringProperty(str(time_now.strftime("%H")))
    value__end_slider = StringProperty('48')


    # STRINGPROPERTY and BOOLEAN PROPERTY realtime update of the string!!
    start_ddhh = StringProperty('ccc')
    end_ddhh = StringProperty('dd')

    # Lable which display the decoded TAF
    label__stations_threat_levels = StringProperty('label__stations_threat_levels')
    label__decoded_TAFs = StringProperty('label__decoded_TAFs')

    font_size = StringProperty('12sp')
    search_input = StringProperty('')

    single_counter_txt = StringProperty('OFF')

    TAFs_validity__earliers_start_txt = StringProperty('7') # Initial sting inside has to be number
    TAFs_validity__latest_end_txt = StringProperty('12')    # Initial sting inside has to be number

    search_hint = StringProperty("Search")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        # YouTube reference:  https://stackoverflow.com/questions/73079260/kivy-how-to-access-global-variables-in-kv-file
        # Initializing global variables --- (__init__ above required!!)
        self.selected_g_group = None  # Just to avoid pycharm caution display

        # Renaming self to app to enable direct the Main App object in other classes
        global app
        app = self
                ### END of youtube reference
        self.g_groups_db = self.load_g_groups_db()
    def update_FontSize_slider_value(self,widget):
        self.fontSize_slider_value = f'{int(widget.value/2)}sp'
        self.update_scroll_height()

    def update_TAFs(self, stations_, start, end):
        print(stations_, start, end, 'main.update_Tafs')
        decoded_TAFs_data_list, combined_stations_threat_level \
            = fpf.analise_stations(settings, stations_,
                                   int(start), int(end))

        # self.label__stations_threat_levels = combined_stations_threat_level

        decoded_TAFs = []
        TAFs_validity_start_times =[]
        TAFs_validity_end_times =[]
        max_threat_level_at_airports =[]
        for decoded_TAF_dict in decoded_TAFs_data_list:
            station_name = decoded_TAF_dict["station_name"]
            decoded_TAFs.append(station_name)
            selected_time_info = decoded_TAF_dict["selected_time_info"]
            decoded_TAF = decoded_TAF_dict["decoded_TAF"]
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

        self.label__decoded_TAFs = combined_stations_threat_level + '\n-----------------------\n' +'\n\n'.join(decoded_TAFs) + "\n\n    -----------END -----------\n"

        # FINDING earliest TAF validity START hour and LATEST end HOUR
        print(min(TAFs_validity_start_times),max(TAFs_validity_end_times),'main.ssss')
        self.TAFs_validity__earliers_start_txt = str(min(TAFs_validity_start_times))
        self.TAFs_validity__latest_end_txt = str(max(TAFs_validity_end_times))

        return max_threat_level_at_airports

    def on_slider_value__start(self, widget):
        self.value__start_slider = str(int(widget.value))
        self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.value__start_slider, self.value__end_slider)

        if self.time_range>3:
            self.value__end_slider = str(int(self.value__start_slider) + self.time_range)
        print('main.suspect0', self.value__start_slider, self.value__end_slider)

        self.update_TAFs(
            self.requested_stations,
            self.value__start_slider,
            self.value__end_slider)

        # Just to make display of day:hh
        self.start_ddhh = Td_helpers.hours_to_ddhh(int(widget.value))

    def on_slider_value__end(self, widget):
        self.value__end_slider = str(int(widget.value))
        if self.time_range>3:
            self.value__end_slider = str(int(self.value__start_slider) + self.time_range)

        self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.value__start_slider, self.value__end_slider)
        print('main.suspect1',self.value__start_slider, self.value__end_slider)
        self.update_TAFs(
            self.requested_stations,
            self.value__start_slider,
            self.value__end_slider)

        # Just to make display of day:hh
        self.end_ddhh = Td_helpers.hours_to_ddhh(int(widget.value))

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

        # Decrase/increase selected period
        if direction == "increase":
            self.period_counter += self.time_range
        if direction == "decrease":
            self.period_counter -= self.time_range


        # Resets counter when the max value reached
        if self.period_counter > int(self.TAFs_validity__latest_end_txt) - self.time_range:
            self.period_counter = int(datetime.datetime.utcnow().strftime("%H"))
        if self.period_counter < int(datetime.datetime.utcnow().strftime("%H")):
            self.period_counter = int(self.TAFs_validity__latest_end_txt)
        # Updates BUTTON description
        self.value__start_slider = str(self.period_counter)
        self.value__end_slider = str(self.period_counter + self.time_range)

    def call_AIRPORTS_reload(self):
        fpf.download_airports_database()

    def load_g_groups_db(self):
        filename = 'Data/g_groups_apts_db.json'
        with open(filename) as f_obj:
            g_groups_db = json.load(f_obj)
        return g_groups_db

    """Methodes related to TOP BAR"""


    def call_TAFs_reload(self):
        fpf.download_taf_database(parse)

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
        self.update_TAFs(app.requested_stations,
            app.value__start_slider,
            app.value__end_slider)
        print(settings.print_type, settings.print_time_group, 'main')
        self.update_TAFs_display_labels()
        # self.label__decoded_TAFs = 'affafafa'

    def print_appr_info__toggle(self, widget):
        if widget.state == "normal":
            # OFF
            settings.print_appr_info = False
        else:
            # ON
            settings.print_appr_info = True
            # settings.print_time_group = True

        print('main.suspect3')
        self.update_TAFs(app.requested_stations,
            app.value__start_slider,
            app.value__end_slider)
        print(settings.print_type, settings.print_time_group, 'main')
        self.update_TAFs_display_labels()
    def update_search_input(self,widget):
        self.search_input = widget.text
        print(self.search_input)

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
    def create_SINGLE_station_buttons(self, widget):
        search_input = app.search_input

        # Opening TAF vs station database
        path = "Data_new/api__tafs_cleaned.json"
        with open(path, 'r') as f_obj:
            tafs_cleaned_dict = json.load(f_obj)
        stations_to_show=[]

        # Look for stations in the database only if search input 2-4 letters long
        if 1 < len(search_input) < 5:
            for station in tafs_cleaned_dict['station_id']:

                # Check if search input is in any station_id
                if search_input.upper() in station.upper():

                    # If search input in station_id, the store the station
                    stations_to_show.append(station)

        # Updating requested_stations so it is more efficient as UPDATE TAF runs 5x times
        app.requested_stations = stations_to_show

        #Minimum number of characters in search input to show THREAT LEVEL
        max_threat_level_at_airports=[]
        print(stations_to_show, 'main.stations_to_show')
        if len(search_input)>=settings.min_num_of_char:
            if len(stations_to_show)> 0:
                # Has to callit self so sliders_values use the same value ()
                app.requested_stations= app.requested_stations[:settings.max_num_of_colored]

                max_threat_level_at_airports = self.update_TAFs(app.requested_stations, int(self.value__start_slider), int(self.value__start_slider) + settings.SINGLE_station_time_range)
                print(max_threat_level_at_airports, 'main.EEEE')

        if len(stations_to_show) > 0:
            i=0
            for station in stations_to_show:
                b_colour = '#474747'    # GRAY-BLUE
                if i<len(max_threat_level_at_airports):
                    tl =max_threat_level_at_airports[i][1][0]
                    print(tl, 'hhhhhhhhhhh')
                    if tl =="severe":
                        b_colour= '#750437'  # MAGENTA
                    elif tl =="warning":
                        b_colour = '#967a09' # RED
                    elif tl == "caution":
                        b_colour = '#967a09' # YELLOW
                    elif tl=="green":
                        b_colour = '#0a6932' # GREEN
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


    def on_press_g_group(self, instance):
        """Defines what happens when any g_group button is being pressed"""
        # Updating app variable - VERY IMPORTANT!
        app.selected_g_group = instance.text
        app.requested_stations = fpf.extract_stations_from_g_group(app.selected_g_group)

        print(app.selected_g_group, app.requested_stations)

        self.generate_TAFs_at_page2_and_show()


    def generate_TAFs_at_page2_and_show(self):
        # Updates decoded TAF on press
        self.update_TAFs(
            self.requested_stations,
            self.value__start_slider,
            self.value__end_slider)

        # Running app function on button press
        # app.update_TAFs_display_labels()

        self.update_scroll_height()

        # Moves to the 2nd screen
        self.root.current = "second"
        self.root.transition.direction = "left"

        # Resets parameters
        self.time_range = 3  # Has to be 3 to show full period  - otherwise it is limited to time range
        # app.single_counter= 0
        app.period_counter = int(self.time_now.strftime("%H"))
        self.value__start_slider = self.time_now.strftime("%H")
        self.value__end_slider = self.TAFs_validity__latest_end_txt

    time_range= 5
    time_range_txt = StringProperty(time_range) # Enable realtime update of the string!!
    def single_slider(self, widget):
        self.time_range += 1

        if self.time_range > 6:
            self.time_range=3
            self.single_counter_txt = "OFF"
        elif self.time_range > 3:

            self.value__end_slider= str(int(self.value__start_slider) + self.time_range)
            self.single_counter_txt = str(self.time_range)

        # elif self.single_counter == 3:
        #     self.single_counter_txt = "OFF"
        self.time_range_txt = str(self.time_range)


    font_counter = 0

    def change_font_size(self):
        """Changes the decoded TAF font"""
        if self.font_counter ==0:
            f_size = "10sp"
        elif self.font_counter ==1:
            f_size = "15sp"
        else:
            f_size = "20sp"
        self.font_size = f_size
        if self.font_counter <2:
            self.font_counter+=1
        else:
            self.font_counter=0

    slider_variable_boolean = BooleanProperty(False)
    def slider_disable(self):
        # Disables the END TIME slider
        if self.time_range == 3:
            self.slider_variable_boolean = False
        else:
            self.slider_variable_boolean =True


    hide_slider_value = StringProperty('1')
    hide_switch=True
    slider_height =StringProperty('40dp')
    def hide_slider(self):
        # Hides END TIME slider when TIME RANGE off
        if  self.time_range == 3:
            self.hide_switch = False

            # INCREASES slider container HEIGHT
            self.slider_height = '40dp'
        else:
            self.hide_switch =True

            # REDUCES slider container HEIGHT
            self.slider_height = '15dp'
        if self.hide_switch:
            self.hide_slider_value = "0"
        else:
            self.hide_slider_value ='1'


    def load_single_TAF(self,widget):
        input_text= str(widget.text)

        # Opening TAF vs station database
        path = "Data_new/api__tafs_cleaned.json"
        with open(path, 'r') as f_obj:
            tafs_cleaned_dict = json.load(f_obj)
        # Checking if TAF in database
        if input_text.upper() in tafs_cleaned_dict['station_id']:
            self.requested_stations = [input_text]
            self.generate_TAFs_at_page2_and_show()
        else:

            if not len(input_text) ==4:
                print('main.saff')
                widget.text = ''
                self.search_hint ='Has to be 4 letter/numbers'
            else:
                widget.text = ''
                self.search_hint= 'No TAF for such station'

    def next_12h(self,widget):
        self.value__start_slider = str(self.time_now.strftime("%H"))
        self.value__end_slider = str(int(self.value__start_slider) + 12)

    ### SETTINGS BINDING
    def single_station_color_on(self, widget):
        if widget.state == "normal":
            settings.min_num_of_char = 5
        else:
            settings.min_num_of_char = 2
    def reset_time_all_day(self):
        app.period_counter = int(self.time_now.strftime("%H"))
        self.value__start_slider = self.time_now.strftime("%H")
        self.value__end_slider = self.TAFs_validity__latest_end_txt


TheTAFApp().run()  # RUNS THE KIVY!!
