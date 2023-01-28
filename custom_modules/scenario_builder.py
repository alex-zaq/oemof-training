from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from custom_modules.helpers import set_label
from custom_modules.specific_blocks import Specific_blocks, Turbine_T_factory
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
        self.custom_es.set_electricity_abs(electricity_demand)
######################################################################################################   
# Установка цены на природный газ
######################################################################################################  
    def set_natural_gas_price(self, usd_per_1000_m3):
        self.custom_es.add_natural_gas_source(usd_per_1000_m3)
######################################################################################################
# Выбор варинта детализации теплофикационных турбин типа Т
######################################################################################################       
    def set_turbine_T_modelling_type(self, modelling_type):
        'установка детализации турбин Т - simple или detail'
        self.custom_es.set_turbine_T_factory(modelling_type)
######################################################################################################   
# Настройки БелАЭС
######################################################################################################   

    def set_bel_npp_vver_1200_first_options(self, active_status, min_power_fraction, usd_per_Mwth = -999):
        if active_status not in [0 , 1] or min_power_fraction < 0 or min_power_fraction > 1 :
            raise Exception('Недопустимые параметры')
        self.custom_es.bel_npp_options['блок_1'] = bool(active_status)
        self.custom_es.bel_npp_options['блок_1_мин'] = min_power_fraction
        self.custom_es.bel_npp_options['блок_1_затраты'] = usd_per_Mwth
            
    
    def set_bel_npp_vver_1200_second_options(self, active_status, min_power_fraction, usd_per_Mwth = -999):
        if active_status not in [0 , 1] or min_power_fraction < 0 or min_power_fraction > 1 :
            raise Exception('Недопустимые параметры')
        self.custom_es.bel_npp_options['блок_2'] = bool(active_status)
        self.custom_es.bel_npp_options['блок_2_мин'] = min_power_fraction
        self.custom_es.bel_npp_options['блок_2_затраты'] = usd_per_Mwth
            
    
######################################################################################################   
# Изменение переменных затрат для газовых и электрокотлов
######################################################################################################       
    def set_el_boilers_hw_variable_cost(self, variable_costs):
        'установка переменных затрат для всех электрокотлов ГВС в энергосистеме'
        self.custom_es.el_boiler_hw_variable_cost = variable_costs
    
        
    def set_el_boilers_steam_variable_cost(self, variable_costs):
        'установка переменных затрат для всех электрокотлов ПАРА в энергосистеме'
        self.custom_es.el_boiler_steam_variable_cost = variable_costs
        
        
    def set_gas_boilers_hw_variable_cost(self, variable_costs):
        'установка переменных затрат для всех газовых котлов ГВС в энергосистеме'
        self.custom_es.gas_boiler_hw_variable_cost = variable_costs
    
        
    def set_gas_boilers_steam_variable_cost(self, variable_costs):
        'установка переменных затрат для всех газовых котлов ПАРА в энергосистеме'
        self.custom_es.gas_boiler_steam_variable_cost = variable_costs


    def set_el_boilers_hw_var_cost_by_station(self, station_name, variable_costs):
        self.custom_es.el_boiler_hw_var_cost[station_name] = variable_costs
    
    def set_el_boilers_steam_var_cost_by_station(self, station_name, variable_costs):
        self.custom_es.el_boiler_steam_var_cost[station_name] = variable_costs
    
    def set_gas_boilers_hw_var_cost_by_station(self, station_name, variable_costs):
        self.custom_es.gas_boiler_hw_var_cost[station_name] = variable_costs
    
    def set_gas_boilers_steam_var_cost_by_station(self, station_name, variable_costs):
        self.custom_es.gas_boiler_steam_var_cost[station_name] = variable_costs
        
    def set_station_variable_cost_by_dict(self, data_dict):
        'установка переменных затрат для всех блоков станции'
        self.custom_es.station_not_fuel_var_cost = data_dict
    
