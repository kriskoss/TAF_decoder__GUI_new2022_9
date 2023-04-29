import datetime
import json
import math

from kivy.properties import StringProperty

import final_program_functions as fpf
from dateutil.parser import parse   # check https://stackabuse.com/converting-strings-to-datetime-in-python/
                                    # module which automatically converts time string into the datetime format

class MainPage:
    def __init__(self):
        self.last_reload_failed = False
        self.num_TAFs_downloaded = '--'
        # self.reload_status="#935999"
        # self.reload_button_msg = "Reload TAFs"

    def call_TAFs_reload(self, app):
        """Method called when TAFs reload button is pressed"""

        try:
            # TRIES TO DOWNLOAD TAFs and METARs
            self.num_TAFs_downloaded = str(fpf.download_taf_database(parse))
            fpf.download_metars_database(parse)
        # UPDATE FAILED
        except:
            # set FLAG to TRUE
            self.num_TAFs_downloaded = '--'
            self.last_reload_failed = True
            app.reload_status = "#ff0015"
            app.reload_button_msg = "TAFs Reload - FAILED!"

        # UPDATE SUCCESSFUL
        else:
            # set FLAG to FALSE
            self.last_reload_failed = False

            # create STRING from DATETIME object using the following format
            reload_time = datetime.datetime.utcnow().strftime("%H:%M'%S UTC  %d-%m-%Y")

            # Saving last update time
            path = "Data_new/last_reload_time.json"
            with open(path, "w") as f_obj:
                json.dump(reload_time, f_obj)

            # Updating button and label
            app.reload_status = "#00ff59"
            app.reload_button_msg = "TAFs Reload - SUCCESSFUL"
            print("MAIN.py -- RELAOD COMPLETE")

    def reloading_inprogress(self, app):
        app.reload_status = "#7b9fba"
        app.reload_button_msg = "Reloading"

    def update_last_TAFs_reload_time(self, app,utc_now):
        # Loading LAST UPDATE TIME
        path = "Data_new/last_reload_time.json"
        with open(path) as f_obj:
            last_update_time = json.load(f_obj)
            # create DATETIME object from STRING of the following format
        last_update__object = datetime.datetime.strptime(last_update_time, "%H:%M'%S UTC  %d-%m-%Y")

        time_delta__object = utc_now - last_update__object

        time_delta_minutes = str(math.floor(time_delta__object.total_seconds() / 60))
        reload_TAFs_msg = f'Last reload  {last_update__object.strftime("%H:%M UTC ,%d-%m-%Y ")},  {fpf.min_to_hours_and_days(time_delta_minutes)} ago, {self.num_TAFs_downloaded} TAFs'

        if self.last_reload_failed:
            reload_TAFs_msg  = f'Reload FAILED. Last reload {fpf.min_to_hours_and_days(time_delta_minutes)} ago. {self.num_TAFs_downloaded} TAFs'
        return reload_TAFs_msg