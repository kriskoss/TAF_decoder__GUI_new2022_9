import json
import final_program_functions as fpf
import pprint


##Kivy
from kivy.app import App

from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout




class Box_Top(BoxLayout):
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

class Main_Box(BoxLayout):
    pass

class TAF_groups_Stack(StackLayout):
    selected_g_group = StringProperty('')
    def __init__(self, **kwargs):  # __init__ is the constructor, ** kwargs is required for internal working of KIVY
        super(TAF_groups_Stack, self).__init__(**kwargs)

        # Loading g_groups data from .json
        filename = 'Data/g_groups_apts_db.json'
        with open(filename) as f_obj:
            g_groups_db = json.load(f_obj)

        # Creating g_groups buttons

        for k,v in g_groups_db.items():
            print(k)

            b = Button(
                text=f'{k[1:]}:     {" ".join(v).upper()}',
                size_hint=(1, None),
                height=dp(40),
                font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
            )
            self.ids[k] = b
            b.bind(on_press=self.on_press_g_group)

            print(self.ids)
                ## https://stackoverflow.com/questions/50099151/python-how-to-set-id-of-button
            self.add_widget(b)

    def on_press_g_group(self, instance):
        # PRINTS pressed g_group !!!
        self.selected_g_group= "g"+instance.text[:4].upper()
        print(self.selected_g_group)

        # pprint.pprint(self.ids) # Pritnst all ids in the class

        instance.background_color = "#FF00FF" # changes colour of the selected g_group button

class StackLayoutExample(StackLayout):
    pass

class Add_Group(BoxLayout):
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
            self.terminal_answer = "Try format: XXXX XXXX XXXX etc."
class TheTAFApp(App):
    pass

TheTAFApp().run()  # RUNS THE KIVY!!
