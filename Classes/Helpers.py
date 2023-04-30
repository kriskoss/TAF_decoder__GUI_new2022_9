import json
class Helpers:

    @staticmethod
    def open_json_file(path):
        with open(path, 'r') as f_obj:
            dict_from_json = json.load(f_obj)
        return dict_from_json

    @staticmethod
    def dump_json_file(path, to_dump):
        with open(path, 'w') as f_obj:
            json.dump(to_dump, f_obj)