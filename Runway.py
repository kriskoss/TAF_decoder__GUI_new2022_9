########### ADDING CLASSED (2023.04.09) ##############
class Runway:
    def __init__(self,
                 _length__meters,
                 _width__meters,
                 _le_ident,
                 _le_heading_degT,
                 _le_displaced_threshold__meters,
                 _le_latitude_deg,
                 _le_longitude_deg,
                 _he_ident,
                 _he_heading_degT,
                 _he_displaced_threshold__meters,
                 _he_latitude_deg,
                 _he_longitude_deg
                 ):
        self.length__meters = _length__meters
        self.width__meters = _width__meters
        self.le_ident = _le_ident
        self.le_heading_degT = _le_heading_degT
        self.le_displaced_threshold__meters = _le_displaced_threshold__meters
        self.le_latitude_deg = _le_latitude_deg
        self.le_longitude_deg = _le_longitude_deg
        self.he_ident = _he_ident
        self.he_heading_degT = _he_heading_degT
        self.he_displaced_threshold__meters = _he_displaced_threshold__meters
        self.he_latitude_deg = _he_latitude_deg
        self.he_longitude_deg = _he_longitude_deg
