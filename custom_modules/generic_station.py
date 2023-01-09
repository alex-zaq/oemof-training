from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from custom_modules.helpers import set_label


class Generic_station:
    
    def __init__(self, station_name) -> None:
        self.set_heat_water_demand = None
        pass
        
    def set_heat_water_demand(self, heat_water_demand_name):
        pass
     
    
    def set_steam_demand(self, steam_demand_name):
        pass
    
    
    def add_el_block(self, block):
        pass
        
    def add_el_block(self, block):
        pass
    
    
    
                # self.active_stations_data[station_name] = {
                # 'э-тэц-источник': el_turb,
                # 'гвс-тэц-источник': hw_chp_turb,
                # 'гвс-кот-источник': hw_gas_boilers,
                # 'гвс-эк-источник': hw_el_boilers,
                # 'пар-тэц-источник': steam_chp_turb,
                # 'пар-кот-источник': steam_gas_boilers,
                # 'пар-эк-источник': steam_el_boilers,
                # 'гвс-поток': hw_bus, 
                # 'пар-поток': steam_bus,
                # 'гвс-потребитель': hw_sink,
                # 'пар-потребитель': steam_sink
                # }  