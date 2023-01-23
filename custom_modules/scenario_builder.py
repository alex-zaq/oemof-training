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
    
    
######################################################################################################   
# Установка параметров электропотребления
######################################################################################################   
    def set_electricity_level(self,energy_level_in_billion_kWth):
        "установка уровня электропотребления в млрд. кВтч"
        self.custom_es.set_electricity_level(energy_level_in_billion_kWth)


    def set_electricity_profile(self, elictricity_profile):
        "установка профиля электрической нагрузки в относительном виде"
        self.custom_es.set_electricity_profile(elictricity_profile)


    def set_electricity_demand_abs(self, electricity_demand):
        "установка элетктрической нагрузки в абсолютном виде (МВт)"
        pass
######################################################################################################   
# Установка цены на природный газ
######################################################################################################  
    def set_natural_gas_price(self, usd_per_1000_m3):
        self.custom_es.add_natural_gas_source(usd_per_1000_m3)
######################################################################################################
# Выбор варинта детализации теплофикационных турбин типа Т
######################################################################################################       
    def set_turbine_T_modelling_type(type):
        'установка детализации турбин Т - simple или detail'
        pass
######################################################################################################   
# Добавление проектного маневрирования для двух блоков БелАЭС
######################################################################################################   
    def set_bel_npp_options(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        'установка себестоимости и возможности маневрирования для двух блоков БелАЭС'        
        # +++++++++
        return self
######################################################################################################   
# Изменение переменных затрат для газовых и электрокотлов
######################################################################################################       
    def set_el_boilers_hw_variable_cost(self):
        'установка переменных затрат для всех электрокотлов ГВС в энергосистеме'
        pass
    
        
    def set_el_boilers_steam_variable_cost(self):
        'установка переменных затрат для всех электрокотлов ПАРА в энергосистеме'
        pass
        
        
    def set_gas_boilers_hw_variable_cost(self):
        'установка переменных затрат для всех газовых котлов ГВС в энергосистеме'
        pass
    
        
    def set_gas_boilers_steam_variable_cost(self):
        'установка переменных затрат для всех газовых котлов ПАРА в энергосистеме'
        pass
    
    
    def set_station_variable_cost_by_station_name(self, station_name, value):
        'установка переменных затрат для всех блоков станции'
        pass
    
######################################################################################################   
# Удаление существующих источников
######################################################################################################   
    def remove_siemens(self):
        'удалить из энергосистемы энергоисточники siemens'
        self.custom_es.allowSiemens = False
    
    def reduce_block_station_power_to_minimum(self):
        'удалить блок-станции без технологических ограничений'
        self.custom_es.reduce_block_station_power = True
    
    def remove_renewables(self):
        'удалить существующих ВИЭ всех видов'
        self.custom_es.allowRenewables = False
    
    def apply_BelEnergo_retirement_until_2025(self):
        'применить план вывода из эксплуатации Белэнерго до 2025 года'
        pass
    
    def reduce_small_chp_power_by_part(self, part):
        'уменьшить мощность малых тэц (например part = 0.2 - на 20 %)'
        pass
    
    def remove_all_turb_steam_demand_large_chp(self):
        'удалить все теплофикационные турбины для технологического пара'
        # +++++++++
        return self
        
    def remove_all_turb_hw_demand_large_chp(self):
        'удалить все теплофикационные турбин гвс'
        # +++++++++
        return self
    
    def remove_boiler_district_by_part(self, part):
        pass
    
    def remove_boiler_district_Belenergo_by_part(self, part):
        pass
    
 ######################################################################################################   
 # Добавление новых источников
 ######################################################################################################   
    def add_inifinity_el_boilers_hw_for_all_large_chp(self):
        'добавить бесконечное количество электрокотлов ГВС на все КРУПНЫЕ ТЭЦ с ГВС Белэнерго'
        # +++++++++
        return self

    def add_inifinity_el_boilers_steam_for_all_large_chp(self):
        'добавить бесконечное количество электрокотлов ПАРА на все КРУПНЫЕ ТЭЦ с паром Белэнерго'
        # +++++++++
        return self
    
    def add_inifinity_gas_boilers_hw_for_all_large_chp(self):
        'добавить бесконечное количество газовых котлов ГВС на все КРУПНЫЕ ТЭЦ с ГВС Белэнерго'
        # +++++++++
        return self

    def add_inifinity_gas_boilers_steam_for_all_large_chp(self):
        'добавить бесконечное количество газовых котлов ПАРА на все КРУПНЫЕ ТЭЦ с паром Белэнерго'
        # +++++++++
        return self
    
    def add_inifinity_el_boilers_hw_for_all_small_chp(self):
        'добавить бесконечное количество электрокотлов ГВС на все МАЛЫЕ ТЭЦ с ГВС Белэнерго'
        # +++++++++
        return self
        
    def add_inifinity_gas_boilers_hw_for_all_small_chp(self):
        'добавить бесконечное количество электрокотлов ГВС на все МАЛЫЕ ТЭЦ с ГВС Белэнерго'
        # +++++++++
        return self
            
    def add_inifinity_el_boilers_hw_for_district_boiler(self):
        'добавить бесконечное количество электрокотлов ГВС для  КОТЕЛЬНЫХ жкх'
        # +++++++++
        return self
                    
    def add_inifinity_el_boilers_hw_for_Belenergo_district_boiler(self):
        'добавить бесконечное количество электрокотлов ГВС для  КОТЕЛЬНЫХ Белэнерго'
        # +++++++++
        return self
     
 
    def add_ocgt_122(self):
        'добавить гту-122'
        # +++++++++
        return self    
    
    def add_ocgt_100(self):
        'добавить гту-100'
        # +++++++++
        return self
        
    def add_ocgt_25(self):
        'добавить гту-25'
        # +++++++++
        return self
    
    def add_vver_toi_1255(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        'добавить ввэр-тои с устновкой себестоимости и возможностью маневренирования'
        # +++++++++
        return self
    
    def add_vver_600(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        'добавить ввэр-600 с устновкой себестоимости и возможностью маневренирования'
        # +++++++++
        return self

    def add_ritm_200(self, allow_power_variability = False, usd_per_Mwth = -9999 ):
        'добавить ритм-200 с устновкой себестоимости и возможностью маневренирования'
        # +++++++++
        return self
    
    def add_storage(self):
        'добавить аккумулятор'
        return self
######################################################################################################