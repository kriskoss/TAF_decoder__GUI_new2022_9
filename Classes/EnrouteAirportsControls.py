from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.app import App    # This imports App class from kivy.app

from Classes.Route import Route
from Classes.Airport import Airport
class EnrouteAirportsControls:
    """This class contain all functionality related to displaying Enroute Airports"""
    def __init__(self, mapControls, **kwargs):
        self.mapControls = mapControls
        self.current_route = Route()


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
        """updates current_route (Route object) to contain the route string from route_input__widget (CONFIRMED route)"""
        route_input__widget = self.get__route_input()
        self.current_route.updateRoute(route_input__widget.text)     # Converts input route string into Route object which is a list of validated icao codes
        route_str__corrected = self.current_route.get_corrected_route_string()
        route_input__widget.text = route_str__corrected


    def route_confirmed(self):
        print("ROUTE COFIRMED", "       main.py - def route_confirmed(self): AAAAAAAAAAA")
