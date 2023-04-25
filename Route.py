from Helpers import Helpers
class Route:
    def __init__(self, route_input):
        self.route_input = route_input
        self.route_list = self.__parse_route_input(route_input)
        self.route__corrected_string = self.__generate_corrected_route_string()

    def get_corrected_route_string(self):
        return self.route__corrected_string
    def __parse_route_input(self, route_input):
        route_list = list()

        route__raw = route_input.split(" ")
        for item in route__raw:
            if item:
                if len(item)==4:

                    if self.__validate_apt(item):
                        route_list.append(item.upper())
                    else:
                        route_list.append(item.lower())

                else:
                    route_list.append('x')
        return route_list

    def __generate_corrected_route_string(self):
        route_str__corrected = ''
        for item in self.route_list:
            route_str__corrected += " " + item

        return route_str__corrected


    @staticmethod
    def __validate_apt(apt_code):
        """This function checks if given airport identification is valid -
        that is: it checks if it apt_code is  in the airports_cleaned.json file database
        INPUT: 4-letter apt_code
        RETURN: True if apt_code is valid, False otherwise
        """
        airports_cleaned = Helpers.open_json_file(path="Data_new/airports_cleaned.json")

        for i in range(len(airports_cleaned["airport_ident"])):
            # Searching for selected airport identification
            if airports_cleaned["airport_ident"][i].lower() == apt_code.lower():
                return True
        return False
