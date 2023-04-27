from Classes.Helpers import Helpers
class Route:
    def __init__(self):
        self.route_input = ""
        self.route_list= []
        self.only_valid_points= []
        self.route__corrected_string= ""
        self.dep= ""
        self.dest= ""
    def updateRoute(self, route_input):
        self.route_input = route_input  # Initiazing route input string
        self.route_list, self.only_valid_points = self.__parse_route_input(
            route_input)  # Parses string into two lists: one contains all input points of the route (upper when apt exists, lower when 4-letter code but not valid, x-if inccorect input, different then length of 4. Second list - contains only valid points(airports) )
        self.route__corrected_string = self.__generate_corrected_route_string()  # Converts route list into the string
        self.dep, self.dest = self.get_dest_and_dep_apts()


    def get_corrected_route_string(self):
        return self.route__corrected_string
    def __parse_route_input(self, route_input):
        route_list = []
        only_valid_points = []
        route__raw = route_input.split(" ")
        for item in route__raw:
            if item:
                if len(item)==4:

                    if self.__validate_apt(item):
                        route_list.append(item.upper())
                        only_valid_points.append(item.upper())
                    else:
                        route_list.append(item.lower())

                else:
                    route_list.append('x')
        return route_list, only_valid_points

    def __generate_corrected_route_string(self):
        route_str__corrected = ''
        for item in self.route_list:
            route_str__corrected += " " + item

        return route_str__corrected

    def __check_if_valid_route(self):
        if len(self.only_valid_points) >=2:
            return True
        return False

    def get_dest_and_dep_apts(self):
        """Returns departure and destination airport identifications"""
        if self.__check_if_valid_route():
            return self.only_valid_points[0], self.only_valid_points[-1]
        else:
            return None, None



    @staticmethod
    def __validate_apt(apt_code):
        """This function checks if given airport identification is valid -
        that is: it checks if it apt_code is  in the airports_cleaned.json file database
        INPUT: 4-letter apt_code
        RETURN: True if apt_code is valid, False otherwise
        """
        airports_cleaned = Helpers.open_json_file(path="./Data_new/airports_cleaned.json")

        for i in range(len(airports_cleaned["airport_ident"])):
            # Searching for selected airport identification
            if airports_cleaned["airport_ident"][i].lower() == apt_code.lower():
                return True
        return False
