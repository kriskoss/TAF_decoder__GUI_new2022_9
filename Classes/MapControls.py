import collections
import threading
import json

from TAF_decoder import SingleStation
from Classes.Airport import Airport

from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivy.app import App    # This imports App class from kivy.app

from geographiclib.geodesic import Geodesic
from geopy.distance import geodesic


class MapControls:
    """This class is used to control the map"""
    def __init__(self):
        self.airport_cleaned = None      # Initialization of the varialbe - will store the airport data base
        self.enr_apts_to_be_added_queue = collections.deque()       # QUEUE: one thread enqueue it with airports which markers are to be put on map, while the other thread dequeue it when MapMarker added for specific airport
        self.apts_enroute = []      # Stores Airport objects - those are Enroute Airports found enroute

        # Positions/points
        self.rhumb_line_inter_pts = []    # Markers to indicate positions on the Rhumb Line connecting DEP to DEST
        self.GC_line_inter_pts = []     # Markers to indicate positions on the Great Circle Line connecting DEP to DEST

        # MapMarkers
        self.g_group_mapMarkers = []        # Stores MapMarkers indicating g_group airports - used only to REMOVE them when necessary
        self.pts_btwn_apts_mapMarkers = []      # Stores MapMarkers indicating positions on the Rhumb or Great Circle line
        self.apts_enroute__mapMarkers = []

        self.enr_apts_generating = False        # This variable is used to indicate if the thread is currently generating Enroute Airports

    def getEnrouteAirports(self):
        """This function returns a list of enroute airports"""
        return self.apts_enroute

    def add_current_g_group_markers(self):
        """Adds markers to the map for all stations in the current g_group"""
        # Getting mapView widget
        app = App.get_running_app()
        mapView_my = app.root.ids['map'].ids['id__MapView_my']
        # CLEAR PREVIOUS MARKERS
        self.clear_enroute_markers(mapView_my)
        self.clear_previous_g_group_markers(mapView_my)

        # This is pre-annotation syntax for type hinting
        stationObject: SingleStation

        for stationObject in app.stationsList:
            # Adding marker to the map
            mkr = MapMarker(lat=stationObject.apt_coordinates[0],
                            lon=stationObject.apt_coordinates[1])
            mapView_my.add_marker(mkr)

            # Adding marker to the list of markers - to be able to remove them later
            self.g_group_mapMarkers.append(mkr)

    def clear_enroute_markers(self, mapView_my):
        for mkr in self.apts_enroute__mapMarkers:
            mapView_my.remove_marker(mkr)

    def clear_previous_g_group_markers(self,mapView_my):
        for mkr in self.g_group_mapMarkers:
            mapView_my.remove_marker(mkr)


    def pts_btwn_apts(self):
        if self.enr_apts_generating == False:
            app = App.get_running_app()

            # Getting acces to the MapView widget
            mapView_my = app.root.ids['map'].ids['id__MapView_my']

            # Clearing map of the previous g_group markers
            self.clear_enroute_markers(mapView_my)
            self.clear_previous_g_group_markers(mapView_my)

            # Adding DEP an DEST apts
            apt1 = Airport()    # Creates empty Airport objrct
            apt1.get_airport_data_by_apt_code('EGPD')   # Populates Airport object with data

            # app: main.TheTAFApp
            # app.enrAptsCtrls.
            # apt1.get_airport_data_by_apt_code(app.)   # Populates Airport object with data

            apt2 = Airport()
            apt2.get_airport_data_by_apt_code('LLBG')

            # Clearing map of the previous g_group markers
            for mkr in self.pts_btwn_apts_mapMarkers:
                mapView_my.remove_marker(mkr)

            # Adding DEP/DEST markers
            dep_apt = apt1
            dest_apt = apt2
            dep_mkr = MapMarker(lat=dep_apt.lat, lon=dep_apt.lon)
            dest_mkr = MapMarker(lat=dest_apt.lat, lon=dest_apt.lon)

            mapView_my.add_marker(dep_mkr)
            mapView_my.add_marker(dest_mkr)


            ### Adding markers at interpolated coordinates ###
            # self.drawRhumbLineMarkers(mapView_my, dep_apt,dest_apt)
            self.drawGreatCircleMarkers(mapView_my, dep_apt,dest_apt, 90)

            ### Getting airports that meet the specific coordinates/distance condition ###

            # Opening the airport data file
            self.airport_cleaned = self.open_json_file("./Data_new/airports_cleaned.json")


            # Searching for airports that meet conditions
            app.ready_for_enroute_markers = True
            self.enr_apts_generating = True
            t1 = threading.Thread(name="Add_enroute_markers", target=self.get_enroute_apts, args=[])
            t1.start()

    def drawRhumbLineMarkers(self, mapView_my, dep_apt,dest_apt):
        steps = 30
        lat_step = (dest_apt.lat - dep_apt.lat) / steps
        lon_step = (dest_apt.lon - dep_apt.lon) / steps

        # CREATING MARKERS
        for i in range(steps):
            lat_mkr = dep_apt.lat + i * lat_step  # Calculates the marker coordinates
            lon_mkr = dep_apt.lon + i * lon_step

            mkr = MapMarker(lat=lat_mkr, lon=lon_mkr)  # Creates marker object
            mkr.source = "Resources/MapMarkers/inter_mkr.png"
            mapView_my.add_marker(mkr)  # Adds marker to the map
            self.pts_btwn_apts_mapMarkers.append(mkr)  # Add markers to the list - this enables removal of the markers later

    def drawGreatCircleMarkers(self, mapView_my, dep_apt,dest_apt, dist_btwn_markers):
        # Create a geodesic line between the two points
        line = Geodesic.WGS84.InverseLine(dep_apt.lat, dep_apt.lon, dest_apt.lat, dest_apt.lon)

        # Set the distance interval to 100 km
        ds = dist_btwn_markers*1000 # [m]

        # Loop over the distance along the line
        for s in range(0, int(line.s13) + ds, ds):
            # Get the position of the point at distance s
            pos = line.Position(s)

            # Add add markaer to the mapView
            lat_mkr = pos['lat2']
            lon_mkr = pos['lon2']

            mkr = MapMarker(lat=lat_mkr, lon=lon_mkr)  # Creates marker object
            mkr.source = "Resources/MapMarkers/inter_mkr.png"

            mapView_my.add_marker(mkr)  # Adds marker to the map
            self.pts_btwn_apts_mapMarkers.append(mkr)  # Add markers to the list - this enables removal of the markers later

            # Print the latitude, longitude, and azimuth
            print("s = {:.3f} km: lat = {:.5f}, lon = {:.5f}, azi = {:.5f}".format(
                s / 1000, pos['lat2'], pos['lon2'], pos['azi2']))

            # Storing intermediate points
            self.GC_line_inter_pts.append(pos)

    def get_enroute_apts(self):
        max_dist= 200 # [km]
        prev_apt_code = ""
        enroute_apts_code = [] # Stores only apt_codes - used to check if apt was already selected as an enroute_apt

        pos_index=0
        for pos in self.GC_line_inter_pts:
            pos_index+= 1


            # CALCULATING DELTA LAT
            delta_lat = 0
            lat_dist = -1
            while lat_dist < max_dist / 2:
                lat_dist = abs(geodesic((pos["lat2"], pos["lon2"]),
                                    (pos["lat2"] + delta_lat, pos["lon2"]) ))
                delta_lat += 0.01
                delta_lat=round(delta_lat,3)

            # CALCULATING DELTA LON
            delta_lon = 0
            lon_dist = -1
            while lon_dist < max_dist / 2:
                lon_dist = abs(geodesic((pos["lat2"], pos["lon2"]),
                                    (pos["lat2"], pos["lon2"] + delta_lon)))
                delta_lon += 0.01
                delta_lon = round(delta_lon,3)


            print("########## POS " + str(pos_index) + " ##################")
            for i in range(len(self.airport_cleaned["airport_ident"])):
                apt_lat = self.airport_cleaned["le_latitude_deg"][i]
                apt_lon = self.airport_cleaned["le_longitude_deg"][i]
                apt_code = self.airport_cleaned["airport_ident"][i]

                ### SELECTION OF AIRPORTS ENROUTE
                # INITIAL SELECTION - based on COORDINATES
                if  apt_code not in enroute_apts_code and\
                        prev_apt_code != apt_code and \
                        pos["lat2"]- delta_lat < apt_lat < pos["lat2"]+ delta_lat and \
                        pos["lon2"] - delta_lon < apt_lon < pos["lon2"]+ delta_lon:

                    # PRECISE SELECTION - based on DISTANCE
                    pt = (pos["lat2"], pos["lon2"])
                    ap = (apt_lat, apt_lon)
                    # wgs84 = Geodesic.WGS84 # NOT requred here
                    dist = int(geodesic(pt, ap).km)

                    if dist < max_dist:     # Checks if distance to the airport and pont at great_circle line is less than required
                        apt = Airport()     # Creating empty Airport Object
                        apt.get_airport_data_by_apt_code(apt_code) # Adding data to the airport object using apt_code

                        print("   Enroute apt:" +   apt_code + ", dist: " + str(dist) + " km,   (main.py => apt_code,str(dist))")

                        self.apts_enroute.append(apt)   # Adds Airport object in the list
                        self.enr_apts_to_be_added_queue.append(apt)  # ENQUEUE   - probably this queue is used in separate thread to add markers on the map

                        enroute_apts_code.append(apt_code) # airport code stored to be used to detect duplicates
                        prev_apt_code = apt_code

        self.enr_apts_generating = False
    def addMarker(self,apt):
        app = App.get_running_app()
        mapView_my = app.root.ids['map'].ids['id__MapView_my']

        mkr = MapMarker(lat=apt.lat, lon=apt.lon)

        mapView_my.add_marker(mkr)
        self.apts_enroute__mapMarkers.append(mkr)

    def open_json_file(self,path):
        with open(path, 'r') as f_obj:
            airport_cleaned = json.load(f_obj)
        return airport_cleaned
