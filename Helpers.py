import json
class Helpers:

    def open_json_file(self,path):
        with open(path, 'r') as f_obj:
            airport_cleaned = json.load(f_obj)
        return airport_cleaned
