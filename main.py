import json


from kivy.app import App

from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

import final_program_functions as fpf




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

            self.add_widget(b)


            # self.add_widget(l)


class StackLayoutExample(StackLayout):
    pass
class TheTAFApp(App):
    pass

TheTAFApp().run()  # RUNS THE KIVY!!
