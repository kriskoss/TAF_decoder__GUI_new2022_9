import json
class Helpers:

    @staticmethod
    def open_json_file(path):
        with open(path, 'r') as f_obj:
            dict_from_json = json.load(f_obj)
        return dict_from_json
