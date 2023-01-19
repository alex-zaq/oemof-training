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
    
    def set_electricity_level(self, profile, level_in_billion_kWth):
        # +++++++++
        return self

    def set_natural_gas_price(self, usd_per_1000_m3):
        # +++++++++
        return self
    
    def remove_siemens(self):
        # +++++++++
        return self
    
    def reduce_block_station_power_to_minimum(self):
        # +++++++++
        return self
    
    def remove_renewables(self):
        # +++++++++
        return self
    
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
    
    def add_vver_toi_1255(self, allow_power_variability = False):
        # +++++++++
        return self
    
    def add_vver_600(self, allow_power_variability = False):
        # +++++++++
        return self

    def allow_bel_npp_power_changes(self):
        # +++++++++
        return self
    
    def add_ritm_200(self, allow_power_variability = False):
        # +++++++++
        return self
    
    def add_storage(self):
        return self