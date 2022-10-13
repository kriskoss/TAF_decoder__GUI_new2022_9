## General use modules
import json
import requests
import pprint

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


class Add_Group(BoxLayout):
    """ Methods used to Add and Edit new g_group"""

    # Adds new g-group in to the database
    new_group_str =StringProperty("")
    terminal_answer=StringProperty("")

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
    value__start_slider = StringProperty('131')
    value__end_slider = StringProperty('132')


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

    def update_TAFs(self, stations, start, end):
        print(stations, start, end, 'update_Tafs.main')
        decoded_TAFs_data_list, combined_stations_threat_level \
            = fpf.analise_stations(settings, app.requested_stations,
                                   int(start), int(end))

        # self.label__stations_threat_levels = combined_stations_threat_level

        decoded_TAFs = []
        TAFs_validity_start_times =[]
        TAFs_validity_end_times =[]

        for decoded_TAF_dict in decoded_TAFs_data_list:
            station_name = decoded_TAF_dict["station_name"]
            decoded_TAFs.append(station_name)
            selected_time_info = decoded_TAF_dict["selected_time_info"]
            decoded_TAF = decoded_TAF_dict["decoded_TAF"]
            decoded_TAFs.append(decoded_TAF)  ## APPEND - VERY IMPORTATN!!! - here it is being decided what is being printed out
            runways_length = decoded_TAF_dict["runways_length"]
            station_threats = decoded_TAF_dict["station_threats"]
            appr_data = decoded_TAF_dict["appr_data"]


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


    def on_slider_value__start(self, widget):
        self.value__start_slider = str(int(widget.value))
        self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.value__start_slider, self.value__end_slider)

        if self.time_range>3:
            self.value__end_slider = str(int(self.value__start_slider) + self.time_range)

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



    period_counter= 0
    def update_range(self,direction):
        """ Changes the value of the period that wil be selected at each BUTTON click"""

        # Decrase/increase selected period
        if direction == "increase":
            self.period_counter += self.time_range
        if direction == "decrease":
            self.period_counter -= self.time_range


        # Resets counter when the max value reached
        if self.period_counter > int(self.TAFs_validity__latest_end_txt) - self.time_range:
            self.period_counter = int(self.TAFs_validity__earliers_start_txt)
        if self.period_counter < 0:
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

    def on_press_g_group(self, instance):
        """Defines what happens when any g_group button is being pressed"""
        # Updating app variable - VERY IMPORTANT!
        app.selected_g_group = instance.text
        app.requested_stations = fpf.extract_stations_from_g_group(app.selected_g_group)

        print(app.selected_g_group, app.requested_stations)

        # Updates decoded TAF on press
        app.update_TAFs(
            app.requested_stations,
            app.value__start_slider,
            app.value__end_slider)

        #

        # TESTING - changing the colour of g_group buttin once pressed
        instance.background_color = "#FF00FF"  # changes colour of the selected g_group button

        # Running app function on button press
        # app.update_TAFs_display_labels()

        app.update_scroll_height()

        # Moves to the 2nd screen
        app.root.current = "second"
        app.root.transition.direction = "left"

        # Resets parameters
        app.time_range = 3 # Has to be 3 to show full period  - otherwise it is limited to time range
        # app.single_counter= 0
        # app.period_counter = 0
        app.value__start_slider = app.TAFs_validity__earliers_start_txt
        app.value__end_slider = app.TAFs_validity__latest_end_txt

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
    slider_height =StringProperty('30dp')
    def hide_slider(self):
        # Hides END TIME slider when TIME RANGE off
        if  self.time_range == 3:
            self.hide_switch = False

            # INCREASES slider container HEIGHT
            self.slider_height = '30dp'
        else:
            self.hide_switch =True

            # REDUCES slider container HEIGHT
            self.slider_height = '15dp'
        if self.hide_switch:
            self.hide_slider_value = "0"
        else:
            self.hide_slider_value ='1'

TheTAFApp().run()  # RUNS THE KIVY!!
