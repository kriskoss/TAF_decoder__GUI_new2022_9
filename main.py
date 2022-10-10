## General use modules
import json
import pprint

## My modules
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
            print(g_group_key)

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
        print(app.selected_g_group)

        # TESTING - changing the colour of g_group buttin once pressed
        instance.background_color = "#FF00FF" # changes colour of the selected g_group button

        # Running app function on button press
        app.update_TAFs_display_labels()

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

    # Sets the initial value of the time sliders
    value__start_slider = StringProperty(time_start_str)
    value__end_slider = StringProperty(time_end_str)

    # Read value o the slider
    slider_value_txt__start = StringProperty(time_start_str)
    slider_value_txt__end = StringProperty(time_end_str)

    # Lable which display the decoded TAF
    label__taf_display = StringProperty('label__taf_display')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        # YouTube reference:  https://stackoverflow.com/questions/73079260/kivy-how-to-access-global-variables-in-kv-file
        # Initializing global variables --- (__init__ above required!!)
        self.selected_g_group = None  # Just to avoid pycharm caution display

        # Renaming self to app to enable direct the Main App object in other classes
        global app
        app = self
                ### END of youtube reference

    def on_slider_value__start(self, widget):
        print("Slider value START:" + str(int(widget.value)))
        self.slider_value_txt__start = str(int(widget.value))
        self.TAF_decoder__input_data = str([self.selected_g_group, "sss", self.slider_value_txt__start, self.slider_value_txt__end])
        self.label__taf_display = self.combine_data(self.selected_g_group,self.slider_value_txt__start,self.slider_value_txt__end)

    def on_slider_value__end(self, widget):
        print("Slider value END:" + str(int(widget.value)))
        self.slider_value_txt__end = str(int(widget.value))
        self.label__taf_display = self.combine_data(self.selected_g_group,self.slider_value_txt__start,self.slider_value_txt__end)

    def update_TAFs_display_labels(self):
        """ Labels are updated on function activation - used to update TAF display (VERY IMPORTANT!!!)"""
        # https://www.youtube.com/watch?v=TEpHeuH7wNw&list=WL&index=3

        # Getting elements (using IDs)
        # label__test = app.root.ids.id__Page1.ids.label__test
        # label__taf_display = app.root.ids.id__Page2.ids.lebel__taf_display


        # Updating elements
        self.TAF_decoder__input_data = self.combine_data(self.selected_g_group,self.slider_value_txt__start,self.slider_value_txt__end)
        self.label__taf_display  = self.TAF_decoder__input_data

    # def combine_data(self, data1, data2, data3):
    #     """Just combines data into one element - to avoid repeating the code"""
    #
    #     return str([data1,data2, data3])

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
