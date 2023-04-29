from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.app import App    # This imports App class from kivy.app

import final_program_functions as fpf
from Classes.Route import Route
from Classes.Airport import Airport
from Classes.settings import Settings
from TAF_decoder import TAF_decoder_function
import threading
import collections

# from main import TheTAFApp # just for syntax
settings = Settings()
class EnrouteAirportsControls:
    """This class contain all functionality related to displaying Enroute Airports"""
    def __init__(self, mapControls, **kwargs):

        self.mapControls = mapControls
        self.current_route = Route()
        self.analyzed_enr_apts__ready_for_btn_update__QUEUE = collections.deque()
        self.enr_apts_invalid_stations =[]

        self.ready_for_enr_apts_btns_change_of_color = False
        self.enr_apt__btn__identifier = "btnID:"
        self.rout_input__widget__STATE = None
        self.colour_change_finished = False
        self.creating_enr_apts_buttons_finished = False

    def create_enr_btns_and_mapMarkers(self, app):
        """This function creates the buttons for the Enroute Apts page and the map markers for the map"""

        if (self.mapControls.ready_for_enroute_markers and app.find_thread("Add_enroute_markers__THREAD")
                or self.creating_enr_apts_buttons_finished):  # This line enables LAST PASS !!
            queue_enr = self.mapControls.enr_apts_to_be_added__queue

            while len(queue_enr) > 0:
                apt = self.mapControls.enr_apts_to_be_added__queue.popleft()

                self.mapControls.addMarker(apt)

                # CREATE Enroute Airport Button on the Enroute Apts Page
                self.createEnrAptButton(apt)
                self.get_EnrApt_messageBox__widget().text = f'FINDING ENROUTE APTS...'
                self.creating_enr_apts_buttons_finished = True

        # Clearing ENROUTE APTS MESSAGE BOX
        if self.creating_enr_apts_buttons_finished and not self.mapControls.ready_for_enroute_markers:
            self.creating_enr_apts_buttons_finished = False
            self.get_EnrApt_messageBox__widget().text = ""

    def update_btns_for_threat_level(self,app):
        """This function updates the buttons for the Enroute Apts page with the threat level"""

        # UPDATING ENROUTE APTS BUTTONS COLOR
        if (self.ready_for_enr_apts_btns_change_of_color and app.find_thread("Enr_apts__TAF_decoding__THREAD")) or app.enrAptsCtrls.colour_change_finished == True:

            enr_apts__queue = self.analyzed_enr_apts__ready_for_btn_update__QUEUE
            enr_apts_stack__widget = app.enrAptsCtrls.getEnr_apts_stack__widget()

            self.get_EnrApt_messageBox__widget().text = f'LOADING THREAT LEVELS....'
            while len(enr_apts__queue) > 0:
                apt = enr_apts__queue.popleft()
                self.changeEnrAptButtonColor(apt, enr_apts_stack__widget)

            self.colour_change_finished = True  # This enables a LAST PASS

        # CLEARES ENROUTE APTS MESSAGE BOX once the colour change is finished
        if self.colour_change_finished and not self.ready_for_enr_apts_btns_change_of_color:
            self.colour_change_finished = False
            self.get_EnrApt_messageBox__widget().text = ""

    def getEnr_apts_stack__widget(self):
        app = App.get_running_app() # This gets the running app - in this case it is the main.py

        return app.root.ids['id__enr_apts'].ids['id__EnrApts__scroll'].ids['Enr_apts_stack']


    def get_EnrApt_messageBox__widget(self):

        app = App.get_running_app()  # This gets the running app - in this case it is the main.py

        return app.root.ids['id__enr_apts'].ids["messageBox"]

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
            background_color="lightgray",
            # background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
        )
        widget.ids[self.enr_apt__btn__identifier + apt.apt_code] = btn  # CORRECT WAY based on the above
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

    def next_nh__enr_apts_page(self,n):
        #3h,6h,12h,
        if not self.ready_for_enr_apts_btns_change_of_color:
            app = App.get_running_app()

            settings.SINGLE_station_time_range = n
            app.color_on__t_range= str(settings.SINGLE_station_time_range)

            # Updating slider values
            app.value__start_slider = str(int(app.time_now.strftime("%H"))+1) # + 1 to start counting from the next full hour
            app.value__end_slider = str(int(app.value__start_slider) + n)
            print(app.value__start_slider, app.value__end_slider, "app.value__start_slider, app.value__end_slider ENC.py  MMMMMMMMMM")

            self.refresh_enroute_apts_buttons(app)

    def refresh_enroute_apts_buttons(self, app):
        enr_apts_stack__widget =self.getEnr_apts_stack__widget()
        # self.recreate_enr_btns_with_threat_colour(app,enr_apts_stack__widget)

        self.ready_for_enr_apts_btns_change_of_color = True
        self.rout_input__widget__STATE = self.get__route_input()
        t = threading.Thread(name="Enr_apts__TAF_decoding__THREAD", target=self.recreate_enr_btns_with_threat_colour, args =[app,enr_apts_stack__widget])
        t.start()



    def recreate_enr_btns_with_threat_colour(self,app,widget):
        apt: Airport
        enr_apts_obj: list[Airport]

        enr_apts_objs  = app.mapControls.apts_enroute # List of Airport instances

        # Extracting apt_codes from Airport objects
        enroute_apts__apt_codes=[]
        TAF_num = 0
        for apt in enr_apts_objs:
            enroute_apts__apt_codes.append(apt.apt_code)
            self.analyze_enr_apt(app, apt, TAF_num)
            self.analyzed_enr_apts__ready_for_btn_update__QUEUE.append(apt)
            print(apt.apt_code, " ANALYZED EAC.py")
            TAF_num+=1

        self.ready_for_enr_apts_btns_change_of_color = False # Thread completed its job.
            # thr_name = "Enr_apts__decodingTAFs:" + apt.apt_code
            # t = threading.Thread(name=thr_name, target=self.analyze_enr_apt, args =[app])
            # t.start()

        # t1 = threading.Thread(name="Preparing_MaxThreatLevels_THREAD",target=self.get_max_threat_level_for_selected_stations, args =[app])
        # t1.start()

    def analyze_enr_apt(self,app, apt:Airport, TAF_num):
        # app: TheTAFApp
        apt.METAR_raw = fpf.load_single_METAR(apt.apt_code)
        return_data = fpf.get_single_stations_TAF(settings, apt.apt_code)
        if type(return_data)==list:
            print(apt.apt_code, " -- INVALID station -  KKKKK ENC.py - same call as in: fpf.get_single_stations_TAF() above ")
            return [apt.apt_code, "error"]

        else:
            apt.TAF__raw = return_data


            # DECODING TAF for the selected station
            decoded_TAF_dict, stationObject = TAF_decoder_function(settings, apt.TAF__raw, TAF_num, int(app.value__start_slider), int(app.value__end_slider))

            max_thrts_at_apt = app.get_max_threat_level_for_selected_airports(settings, [apt.apt_code], int(app.value__start_slider),
                                                                                 int(app.value__end_slider))

            apt.max_thr_lvl_in_sel_period = max_thrts_at_apt[0][1][0]

            apt.combined_station_data = fpf.combine_data(settings,
                                                        decoded_TAF_dict["station_threats"],
                                                        decoded_TAF_dict["wind_profile"],
                                                        decoded_TAF_dict["runways_length"],
                                                        decoded_TAF_dict["appr_data"])

            return apt.apt_code,apt.max_thr_lvl_in_sel_period

    def changeEnrAptButtonColor(self,apt, widget):
        apt: Airport

        btn =  widget.ids[self.enr_apt__btn__identifier + apt.apt_code]

        if apt.max_thr_lvl_in_sel_period == "green":
            btn.background_color = "green"
        elif apt.max_thr_lvl_in_sel_period == "caution":
            btn.background_color = "yellow"
        elif apt.max_thr_lvl_in_sel_period == "warning":
            btn.background_color = "red"
        elif apt.max_thr_lvl_in_sel_period == "error":
            btn.background_color = "blue"
        elif apt.max_thr_lvl_in_sel_period == "severe":
            btn.background_color = "purple"
        else:
            btn.background_color = "grey"


