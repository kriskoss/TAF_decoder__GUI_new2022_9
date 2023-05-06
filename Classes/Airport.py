import math
from Classes.settings import Settings
from Classes.Helpers import Helpers
from Classes.Runway import Runway
from colouring import prGreen, prYellow, prRed, prLightGray

class Threats:
    def __init__(self):
        self.name =None
        self.caut =[]
        self.warn=[]
        self.sev = []

    def reset_lists(self):
        self.sev.clear()
        self.warn.clear()
        self.caut.clear()
class Apt_threats:
    def __init__(self):
        self.winds = Threats()
        self.vises =Threats()
        self.wxs = Threats()
        self.clds = Threats()

        self.max_lvl__winds = None
        self.max_lvl__vises = None
        self.max_lvl__wxs = None
        self.max_lvl__clds = None

    def reset_all_lists(self):
        self.winds.reset_lists()
        self.vises.reset_lists()
        self.wxs.reset_lists()
        self.clds.reset_lists()

    def sort_groups_according_to_max_threat_in_group(self):
        """This function sorts the groups according to the max threat level in the group"""

        # Simplyfing the names
        wind = self.max_lvl__winds
        vis =self.max_lvl__vises
        wx = self.max_lvl__wxs
        cld = self.max_lvl__clds

        # List of tuples (threat_name, threat_level) - the DEFAULT ORDER
        threats_order = [('wx', wx),
                         ('wind', wind),
                         ('vis', vis),
                         ('cld', cld)]

        new_order = []

        # sort the threats according to the max threat level in the group
        temp_list = sorted(threats_order, key=lambda x: x[1], reverse=True)

        # Convert the list of tuples to a list of threat names
        for i in range(len(temp_list)):
            new_order.append(temp_list[i][0])

        return new_order


class Airport:

    def __init__(self):
        """Creates an empty Airport object"""

        self.settings = Settings()

        self.apt_code = None
        self.airport_cleaned = None
        self.runways = []
        self.TAF__raw = None
        self.METAR_raw =None
        self.max_thr_lvl_in_sel_period = None
        self.combined_station_data = None

        self.threats = Apt_threats()
        self.lat =-99
        self.lon = -99



        # From TAF_decode_function


        self.station_name= None
        self.selected_time_info= None
        self.decoded_TAF= None
        self.runways_length= None
        self.apt_coordinates= None
        self.station_threats= None
        self.thr_lvl_data=None
        self.appr_data= None
        self.time_range= None
        self.max_threat_level_at_airport= None
        self.wind_profile= None
        self.stationObject =None

        self.station_name_color_coded=self.apt_code

    def get_airport_data_by_apt_code(self, apt_code):
        """
        Fills the Airport object with data using JSON file
        INPUT: ICAO airport code
        OUTPUT: runway info string coloured depending on the runway length
        """
        self.__init__()
        self.apt_code = apt_code
        self.airport_cleaned = Helpers.open_json_file(path="./Data_new/airports_cleaned.json")
        self.runways = self.__get_runway_info(self.airport_cleaned)
        self.__get_apt_coordinates()

        return self.__get_runway_info_for_display()

    def __get_runway_info_for_display(self):
        # Making runway information ready for display
        runway_info_for_display = []
        for runway in self.runways:
            # Extracting data from dictionary
            le_len = runway.length__meters
            le_width = runway.width__meters

            he_len = runway.length__meters
            he_width = runway.width__meters

            le_name = runway.le_ident
            he_name = runway.he_ident

            # Rounding runway length
            le_len = math.floor(le_len / 100) * 100
            he_len = math.floor(he_len / 100) * 100

            # Getting color changeover thresholds from settings
            s_rwy = self.settings.short_runway
            m_rwy = self.settings.medium_runway
            l_rwy = self.settings.long_runway
            vl_rwy = self.settings.very_long_runway

            # RUNWAY LENGTH string recolouring depending on its LENGTH
            # Initializing variables
            le_len_str = 'xx'
            he_len_str = 'xx'

            # recolouring LOW END threshold
            if le_len < s_rwy:
                le_len_str = prLightGray(str(le_len))
            elif le_len < m_rwy:
                le_len_str = prRed(str(le_len))
            elif le_len < l_rwy:
                le_len_str = prYellow(str(le_len))
            elif le_len >= l_rwy:
                le_len_str = prGreen(str(le_len))

                # Recoloring of HI END threshold
            if he_len < s_rwy:
                he_len_str = prLightGray(str(he_len))
            elif he_len < m_rwy:
                he_len_str = prRed(str(he_len))
            elif he_len < l_rwy:
                he_len_str = prYellow(str(he_len))
            elif he_len >= l_rwy:
                he_len_str = prGreen(str(he_len))

            # RUNWAY NAME recolouring - it becomes gray for VERY SHORT runway
            if le_len < s_rwy:
                le_name = prLightGray(le_name)
            if he_len < s_rwy:
                he_name = prLightGray(he_name)

                # If runway is narrow then width becomes RED
            if le_width < self.settings.normal_width_runway:
                le_width = prRed(le_width)

            # Concatenating single runway data into one string
            if le_len == he_len:
                # Runway is same length for both landing direction
                runway_info_for_display.append(
                    f"{le_name}|{he_name} {le_len_str}({le_width})")
            else:
                # Different lengths for both ends
                runway_info_for_display.append(
                    f"{le_name}|{he_name} {le_len_str}({le_width}){he_len_str}")

        ## COMBINING RUNWAY INFO INTO ONE STRING
        runways_info_for_display = '\n   '.join(runway_info_for_display)

        return runways_info_for_display



    # PRIVATE (make it if possible)
    def __get_runway_info(self,airport_cleaned):
        rwys= []
        for i in range(len(airport_cleaned["airport_ident"])):
            # Searching for selected airport identification
            if airport_cleaned["airport_ident"][i] == self.apt_code:

                # Creating runway object
                rwy = Runway(
                    airport_cleaned["length__meters"][i] - airport_cleaned["le_displaced_threshold__meters"][i],
                    airport_cleaned["width__meters"][i],
                    airport_cleaned["le_ident"][i],
                    airport_cleaned["le_heading_degT"][i],
                    airport_cleaned["le_displaced_threshold__meters"][i],
                    airport_cleaned["le_latitude_deg"][i],
                    airport_cleaned["le_longitude_deg"][i],
                    airport_cleaned["he_ident"][i],
                    airport_cleaned["he_heading_degT"][i],
                    airport_cleaned["he_displaced_threshold__meters"][i],
                    airport_cleaned["he_latitude_deg"][i],
                    airport_cleaned["he_longitude_deg"][i]
                )
                # Adding runway object to the list
                rwys.append(rwy)
        return rwys

    def __get_apt_coordinates(self):
        if len(self.runways)>0:
            lat = (self.runways[0].le_latitude_deg + self.runways[0].he_latitude_deg)/2
            lon = (self.runways[0].le_longitude_deg + self.runways[0].he_longitude_deg)/2

            # Storing apt coordinates
            self.lat = lat
            self.lon = lon

            return lat,lon
        else:
            print("ERROR: No runways found for this airport", "Taf_decoder.get_apt_coordinates AAAAA")
            return -99,-99
##### END OF CLASSES TEST ###############################
