from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.app import App    # This imports App class from kivy.app

import final_program_functions as fpf
from Classes.Route import Route
from Classes.Airport import Airport
from Classes.settings import Settings
from Classes.Helpers import Helpers
from TAF_decoder import TAF_decoder_function
from kivy.utils import escape_markup
import threading
import collections
import copy

import colouring

# from main import TheTAFApp # just for syntax
settings = Settings()


class EnrouteAirportsControls:
    """This class contain all functionality related to displaying Enroute Airports"""
    def __init__(self, mapControls, **kwargs):

        self.appr_data_font_size = 13

        self.mapControls = mapControls
        self.current_route = Route()
        self.analyzed_enr_apts__ready_for_btn_update__QUEUE = collections.deque()
        self.enr_apts_invalid_stations =[]

        self.ready_for_enr_apts_btns_change_of_color = False
        self.enr_apt__btn__identifier = "btnID:"
        self.rout_input__widget__STATE = None
        self.colour_change_finished = False
        self.creating_enr_apts_buttons_finished = False
        self.update_period_in_MessageBox = False

        self.current_threats_period = None  # This variable stores the current threats period (in hours) displayed on the enrDisplay page

        self.single_current_enr_apt_DISPALYED = None    # Stores the current Enroute Airport displayed on enrDisplay page
        self.all_current_enr_apts_BUTTONS = []      # This list contains all buttons for Enroute Airports for the current PERIOD. Enables to restore deleted buttons



    def show_current_period(self,app):
        if self.update_period_in_MessageBox and not app.find_thread("Enr_apts__TAF_decoding__THREAD"):
            self.update_period_in_MessageBox = False
            widget = self.get_MessageBox__widget()
            widget.text = f'Threats valid from: {app.value__start_slider}:00 UTC (+ {self.current_threats_period} hours)'

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
                self.get_MessageBox__widget().text = f'FINDING ENROUTE APTS...'
                self.creating_enr_apts_buttons_finished = True

        # Clearing ENROUTE APTS MESSAGE BOX
        if self.creating_enr_apts_buttons_finished and not self.mapControls.ready_for_enroute_markers:
            self.creating_enr_apts_buttons_finished = False
            self.get_MessageBox__widget().text = ""

    def update_btns_for_threat_level(self,app):
        """FUNCTION CALLED app.update_clock:
        This function updates the buttons for the Enroute Apts page with the threat level"""



        # UPDATING ENROUTE APTS BUTTONS COLOR
        if (self.ready_for_enr_apts_btns_change_of_color and app.find_thread("Enr_apts__TAF_decoding__THREAD")) or app.enrAptsCtrls.colour_change_finished == True:

            enr_apts__queue = self.analyzed_enr_apts__ready_for_btn_update__QUEUE
            enr_apts_stack__widget = app.enrAptsCtrls.getEnr_apts_stack__widget()

            self.get_MessageBox__widget().text = f'LOADING THREAT LEVELS....'
            while len(enr_apts__queue) > 0:
                apt = enr_apts__queue.popleft()

                # Change btn background colour depending on the apt MAX threat level
                self.changeEnrAptButtonColor(apt, enr_apts_stack__widget)

                ### RUNS ONLY IF THERE IS ANY THREAT AT THE APT
                if apt.thr_lvl_data:
                    line = self.get_main_threats_for_enr_apt(apt) # CORE function !! checks threats at specific group (wx,wind,vis and cld) and creates the string to be added to the button text
                    self.changeEnrAptText(apt, enr_apts_stack__widget, line)

            self.colour_change_finished = True  # This enables a LAST PASS

        # CLEARES ENROUTE APTS MESSAGE BOX once the colour change is finished
        if self.colour_change_finished and not self.ready_for_enr_apts_btns_change_of_color:
            self.colour_change_finished = False
            self.get_MessageBox__widget().text = ""

    ################### THREATS IN ENROUTE APTS PAGE #############################
    def get_main_threats_for_enr_apt(self,apt):
        """Gets the threats from the data to be displayed next to the ENR APT button"""
        apt:Airport

        apt.threats.reset_all_lists()
        winds = apt.threats.winds
        vises = apt.threats.vises
        clds = apt.threats.clds
        wxs = apt.threats.wxs
        apt.station_name_color_coded = None

        # CLEAR DATA

        for n in range(len(apt.thr_lvl_data)):

            # GETTING APT CODE
            if n == 0:
                if len(apt.thr_lvl_data[n]['wind']) > 1:
                    apt.station_name_color_coded = apt.thr_lvl_data[n]['wind'][1]

            # GETTING WEATHER
            elif n > 0:
                # CHECKING EACH KEY
                for k in apt.thr_lvl_data[n].keys():

                    # ADDING WEATHER DATA to the different threat lists
                    data_for_key = apt.thr_lvl_data[n][k]
                    if data_for_key:
                        # WIND
                        for i in data_for_key:
                            # Continues when item is in valid period
                            if i[3] != 'not-relevant TEMPO' and i[3] != 'not-relevant BECMG' and i[3] != 'not-relevant INTER':

                                if k == 'wind' :
                                    self.clasifing_threats_for_key(i, winds, k)

                                if k == 'vis':
                                    self.clasifing_threats_for_key(i, vises, k)

                                if k == 'weather':
                                    self.clasifing_threats_for_key(i, wxs, k)

                                if k == 'clouds':
                                    self.clasifing_threats_for_key(i,clds, k)

        # UPDATING THREATS
        wind_line = self.get_WIND_line__and_max_lvl(winds, "", apt)
        vis_line = self.get__VIS_line_and_max_lvl(vises, "", apt)
        clds_line = self.get_CLDS_line_and_max_lvl(clds, "", apt)
        wx_line = self.get_WX_line_and_max_lvl(wxs, "", apt)

        threats_order = apt.threats.sort_groups_according_to_max_threat_in_group()

        # CREATING STRING LINE
        line = ""
        for i in range(len(threats_order)):
            if threats_order[i] == 'wind':
                line+=wind_line

            elif threats_order[i] == 'vis':
                line+=vis_line

            elif threats_order[i] == 'cld':
                line+=clds_line

            elif threats_order[i] == 'wx':
                line+=wx_line



        # line =""
        #
        # line = self.update_threats_line_VIS(vises, line,apt)
        # line = self.update_threats_line_WX(wxs, line,apt)
        # line = self.update_threats_line_CLDS(clds, line,apt)


        return line
    @staticmethod
    def clasifing_threats_for_key(i, group, name):
        """Places wx,cld, vis or wind in propper threat bucket"""
        group.name = name
        if i[0] == 'caution':
            group.caut.append(i[1])
        if i[0] == 'warning':
            group.warn.append(i[1])
        if i[0] == 'severe':
            group.sev.append(i[1])

    @staticmethod
    def get_WX_line_and_max_lvl(wxs, line, apt):
        """Updates the line with the WX threats"""
        max_lvl = 0 # Initializing max level in the group - 0 means GREEN
        ### SEVERE WX
        if wxs.sev:
            if max_lvl < 3: # SEVERE WX detected and becomes the highest threat
                max_lvl = 3

            wx_only = True
            FG_in = False # FOG in any form in the wxs.sev list
            TS_in = False # THUNDERSTORM in any form in the wxs.sev list
            SN_in = False # SNOW in any form in the wxs.sev list
            for wx in wxs.sev:
                if "FG" in wx:
                    wx_only = False
                    FG_in = True
                if "TS" in wx:
                    TS_in = True
                    wx_only = False
                if "SN" in wx:
                    SN_in = True
                    wx_only = False

            if FG_in:
                line += f"{colouring.prPurple('FG ')}"
            if SN_in:
                line += f"{colouring.prPurple('SN ')}"
            if TS_in:
                line += f"{colouring.prPurple('TS ')}"

            # NO FOG, SNOW OR TS IN SEVERE WX
            if wx_only:
                line += f"{colouring.prPurple('WX ')}"


        ### WARNING WX
        elif wxs.warn:
            if max_lvl < 2: # WARNING WX detected and becomes the highest threat if there is no SEVERE WX
                max_lvl = 2

            wx_only = True
            FG_in = False # FOG in any form in the wxs.warn list
            TS_in = False # THUNDERSTORM in the wxs.warn list
            SN_in = False # SNOW in any form in the wxs.warn list
            for wx in wxs.warn:
                if "FG" in wx:
                    wx_only = False
                    FG_in = True
                if "TS" in wx:
                    TS_in = True
                    wx_only = False
                if "SN" in wx:
                    SN_in = True
                    wx_only = False


            if FG_in:
                line += f"{colouring.prRed('FG ')}"
            if SN_in:
                line += f"{colouring.prRed('SN ')}"
            if TS_in:
                line += f"{colouring.prRed('TS ')}"

            # NO FOG, SNOW OR TS IN WARNING WX
            if wx_only:
                line += f"{colouring.prRed('WX ')}"


        ### CAUTION WX
        elif wxs.caut:
            if max_lvl < 1: # CAUTION WX detected and becomes the highest threat if there is no SEVERE or WARNING WX
                max_lvl = 1

            wx_only = True
            MIFG_in = False # FOG in any form in the wxs.warn list
            BR_in = False
            SN_in = False
            RA_in = False
            for wx in wxs.caut:
                if "MIFG" in wx:
                    wx_only = False
                    MIFG_in = True
                if "BR" in wx:
                    BR_in = True
                    wx_only = False
                if "SN" in wx:
                    SN_in = True
                    wx_only = False
                if "RA" in wx:
                    RA_in = True
                    wx_only = False


            if MIFG_in:
                line += f"{colouring.prYellow('MIFG ')}"

            if SN_in:
                line += f"{colouring.prYellow('SN ')}"
            if RA_in:
                line += f"{colouring.prYellow('RA ')}"
            if BR_in:
                line += f"{colouring.prYellow('BR ')}"

            # NO SNOW, RAIN, BR OR MIFG IN CAUTION WX
            if wx_only:
                line += f"{colouring.prYellow('WX ')}"

        else:
            apt.threats.max_lvl__wxs = max_lvl
            return line
        apt.threats.max_lvl__wxs = max_lvl
        return line + " "

    @staticmethod
    def get_WIND_line__and_max_lvl(winds, line, apt):
        max_lvl = 0

        if winds.sev:
            line += f"{colouring.prPurple('WIND')}"
            if max_lvl <3:
                max_lvl=3
        elif winds.warn:
            line += f"{colouring.prRed('WIND')}"
            if max_lvl<2:
                max_lvl=2
        elif winds.caut:
            line += f"{colouring.prYellow('WIND')}"
            if max_lvl<1:
                max_lvl=1
        else:
            apt.threats.max_lvl__winds= max_lvl
            return line
        apt.threats.max_lvl__winds = max_lvl
        return line + " "

    @staticmethod
    def get_CLDS_line_and_max_lvl(clds, line, apt):
        max_lvl = 0
        if clds.sev:
            line += f"{colouring.prPurple('CLD')}"
            if max_lvl <3:
                max_lvl=3
        elif clds.warn:
            line += f"{colouring.prRed('CLD')}"
            if max_lvl<2:
                max_lvl=2
        elif clds.caut:
            line += f"{colouring.prYellow('CLD')}"
            if max_lvl<1:
                max_lvl=1
        else:
            apt.threats.max_lvl__clds = max_lvl
            return line

        apt.threats.max_lvl__clds = max_lvl
        return line + " "

    def get__VIS_line_and_max_lvl(self, vis, line, apt):
        max_lvl = 0
        if vis.sev:
            max_lvl = 0
            min_vis = 9999
            vis_active = False
            for vi in vis.sev:
                vi =self.remove_markup_from_vis(vi)
                if int(vi) < min_vis:
                    min_vis = int(vi)
                    vis_active = True
                    if max_lvl < 3:
                        max_lvl = 3


            if vis_active:
                line += f"{colouring.prPurple(str(min_vis))}"
            else:
                line += f"{colouring.prPurple('VIS')}"

        elif vis.warn:
            min_vis = 9999
            vis_active = False
            for vi in vis.warn:
                vi = self.remove_markup_from_vis(vi)
                if int(vi) < min_vis:
                    min_vis = int(vi)
                    vis_active = True
                    if max_lvl < 2:
                        max_lvl = 2
            if vis_active:
                line += f"{colouring.prRed(str(min_vis))}"
            else:
                line += f"{colouring.prRed('VIS')}"


        elif vis.caut:
            min_vis = 9999
            vis_active = False
            for vi in vis.caut:
                vi = self.remove_markup_from_vis(vi)
                if int(vi) < min_vis:
                    min_vis = int(vi)
                    vis_active = True
                    if max_lvl < 1:
                        max_lvl = 1

            if vis_active:
                line += f"{colouring.prYellow(str(min_vis))}"
            else:
                line += f"{colouring.prYellow('VIS')}"

        else:
            apt.threats.max_lvl__vises = max_lvl
            return line
        apt.threats.max_lvl__vises = max_lvl
        return line + " "

    @staticmethod
    def remove_markup_from_vis(vis):
        """Removes markup from vis"""
        vis: str
        prev_ch = ""

        i = -1
        for ch in vis:  # checking each character in the marked up vis string
            i += 1
            if prev_ch == "]" and ch != "[":  # if the previous character was a ] and the current is not a [ then we have reached the end of the markup
                break
            prev_ch = ch

        try:
            int(vis[i:i + 4])  # checking if the vis is in the format of four digits
        except(ValueError):
            print("ERRORO IN CONVERTION OF VIS - EAC.py")
            return -99
        return int(vis[i:i + 4])

    ####################### END OF THREATS IN ENR-APT #######################
    def add_wind(self,thr_lvl_data, n, data_for_key, wind_line, k):
        """TO SIMPLYFY CODE - ADDs wimd only if it is NOT not-relevant"""
        if thr_lvl_data[n]['wind']:
            if not "not-relevant" in thr_lvl_data[n]['wind'][0][3]:

                if k == 'time_group':
                    # IF TIME GROUP then start new line after
                    wind_line.append(data_for_key[1] + ' newlinee.Tdf')
                else:
                    wind_line.append(data_for_key[1])

    def getEnr_apts_stack__widget(self):
        app = App.get_running_app() # This gets the running app - in this case it is the main.py

        return app.root.ids['id__enr_apts'].ids['id__EnrApts__scroll'].ids['Enr_apts_stack']


    def get_MessageBox__widget(self):

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
            markup = True,
            size_hint=(1, None),
            height=dp(30),
            # width=dp(100),
            font_name="Resources/Fonts/JetBrainsMono-Regular.ttf",
            font_size='20dp',
            background_color="lightgray",
            on_press=lambda *args: self.display_enr_apt_info(apt),
            # background_normal=''  # MODIIES HOW COLOR ARE BEING DISPLAYED
        )

        widget.ids[self.enr_apt__btn__identifier + apt.apt_code] = btn  # CORRECT WAY based on the above
        widget.add_widget(btn)
        self.all_current_enr_apts_BUTTONS.append(btn) # Stores the button for later use - it is cleared when the period is changed

    def get_enrDetails__DisplayLabel(self):
        app = App.get_running_app()

        return app.root.ids['id__enrDetails'].ids['EnrDetails__DisplayLabel']



    def add_enr_btns(self, widget):
        enroute_airports = self.mapControls.getEnrouteAirports()
        apt: Airport
        for apt in enroute_airports:
            btn = Button(
                markup=True,
                halign='left',
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

            self.current_threats_period = n
            self.update_period_in_MessageBox = True


            self.refresh_enroute_apts_buttons(app)



    def next_nh__enrDetails_page(self,n):
        #3h,6h,12h,
        app = App.get_running_app()

        # Updating slider values
        app.value__start_slider = str(int(app.time_now.strftime("%H"))+1) # + 1 to start counting from the next full hour
        temp_end_time = str(int(app.value__start_slider) + n)

        # app: TheTAFApp
        apt_copy = copy.deepcopy(self.single_current_enr_apt_DISPALYED)

        # DECODING TAF for the selected station

        decoded_TAF_dict, apt_copy.stationObject = TAF_decoder_function(settings, apt_copy.TAF__raw, -1, int(app.value__start_slider), int(temp_end_time))
        apt = self.transfer_data_from__decoded_TAF_dict__to__apt_object(decoded_TAF_dict,apt_copy)
        app.current_difference = n
        widget = self.get_enrDetails__DisplayLabel()
        widget.text = self.enrDisplay__format_final_string(apt)

        app.temp_current_difference_str = app.current_difference_str
        app.current_difference_str = str(n)


    def restore_current_difference_str(self):
        app = App.get_running_app()
        app.current_difference_str = app.temp_current_difference_str

    def display_enr_apt_info(self,apt):
        ### CORE FUCNTION ### for EnrDisplay Screen
        """Function responsible for DISPLAYING TAFs for ENR APTS
        * Called when ENR APT button pressed *"""
        self.single_current_enr_apt_DISPALYED = apt
        app = App.get_running_app()  # This gets the running app - in this case it is the main.py
        widget = self.get_enrDetails__DisplayLabel()

        # Switches Screen
        app.root.current = "EnrDetails__Screen"
        app.root.transition.direction = "left"

        apt: Airport

        ### UPDATING THE ENR APT TAF DISPLAY FOR APT
        widget.text = self.enrDisplay__format_final_string(apt)

    def enrDisplay__format_final_string(self,apt):
        if apt.appr_data:
            s = f'{apt.decoded_TAF} \n ' \
            f'\n\n[size={self.appr_data_font_size}dp]****** APPR INFO *******' \
            f'\n{apt.appr_data.replace("       ","")}'
        else:
            s = f'{apt.decoded_TAF} \n ' \
                f'\n\n[size={self.appr_data_font_size}dp]****** APPR INFO *******' \
                f'\n{apt.appr_data}'
        return s

    def refresh_enroute_apts_buttons(self, app):
        enr_apts_stack__widget =self.getEnr_apts_stack__widget()
        # self.recreate_enr_btns_with_threat_colour(app,enr_apts_stack__widget)

        self.ready_for_enr_apts_btns_change_of_color = True
        self.rout_input__widget__STATE = self.get__route_input()
        t = threading.Thread(name="Enr_apts__TAF_decoding__THREAD", target=self.recreate_enr_btns_with_threat_colour, args =[app,enr_apts_stack__widget])
        t.start()



    def recreate_enr_btns_with_threat_colour(self,app,widget):
        """Changes the ENR APTS buttons backgroud depeding on the threat level. Contains a THREAD"""

        apt: Airport
        enr_apts_obj: list[Airport]
        enr_apts_objs  = app.mapControls.apts_enroute # List of Airport instances

        # Extracting apt_codes from Airport objects
        enroute_apts__apt_codes=[]
        TAF_num = 0 # Enumerates the decoded TAFs
        for apt in enr_apts_objs:
            enroute_apts__apt_codes.append(apt.apt_code)

            ## CORE FUNCTION###
            self.analyze_enr_apt(app, apt, TAF_num)

            # SENDS APT TO THE QUEUE - main.py to update as THREAD goes
            self.analyzed_enr_apts__ready_for_btn_update__QUEUE.append(apt)

            TAF_num+=1

        # Thread completed its job - sends this data to main.py update_clock funcion.
        self.ready_for_enr_apts_btns_change_of_color = False



    def analyze_enr_apt(self,app, apt:Airport, TAF_num):
        # app: TheTAFApp
        apt.METAR_raw = fpf.load_single_METAR(apt.apt_code)
        return_data = fpf.get_single_stations_TAF(settings, apt.apt_code)
        if type(return_data)==list:
            return [apt.apt_code, "error"]

        else:
            apt.TAF__raw = return_data


            # DECODING TAF for the selected station
            decoded_TAF_dict, apt.stationObject = TAF_decoder_function(settings, apt.TAF__raw, TAF_num, int(app.value__start_slider), int(app.value__end_slider))

            # Data transfer to apt object
            self.transfer_data_from__decoded_TAF_dict__to__apt_object(decoded_TAF_dict, apt)

            max_thrts_at_apt = app.get_max_threat_level_for_selected_airports(settings, [apt.apt_code], int(app.value__start_slider),
                                                                                 int(app.value__end_slider))
            apt.max_thr_lvl_in_sel_period = max_thrts_at_apt[0][1][0]

            # apt.combined_station_data = fpf.combine_data(settings,
            #                                             decoded_TAF_dict["station_threats"],
            #                                             decoded_TAF_dict["wind_profile"],
            #                                             decoded_TAF_dict["runways_length"],
            #                                             decoded_TAF_dict["appr_data"])


            return apt.apt_code,apt.max_thr_lvl_in_sel_period

    def transfer_data_from__decoded_TAF_dict__to__apt_object(self,decoded_TAF_dict, apt):

        apt.station_name = decoded_TAF_dict["station_name"]
        apt.selected_time_info = decoded_TAF_dict["selected_time_info"]

        apt.decoded_TAF = decoded_TAF_dict["decoded_TAF"].replace('space.Tdf', '   ').replace("newlinee.Tdf", '\n')

        apt.runways_length = decoded_TAF_dict["runways_length"]
        apt.apt_coordinates = decoded_TAF_dict["apt_coordinates"]
        apt.station_threats = decoded_TAF_dict["station_threats"]

        apt.thr_lvl_data = decoded_TAF_dict["thr_lvl_data"]

        apt.appr_data = decoded_TAF_dict["appr_data"]
        apt.appr_data.replace('space.Tdf', '   ')  # Replacing SPACE marker in String
        apt.appr_data.replace("newlinee.Tdf", '\n')  # Replacing NEWLINEE marker in String

        apt.time_range = decoded_TAF_dict["time_range"]
        apt.max_threat_level_at_airport = decoded_TAF_dict["max_threat_level_at_airport"]
        apt.wind_profile = decoded_TAF_dict["wind_profile"]

        return apt
    def changeEnrAptButtonColor(self,apt, widget):
        apt: Airport

        btn =  widget.ids[self.enr_apt__btn__identifier + apt.apt_code]

        btn.opacity = 1.0
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
            btn.background_color = "gray"
            btn.opacity = 0.25
            if settings.remove_enr_apt_which_has_no_valid_wx:
                widget.remove_widget(btn)

    def changeEnrAptText(self,apt, widget, text):
        """Changes the text of the button depending on the threat level at the airport"""
        apt: Airport
        btn:Button
        btn =  widget.ids[self.enr_apt__btn__identifier + apt.apt_code]

        btn.text = f"   {apt.station_name_color_coded}     [size=14dp]{text}[/size]"
        btn.text_size = btn.size



    def save_last_route(self):
        """Saves the last route to the file"""
        path = "Data_new/last_route.json"
        widget = self.get__route_input()
        if widget.text != "":
            Helpers.dump_json_file(path, widget.text)

    def load_last_route(self):
        """Loads the last route from the file"""
        path = "Data_new/last_route.json"
        widget = self.get__route_input()
        widget.text = Helpers.open_json_file(path)