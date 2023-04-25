from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.app import App    # This imports App class from kivy.app

from Route import Route
from Airport import Airport
class EnrouteAirportsControls:
    """This class contain all functionality related to displaying Enroute Airports"""
    def __init__(self, mapControls, **kwargs):
        self.mapControls = mapControls


    def getEnr_apts_stack__widget(self):
        app = App.get_running_app() # This gets the running app - in this case it is the main.py

        enr_apts_stack__widget = app.root.ids['id__enr_apts'].ids['id__EnrApts__scroll'].ids['Enr_apts_stack']
        return enr_apts_stack__widget

    def removeAllButtons(self):
        widget = self.getEnr_apts_stack__widget()
        widget.clear_widgets()
    def createEnrAptButton(self, apt):
        # Add Enr apt button to at page_enr_apts.kv Enr_apts_stack
        widget = self.getEnr_apts_stack__widget()

        btn = Button(
            text=apt.apt_code,
            size_hint=(1, None),
            height=dp(30),
            # width=dp(100),
            font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
            font_size='20dp',
            background_color="red",
            # background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
        )

        widget.add_widget(btn)

    def add_enr_btns(self, widget):
        enroute_airports = self.mapControls.getEnrouteAirports()
        apt: Airport
        for apt in enroute_airports:
            print(apt.apt_code, "main.py EnrApts(BoxLayout): apt.apt_code OOOOOOOOOOOO")
            btn = Button(
                text=apt.apt_code,
                size_hint=(1, None),
                height=dp(30),
                # width=dp(100),
                font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                font_size='20dp',
                background_color="red",
                # background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
            )

            widget.add_widget(btn)

        for i in range(3):
            btn = Button(
                text=f'Enr Apt {i}',
                size_hint=(1, None),
                height=dp(30),
                # width=dp(100),
                font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
                font_size='20dp',
                background_color="red",
                # background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
            )

            widget.add_widget(btn)




        # btn = Button(
        #     text="Test Button",
        #     size_hint=(1, None),
        #     height=dp(40),
        #     # width=dp(100),
        #     font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
        #     font_size='20dp',
        #     background_color="red",
        #     # background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
        # )

        # widget.add_widget(btn)

        # self.mapControls = _mapControls
        # Getting mapView widget

    def get__route_input(self):
        """Returns ROUTE INPUT widget"""
        app = App.get_running_app()
        route_input__widget = app.root.ids['id__enr_apts'].ids["id__route_input"]

        return route_input__widget

    def updateRoute(self):
        route_input__widget = self.get__route_input()
        route = Route(route_input__widget.text)     # Converts input route string into Route object which is a list of validated icao codes
        route_str__corrected = route.get_corrected_route_string()
        route_input__widget.text = route_str__corrected


    def route_confirmed(self):
        print("ROUTE COFIRMED", "       main.py - def route_confirmed(self): AAAAAAAAAAA")

    #     mapView_my = self.app.root.ids['map'].ids['id__MapView_my']
    # def create_enr_apts_buttons(self):
    #     apt: Airport
    #     for apt in self.mapControls:
    #
    #         # SINGLE STATION
    #         btn = Button(
    #             text=item.upper(),
    #             size_hint=(1, None),
    #             height=dp(40),
    #             # width=dp(100),
    #             font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
    #             font_size='20dp',
    #             background_color=last_req_single_station__b_colour,
    #             background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
    #         )
    #
    #         widget.ids[item] = btn  # CORRECT WAY based on the above
    #
    #         # BINDING event with method - VERY IMPORTANT!
    #         btn.bind(on_press=self.load_single_TAF)
    #
    #         # Adding buttons to the layout
    #         widget.add_widget(btn)
    #
    #     else:
    #         # g_group
    #         btn = Button(
    #             text=f'{item[0].lower() + item[1:].upper()}',
    #             size_hint=(1, None),
    #             height=dp(40),
    #             font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
    #             font_size='20dp',
    #             background_color="#7ca4e6"
    #         )
    #
    #         # ADDING buttons IDs dictionary
    #         # https://stackoverflow.com/questions/50099151/python-how-to-set-id-of-button
    #         widget.ids[item] = btn  # CORRECT WAY based on the above
    #
    #         # BINDING event with method - VERY IMPORTANT!
    #         btn.bind(on_press=self.on_press_g_group)
    #
    #         # Adding buttons to the layout
    #         widget.add_widget(btn)
    # def create_last_requests_buttons(self,widget,settings):
    #
    #
    #
    #                 ### Colours the LAST REQUESTED AIRPORTS buttons
    #                 # COLOR_ON
    #                 if settings.min_num_of_char != 5:
    #                     last_req_single_station__b_colour = self.change_colour_depending_on_threat_level(single_station__max_threat_level)
    #                 # COLOR OFF
    #                 else:
    #                     last_req_single_station__b_colour ="#312f42"
    #
    #
    #                 # SINGLE STATION
    #                 btn = Button(
    #                     text=item.upper(),
    #                     size_hint=(1, None),
    #                     height=dp(40),
    #                     # width=dp(100),
    #                     font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
    #                     font_size='20dp',
    #                     background_color=last_req_single_station__b_colour,
    #                     background_normal = ''  # MODIIES HOW COLOR ARE BEING DISPLAYED
    #                 )
    #
    #                 widget.ids[item] = btn  # CORRECT WAY based on the above
    #
    #                 # BINDING event with method - VERY IMPORTANT!
    #                 btn.bind(on_press=self.load_single_TAF)
    #
    #                 # Adding buttons to the layout
    #                 widget.add_widget(btn)
    #
    #             else:
    #                 # g_group
    #                 btn = Button(
    #                     text=f'{item[0].lower() + item[1:].upper()}',
    #                     size_hint=(1, None),
    #                     height=dp(40),
    #                     font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
    #                     font_size='20dp',
    #                     background_color = "#7ca4e6"
    #                 )
    #
    #                 # ADDING buttons IDs dictionary
    #                 # https://stackoverflow.com/questions/50099151/python-how-to-set-id-of-button
    #                 widget.ids[item] = btn  # CORRECT WAY based on the above
    #
    #                 # BINDING event with method - VERY IMPORTANT!
    #                 btn.bind(on_press=self.on_press_g_group)
    #
    #                 # Adding buttons to the layout
    #                 widget.add_widget(btn)
    #
