## General use modules
import json
import pprint

## My modules
from kivy.core.window import Window

import final_program_functions as fpf

## Kivy modules
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

class Top_Bar(BoxLayout):
    """Methodes related to TOP BAR"""
    t_once_switch = False
    t_always_switch = False

    def call_TAFs_reload(self):
        fpf.download_taf_database()

    def call_AIRPORTS_reload(self):
        fpf.download_airports_database()

    def print_tt(self):
        print("Testing Add time variable:" + str(self.t_always_switch))

    def show_T_time_toggle(self,widget):
        # Toggle to show TIME range of any wx at or above CAUTION level
        init_label = "Add Time (t): "
        if widget.state == "normal":
            #OFF
            widget.text = init_label +  "OFF"
                # widget is inserted as an argument so we can use it
            self.t_always_switch=False
        else:
            #ON
            widget.text = init_label +  "ON"
            self.t_always_switch = True
        print("Add Time (t): "+ str(self.t_always_switch))

# StringProperty ONLY necessary if variable is to be used in KV file
    # selected_g_group = StringProperty('initial: selected_g_group')
    # slider_value_txt = StringProperty('initial: slider_value_txt')

class TAF_groups_Stack(StackLayout):

    def __init__(self, **kwargs):  # __init__ is the constructor, ** kwargs is required for internal working of KIVY
        super(TAF_groups_Stack, self).__init__(**kwargs)
        self.create_g_group_buttons()

    def create_g_group_buttons(self):
        # Loading g_groups data from .json
        filename = 'Data/g_groups_apts_db.json'
        with open(filename) as f_obj:
            g_groups_db = json.load(f_obj)

        # Creating g_groups buttons
        for g_group_key, v in g_groups_db.items():

            btn = Button(
                text=f'{g_group_key[1:]}:     {" ".join(v).upper()}',
                size_hint=(1, None),
                height=dp(40),
                font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
            )

            # ADDING buttons IDs dictionary
            # https://stackoverflow.com/questions/50099151/python-how-to-set-id-of-button
            self.ids[g_group_key] = btn  # CORRECT WAY based on the above

            # BINDING event with method - VERY IMPORTANT!
            btn.bind(on_press=self.on_press_g_group)

            # Adding buttons to the layout
            self.add_widget(btn)

    def on_press_g_group(self, instance):
        # Updating app variable - VERY IMPORTANT!
        app.selected_g_group= "g"+instance.text[:4].upper()
        app.requested_stations = fpf.extract_stations_from_g_group(app.selected_g_group)

        print(app.selected_g_group, app.requested_stations)

        # Updates decoded TAF on press
        app.update_TAFs(
            app.requested_stations,
            app.slider_value_txt__start,
            app.slider_value_txt__end)

        #

        # TESTING - changing the colour of g_group buttin once pressed
        instance.background_color = "#FF00FF" # changes colour of the selected g_group button

        # Running app function on button press
        app.update_TAFs_display_labels()

        app.update_scroll_height()

        # Moves to the 2nd screen
        app.root.current = "second"
        app.root.transition.direction = "left"

        # Resetting sliders
        app.value__start_slider = "0"
        app.value__end_slider = "48"


class Add_Group(BoxLayout):
    """ Methods used to Add and Edit new g_group"""

    # Adds new g-group in to the database
    new_group_str =StringProperty("")
    terminal_answer=StringProperty("TERMINAL")

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
    time_start_str = "10"  # has to be string as it is StringProperty is being updated not the variable itself
    time_end_str = "38"

    requested_stations ='none'
    # Sets the initial value of the time sliders
    value__start_slider = StringProperty(time_start_str)
    value__end_slider = StringProperty(time_end_str)

    # Read value o the slider
    slider_value_txt__start = StringProperty(time_start_str)
    slider_value_txt__end = StringProperty(time_end_str)

    # Lable which display the decoded TAF
    label__stations_threat_levels = StringProperty('label__stations_threat_levels')
    label__decoded_TAFs = StringProperty('label__decoded_TAFs')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        # YouTube reference:  https://stackoverflow.com/questions/73079260/kivy-how-to-access-global-variables-in-kv-file
        # Initializing global variables --- (__init__ above required!!)
        self.selected_g_group = None  # Just to avoid pycharm caution display

        # Renaming self to app to enable direct the Main App object in other classes
        global app
        app = self
                ### END of youtube reference

    def update_TAFs(self, stations, start, end):
        print(stations, start, end)
        decoded_TAFs_data_list, combined_stations_threat_level = fpf.analise_stations(
            app.requested_stations,
            int(start),
            int(end))

        # self.label__stations_threat_levels = combined_stations_threat_level

        decoded_TAFs = []
        for decoded_TAF_dict in decoded_TAFs_data_list:
            station_name = decoded_TAF_dict["station_name"]
            decoded_TAFs.append(station_name)
            selected_time_info = decoded_TAF_dict["selected_time_info"]
            decoded_TAF = decoded_TAF_dict["decoded_TAF"]
            decoded_TAFs.append(decoded_TAF)
            runways_length = decoded_TAF_dict["runways_length"]
            station_threats = decoded_TAF_dict["station_threats"]
            appr_data = decoded_TAF_dict["appr_data"]
        # self.label__decoded_TAFs = '\n'.join(decoded_TAFs)
        self.label__decoded_TAFs = combined_stations_threat_level + '\n-----------------------\n' +'\n\n'.join(decoded_TAFs) + "\n\n    -----------END -----------\n"

            # print(station_name)
            # print(selected_time_info)
        #     print(decoded_TAF)
        #     print(station_threats, runways_length)
        #     print(appr_data)
        #
        # print(combined_stations_threat_level)




    def on_slider_value__start(self, widget):
        print("Slider value START:" + str(int(widget.value)))
        self.slider_value_txt__start = str(int(widget.value))
        self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.slider_value_txt__start, self.slider_value_txt__end)

        self.update_TAFs(
            self.requested_stations,
            self.slider_value_txt__start,
            self.slider_value_txt__end)

    def on_slider_value__end(self, widget):
        print("Slider value END:" + str(int(widget.value)))
        self.slider_value_txt__end = str(int(widget.value))
        self.label__stations_threat_levels = self.combine_data(self.selected_g_group, self.slider_value_txt__start, self.slider_value_txt__end)

        self.update_TAFs(
            self.requested_stations,
            self.slider_value_txt__start,
            self.slider_value_txt__end)

    def update_scroll_height(self):

        MyLabel = app.root.ids.id__Page2.ids.MyLabel

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
        self.TAF_decoder__input_data = self.combine_data(self.selected_g_group,self.slider_value_txt__start,self.slider_value_txt__end)
        self.label__stations_threat_levels  = self.TAF_decoder__input_data


    def combine_data(self, data1, data2, data3):
        """Just combines data into one element - to avoid repeating the code"""

        return str([data1, data2, data3])

    def day1__set_time_values(self):
        self.value__start_slider = "0"
        self.value__end_slider = "24"

    def day2__set_time_values(self):

        self.value__start_slider = "24"
        self.value__end_slider = "48"





TheTAFApp().run()  # RUNS THE KIVY!!
