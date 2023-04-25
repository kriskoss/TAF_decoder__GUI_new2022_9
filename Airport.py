import math
from settings import Settings
from Helpers import Helpers
from Runway import Runway
from colouring import prGreen, prYellow, prRed, prPurple, prLightGray



class Airport:

    def __init__(self):
        """Creates an empty Airport object"""

        self.settings = Settings()

        self.apt_code = None
        self.airport_cleaned = None
        self.runways = []

        self.lat =-99
        self.lon = -99


    def get_airport_data_by_apt_code(self, apt_code):
        """
        Fills the Airport object with data using JSON file
        INPUT: ICAO airport code
        OUTPUT: runway info string coloured depending on the runway length
        """
        self.__init__()
        self.apt_code = apt_code
        self.airport_cleaned = Helpers.open_json_file(path="Data_new/airports_cleaned.json")
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
