import json
from Classes.settings import Settings

filename = Settings.g_groups_apts_db_path()
# filename ='C:/Users/krzys/Dropbox/_DATABASE/TAF_app/g_groups_apts_db.json'  # REMOTE STORAGE
with open(filename) as f:
    apts = json.load(f)

new_apts ={}
for k,v in apts.items():
    k = str(k[0]).lower() +str(k[1:5])
    new_v=[]
    for apt in v:
        apt = apt.upper()
        new_v.append(apt)
    new_apts[str(k)] = new_v

print(new_apts)


