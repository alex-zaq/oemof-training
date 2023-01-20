from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from custom_modules.helpers import set_label
from custom_modules.specific_blocks import Specific_blocks
from custom_modules.generic_blocks import Generic_sinks, Generic_buses
from custom_modules.helpers import Custom_counter, set_label
from functools import reduce



class Scenario_builder:
    def __init__(self, custom_es) -> None:
        self.custom_es = custom_es
    
    def set_electricity_level(self,energy_level_in_billion_kWth):
        self.custom_es.set_electricity_level(energy_level_in_billion_kWth)


    def set_electricity_profile(self, elictricity_profile):
        self.custom_es.set_electricity_profile(elictricity_profile)

    def set_natural_gas_price(self, usd_per_1000_m3):
        self.custom_es.add_natural_gas_source(usd_per_1000_m3)
    
    def remove_siemens(self):
        self.custom_es.allowSiemens = False
    
    def reduce_block_station_power_to_minimum(self):
        self.custom_es.reduce_block_station_power = True
    
    def remove_renewables(self):
        self.custom_es.allowRenewables = False
    
    def remove_turb_steam(self):
        # +++++++++
        return self
    
    def add_inifinity_el_boilers_hw_for_all_chp(self):
        # +++++++++
        return self
        
    def add_inifinity_el_boilers_steam_for_all_chp(self):
        # +++++++++
        return self
    
    def add_cheap_steam_boilers(self):
        # +++++++++
        return self
    
    def remove_all_chp_blocks(self):
        # +++++++++
        return self
    
    def remove_block_by_station(self):
        return self
    
    def add_ocgt_122(self):
        # +++++++++
        return self
    
    def displace_heat_boilers_by_power(self, power):
        return self
    
    def add_vver_toi_1255(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        # +++++++++
        return self
    
    def add_vver_600(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        # +++++++++
        return self

    def change_bel_npp_options(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        # +++++++++
        return self
    
    def add_ritm_200(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        # +++++++++
        return self
    
    def add_storage(self):
        return self