######################################################################################################   
# Удаление существующих источников
######################################################################################################   
    def remove_siemens(self):
        'удалить из энергосистемы энергоисточники siemens'
        self.custom_es.allow_siemens = False
        return self
    
    def reduce_block_station_power_to_minimum(self):
        'удалить блок-станции без технологических ограничений'
        self.custom_es.reduce_block_station_power = True
        return self
    
    def remove_renewables(self):
        'удалить существующих ВИЭ всех видов'
        self.custom_es.allow_renewables = False
        return self
    
    def apply_BelEnergo_retirement_until_2025(self):
        'применить план вывода из эксплуатации Белэнерго до 2025 года'
        return self
    
    def reduce_small_chp_demand_by_part(self, part):
        'уменьшить мощность малых тэц (например part = 0.2 - на 20 %)'
        self.custom_es.small_chp_demand_reduced_part = part
        return self
    
    def disable_all_exist_turb_by_station_name (self, station_name):
        self.custom_es.station_all_turb_avail[station_name] = False
        return self
    
    def disable_all_exist_turb(self):
        stations = self.custom_es.station_all_turb_avail.keys()
        for station in stations:
            self.custom_es.station_all_turb_avail[station]= False
        return self
    
    
    def disable_el_boiler_hw_by_station_name(self, station_name):
        self.custom_es.station_el_hw_on[station_name] = False
        
    def disable_el_boiler_steam_by_station_name(self, station_name):
        self.custom_es.station_el_steam_on[station_name] = False
        pass
    
    
    def disable_el_boiler_hw(self):
        stations = self.custom_es.station_el_hw_on.keys()
        for station in stations:
            self.custom_es.station_el_hw_on[station] = False
        
    
    def disable_el_boiler_steam(self):
        stations = self.custom_es.station_el_steam_on.keys()
        for station in stations:
            self.custom_es.station_el_steam_on[station] = False
    
    def disable_el_boiler_all_types(self):
        self.disable_el_boiler_hw()
        self.disable_el_boiler_steam()
    
    
    def enable_gas_boiler_hw_by_station_name(self, station_name):
        self.custom_es.station_gas_hw_on[station_name] = True
    
    def enable_gas_boiler_steam_by_station_name(self, station_name):
        self.custom_es.station_gas_steam_on[station_name] = True
    
    def enable_gas_boiler_hw(self):
        stations = self.custom_es.station_gas_hw_on.keys()
        for station in stations:
            self.custom_es.station_gas_hw_on[station] = False
            
    def enable_gas_boiler_steam(self):
        stations = self.custom_es.station_gas_steam_on.keys()
        for station in stations:
            self.custom_es.station_gas_steam_on[station] = False
    
    
    def enable_gas_boilers_all_types(self):
        self.enable_gas_boiler_hw()
        self.enable_gas_boiler_steam()
    
        
    def prohibit_steam_demand_chp_turb_by_station_name(self, station_name):
        'запретить покрытия паровой нагрузки теплофикационными турбинами для указанной станции'
        self.custom_es.station_hw_chp_demand_prohibited[station_name] = True
        return self
        
    def prohibit_hw_demand_chp_turb_by_station_name(self, station_name):
        'запретить покрытия отопительной нагрузки теплофикационными турбинами для указанной станции'
        self.custom_es.station_steam_chp_demand_prohibited[station_name] = True
        return self


    def prohibit_steam_demand_chp_turbs(self):
        'запретить покрытия паровой нагрузки теплофикационными турбинами'
        stations = self.custom_es.station_steam_chp_demand_prohibited.keys()
        for station in stations:
            self.custom_es.station_steam_chp_demand_prohibited[station]= True
        return self
        

    def prohibit_hw_demand_chp_turbs(self):
        'запретить покрытия отопительной нагрузки теплофикационными турбинами'
        stations = self.custom_es.station_hw_chp_demand_prohibited.keys()
        for station in stations:
            self.custom_es.station_hw_chp_demand_prohibited[station]= True
        return self
    
    def reduced_demand_boiler_district_by_part(self, part):
        self.custom_es.gas_boiler_hw_demand_reduced_part = part    
    
    def reduced_demand_boiler_district_Belenergo_by_part(self, part):
        self.custom_es.gas_boiler_steam_Belenergo_demand_reduced_part = part
    
 ######################################################################################################   
 # общая группа с ограниечениями
 ######################################################################################################   
    def add_constraint_for_el_boiler_group(self, group_name, upper_el_boiler_hw_power):
        self.custom_es.add_general_el_boiler_hw_constraint(group_name, upper_el_boiler_hw_power) 
        if not hasattr(self.custom_es, 'el_boiler_groups'):
            self.custom_es.el_boiler_groups = {}
        self.custom_es.el_boiler_groups[group_name] = group_name
        return self


 ######################################################################################################   
 # Добавление новых источников
 ######################################################################################################   
    def add_inifinity_el_boilers_hw_for_all_large_chp(self):
        'добавить бесконечное количество электрокотлов ГВС на все КРУПНЫЕ ТЭЦ с ГВС Белэнерго'
        stations = self.custom_es.el_boiler_hw_infinity.keys()
        for station in stations:
            self.custom_es.el_boiler_hw_infinity[station] = True
        return self

    def add_inifinity_el_boilers_steam_for_all_large_chp(self):
        'добавить бесконечное количество электрокотлов ПАРА на все КРУПНЫЕ ТЭЦ с паром Белэнерго'
        stations = self.custom_es.el_boiler_steam_infinity.keys()
        for station in stations:
            self.custom_es.el_boiler_steam_infinity[station] = True
        return self
    
    def add_inifinity_gas_boilers_hw_for_all_large_chp(self):
        'добавить бесконечное количество газовых котлов ГВС на все КРУПНЫЕ ТЭЦ с ГВС Белэнерго'
        stations = self.custom_es.gas_boiler_hw_infinity.keys()
        for station in stations:
            self.custom_es.gas_boiler_hw_infinity[station] = True
        return self

    def add_inifinity_gas_boilers_steam_for_all_large_chp(self):
        'добавить бесконечное количество газовых котлов ПАРА на все КРУПНЫЕ ТЭЦ с паром Белэнерго'
        stations = self.custom_es.gas_boiler_steam_infinity.keys()
        for station in stations:
            self.custom_es.gas_boiler_steam_infinity[station] = True
        return self
    
           
    
    def add_inifinity_el_boilers_hw_by_station(self, station_name):
        self.custom_es.el_boiler_hw_infinity[station_name] = True
        return self
    
        
    def add_inifinity_gas_boilers_hw_by_station(self, station_name):
        self.custom_es.gas_boiler_hw_infinity[station_name] = True
        
     
     
    def add_inifinity_gas_boilers_steam_by_station(self, station_name):
        self.custom_es.gas_boiler_steam_infinity[station_name] = True
    
      
 
    def add_ocgt_125(self, count):
        'добавить гту-122'
        self.custom_es.new_ocgt_count_options['гту-25'] = count
        return self    
    
    def add_ocgt_100(self, count):
        'добавить гту-100'
        self.custom_es.new_ocgt_count_options['гту-100'] = count
        return self
        
    def add_ocgt_25(self, count):
        'добавить гту-125'
        self.custom_es.new_ocgt_count_options['гту-125'] = count
        return self
    
    def add_vver_toi_1255(self, min_power_fraction, usd_per_Mwth = -9999 ):
        'добавить ввэр-тои с устновкой себестоимости и возможностью маневренирования'
        self.custom_es.new_npp_scenario_options['ввэр_тои'] = True
        self.custom_es.new_npp_scenario_options['ввэр_тои_мин'] = min_power_fraction
        self.custom_es.new_npp_scenario_options['ввэр_тои_затраты'] = usd_per_Mwth
        return self
    
    def add_vver_600(self, min_power_fraction, usd_per_Mwth = -9999):
        'добавить ввэр-600 с устновкой себестоимости и возможностью маневренирования'
        self.custom_es.new_npp_scenario_options['ввэр-600'] = True
        self.custom_es.new_npp_scenario_options['ввэр_600_мин'] = min_power_fraction
        self.custom_es.new_npp_scenario_options['ввэр_600_затраты'] = usd_per_Mwth
        return self

    def add_ritm_200(self, min_power_fraction, usd_per_Mwth = -9999 ):
        'добавить ритм-200 с устновкой себестоимости и возможностью маневренирования'
        self.custom_es.new_npp_scenario_options['ритм-200'] = True
        self.custom_es.new_npp_scenario_options['ритм-200_мин'] = min_power_fraction
        self.custom_es.new_npp_scenario_options['ритм-200_затраты'] = usd_per_Mwth
        return self
    
    def add_storage(self):
        'добавить аккумулятор'
        return self
 ######################################################################################################   
 # Добавление новых спросов
 ###################################################################################################### 
    def add_district_boilers_demand(self):
        'добавить спрос тепла котельных ЖКХ'
        pass