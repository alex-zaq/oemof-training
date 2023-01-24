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
from custom_modules.helpers import get_peak_load_by_energy_2020, get_peak_load_by_energy_2021
from functools import reduce



class Specific_stations:
  
        def __init__(self, es, global_input_bus, global_output_bus):
            self.es = es
            self.__global_id = 0
            self.__block_collection = []
            self.global_input_bus = global_input_bus
            self.global_output_bus = global_output_bus
            self.gobal_elictricity_sink = None
            self.global_gas_source = None
            self.block_creator = Specific_blocks(es, global_input_bus, global_output_bus, 9999)
            self.turbine_T_factory = Turbine_T_factory(self.block_creator, 'simple')
            self.sink_creator = Generic_sinks(es)
            self.bus_creator = Generic_buses(es)
            self.active_stations_data = {}


            self.station_not_fuel_var_cost = {
                'Лукомольская ГРЭС' : 0,
                'Березовская ГРЭС' : 0,
                'Минская ТЭЦ-5' : 0,
                'Минская ТЭЦ-3' : 0,
                'Минская ТЭЦ-4' : 0,
                'Светлогорская ТЭЦ' : 0,
                'Новополоцкая ТЭЦ' : 0,
                'Могилевская ТЭЦ-2' : 0,
                'Бобруйская ТЭЦ-2' : 0,
                'Гродненская ТЭЦ-2' : 0,
                'Мозырская ТЭЦ-2' : 0,
                'Гомельская ТЭЦ' : 0,
                'Малые ТЭЦ' : 0,
                'ВИЭ' : 0,
                'Блок-станции' : 0,
            }

            self.el_boiler_variable_cost = {
                'гвс': 0,
                'пар': 0,
            }
            
            
            self.gas_boiler_variable_cost = {
                'гвс': 0,
                'пар': 0,
            }
            
            
            self.infinity_el_boilers_large_chp = {
                'гвс': False,
                'пар': False,
            }                        
            
            self.infinity_gas_boilers_large_chp = {
                'гвс': False,
                'пар': False,
            }                        
            
            self.infinity_el_boilers_small_chp = {
                'гвс': False,
            }                        
            
            self.infinity_gas_boilers_small_chp = {
                'гвс': False,
            }                        

            self.infinity_el_boilers_discrict_boilers = {
                'гвс' : False
            }

            self.infinity_el_boilers_Belenergo_district_boilers = {
                'гвс': False,
                'пар': False,
            }

            self.new_ocgt_count_options = {
                'гту-25': 0,
                'гту-100': 0,
                'гту-125': 0
            }


            self.bel_npp_options = {
                'блок_1': True,
                'блок_2': True,
                'блок_1_мин': 0.75,
                'блок_2_мин': 0.75,
                'блок_1_затраты': -999,
                'блок_2_затраты': -999
                
            }

            self.new_npp_scenario_options = {
                'ввэр_тои': True,
                'ввэр-600': True,
                'ритм-200': 0,
                'ввэр_тои_мин': 0.75,
                'ввэр-600_мин': 0.70,
                'ритм-200_мин': 0.65,
                'ввэр_тои_затраты': -999,
                'ввэр-600_затраты': -999,
                'ритм-200_затраты': -999
            }
                

            self.retirement_options = {
                'блок-станции_без_тех_огр' : True,
                'siemens': True,
                'виэ': True,
                'план вывода Белэнерго': True,
                'пар_крупные_тэц_ПТ' : True,
                'пар_крупные_тэц_Р' : True,
                'малые тэц_откл_часть' : 0,
                'гвс_коте_Белэнерго_откл_часть' : 0,
                'пар_кот_Белэнерго_откл_часть' : 0,
                'гвс_кот_жкх_откл_часть' : 0,
                
            }

            
            
        def set_start_up_options(self, start_up_cost, shout_down_cost, maximum_startups, maximum_shutdowns, initial_status):
            
            options = {
                'start_up_cost': start_up_cost,
                'shout_down_cost': shout_down_cost,
                'maximum_startups': maximum_startups,
                'maximum_shutdowns': maximum_shutdowns,
                'initial_status': initial_status,
            }
            
            self.block_creator = Specific_blocks(self.es, self.global_input_bus, self.global_output_bus, options)
            # self.turbine_T_factory = Turbine_T_factory(self.block_creator, 'detail')
            
            
        def set_turbine_T_factory(self, modelling_type):
            if modelling_type not in ['simple','detail']:
                raise Exception('Не выбран корректный тип представления турбин типа1 Т')
            self.turbine_T_factory = Turbine_T_factory(self.block_creator, modelling_type)
            
        
        
        def set_electricity_profile(self, profile):
            self.profile = profile
            
            
        def set_electricity_level(self, level_in_billion_kWth):
            if self.profile.empty:
                raise Exception('Не установлен профиль электрической нагрузки')
            self.gobal_elictricity_sink = self.sink_creator.create_sink_fraction_demand(
                'электричество_потребитель',
                self.global_output_bus,
                demand_profile = self.profile,
                peak_load= get_peak_load_by_energy_2021(level_in_billion_kWth)
            )
            
            
        def set_electricity_abs(self, demand_absolute_data):
            if not self.profile.empty:
                raise Exception('Недопустимые параметры')
            self.gobal_elictricity_sink = self.sink_creator.create_sink_absolute_demand(
                'электричество_потребитель',
                self.global_output_bus,
                demand_absolute_data = demand_absolute_data 
            )
            
                
            
			
        def inc_global_id(self):
            self.__global_id +=1
            return self.__global_id 
   
        
        def get_block_collection(self):
            return self.__block_collection        
        def get_block_creator(self):
            return self.__block_creater


        def get_global_input_flow(self):
            return self.global_input_bus

               
        def get_global_output_flow(self):
            return self.global_output_bus


        def get_heat_water_bus_by_station(self, station_name):
            return self.active_stations_data[station_name]['потоки']['гвс-поток']
        
        def get_steam_bus_by_station(self, station_name):
            return self.active_stations_data[station_name]['потоки']['пар-поток']
        
                
        def get_install_power_blocklist(self, block_list):
            'возвращает установленную мощность списка блоков'
            if block_list:
                return sum([x.group_options['nominal_value'] for x in block_list])
                
                
        def get_station_el_install_power(self):
            'возращает полную установленную мощность'
            install_power = 0
            for station_name, _ in self.active_stations_data:
                res += self.active_stations_data[station_name]['установленная мощность']
      

        # def set_block_type_station_type(self, data):
        #     'устанавливает приоритет типов блоков в указанных типах станциях'
        #     station_types = data.keys()
        #     order_dict = { station_type: order for order, station_type in enumerate(station_types) }

            

        #     for station_type in station_types:
        #         order_dict = { block_type: order for order,block_type in enumerate(data[station_type])}
        #         for block_type, order in order_dict.items():
        #             blocks = self.get_all_blocks_by_block_type(block_type)
        #             for block in blocks:
        #                 block.group_options['block_order'] = order
            
        

        def set_station_type_with_order(self, data):
            'устанавливает тип станции для группы станций'
            'data = {ТЭЦ: [Минская ТЭЦ-4, Минская ТЭЦ-3]  }'
            
            
            station_types = data.keys()
            for station_type in station_types:
                for station_name in data[station_type]:
                    blocks = self.get_all_blocks_by_station(station_name)
                    for block in blocks:
                        block.group_options['station_type'] = station_type
            
            order_dict = {station_type: order for order, station_type in enumerate(station_types)}
            for station_type, order in order_dict.items():
                blocks = self.get_all_blocks_by_station_type(station_type)
                for block in blocks:
                    block.group_options['station_type_order'] = order
                

        def set_block_type_in_station_order(self, data):
            'устанавливает порядок отображения типов блока для указанной станции'
            'Пример: data = {Минская ТЭЦ-4:[ПТ,Т], ...}'
            
            stations = data.keys()
            
            order_dict = { station_name: order for order,station_name in enumerate(stations) }
            for station_name, order in order_dict.items():
                station_blocks = self.get_all_blocks_by_station(station_name)
                for block in station_blocks:
                    block.group_options['station_order'] = order
                                   
                    
            for station in stations:
                order_dict = { block_type: order for order,block_type in enumerate(data[station])}
                for block_type, order in order_dict.items():
                    blocks = self.get_all_block_by_station_name_block_type(station, block_type)
                    for block in blocks:
                        block.group_options['block_type_order'] = order

                
        def set_block_type_in_station_type(self, data):
            'устаналивает порядок типа блока в пределах типа станции'
            'data = {ТЭЦ: [ПТ, Т], ...}'

            station_types = data.keys()
            for station_type in station_types:
                order_dict = { block_type: order for order,block_type in enumerate(data[station_type])}
                for block_type, order in order_dict.items():
                    blocks = self.get_all_blocks_by_block_type(block_type)
                    for block in blocks:
                        block.group_options['block_type_order'] = order
                            
        

 ##############################################################################
        def set_heat_water_groupname_all_stations(self, hw_group_name):
            'устанавливает название группы все источников гвс'
            hw_all_blocks = self.get_all_heat_water_blocks()
            for block in hw_all_blocks:
                block.group_options['heat_demand_type'] = hw_group_name
 
        def set_steam_groupname_all_stations(self, steam_group_name):
            'устанавливает название группы для всех источников пара'
            hw_all_blocks = self.get_all_steam_blocks()
            for block in hw_all_blocks:
                block.group_options['heat_demand_type'] = steam_group_name
###############################################################################

        
        def get_all_blocks_by_station(self, station_name):
            'получить все блоки все видов для указанной станции'
            res = []
            el_blocks = self.get_el_blocks_by_station(station_name)
            hw_blocks = self.get_heat_water_blocks_by_station(station_name)
            steam_blocks = self.get_steam_blocks_by_station(station_name)
            if el_blocks:
                res.extend(el_blocks)
            if hw_blocks:
                res.extend(hw_blocks)
            if steam_blocks:
                res.extend(steam_blocks)
            return res
        
        
        def get_all_el_blocks(self):
            'получить все блоки(электроэнергия) все станции '
            res = []
            for station_name, _ in self.active_stations_data.items():
                res += self.get_el_blocks_by_station(station_name)
            return res
                
                
        def get_all_blocks(self):
            'получить все блоки всех видов со всех станций'
            res = []
            for station_name, _ in self.active_stations_data.items():
                  res += self.get_all_blocks_by_station(station_name)
            return res
           
   
        def get_el_blocks_by_station(self, station_name):
            'получить все блоки(электроэнергия) для указанной станции'
            return self.active_stations_data[station_name]['источники']['э-источники']
      
        def get_heat_water_blocks_by_station(self, station_name):
            'получить все блоки(гвс) для указанной станции'
            res = []
            hw_blocks_dict = self.active_stations_data[station_name]['источники']['гвс-источники']
            for part, data in hw_blocks_dict.items():
                if isinstance(data, list):
                   res.extend(data)
                elif data:
                    res.append(data)
            return res
               
              
        def get_steam_blocks_by_station(self, station_name):
            'получить все блоки(пар) для указанной станции'
            res = []
            hw_blocks_dict = self.active_stations_data[station_name]['источники']['пар-источники']
            for _ , data in hw_blocks_dict.items():
                if isinstance(data, list):
                   res.extend(data)
                elif data:
                    res.append(data)
            return res
                
        
        def get_all_heat_water_blocks(self):
            'получить все блоки гвс энергосистемы'
            res = []
            for station_name, _ in self.active_stations_data.items():
                res += self.get_heat_water_blocks_by_station(station_name)
            return res
                
        
        def get_all_steam_blocks(self):
            'получить все блоки пара энергосистемы'
            res = []
            for station_name, _ in self.active_stations_data.items():
                res += self.get_steam_blocks_by_station(station_name)
            return res

        def get_all_blocks_by_station_type(self, station_type):
            'получить блоки всех видов для указанной станции'
            res = []
            all_blocks = self.get_all_blocks()
            for block in all_blocks:
                if block.group_options['station_type'] == station_type:
                   res.append(block) 
            return res
        
        
        def get_all_blocks_by_block_type(self, block_type):
            'получить все блоки указанного типа'
            res = []
            all_blocks = self.get_all_blocks()
            for block in all_blocks:
                if block.group_options['block_type'] == block_type:
                   res.append(block) 
            return res
              
        def get_all_block_by_station_name_block_type(self, station_name, block_type):
            station_blocks = self.get_all_blocks_by_station(station_name)
            res = []
            for block in station_blocks:
                if block.group_options['block_type'] == block_type:
                    res.append(block)
            return res
            
              
                
        def set_station_order(self, order_list):
            'устанавливает порядок отображения отдельных станции'
            order_dict = { station_name: order for order,station_name in enumerate(order_list) }
            for station_name, order in order_dict.items():
                station_blocks = self.get_all_blocks_by_station(station_name)
                for block in station_blocks:
                    block.group_options['station_order'] = order
        
        
        def set_station_type_order(self, station_type_order_list):
            'устанавливает порядок отображения типов станций'
            order_dict = { station_type: order for order,station_type in enumerate(station_type_order_list) }
            for station_type, order in order_dict:
               station_blocks = self.get_all_blocks_by_station_type(station_type)
            for block in station_blocks:
               block.group_options['station_order'] = order


        def set_block_type_order(self, block_order_list):
            'устанавливает порядок отображения типов блоков'
            order_dict = { block_type: order for order,block_type in enumerate(block_order_list) }
            for block_type, order in order_dict:
               block_by_type = self.get_all_blocks_by_block_type(block_type)
            for block in block_by_type:
               block.group_options['block_order'] = order


        def filter_block_list_by_group_options_attr(self, block_lst, attr_name, attr_value):
            res = []
            if block_lst:
                for block in block_lst:
                    if block.group_options.get(attr_name) is not None:
                        if block.group_options[attr_name] == attr_value:
                            res.append(block)
            return res
            


# ТЭЦ-5 энергоблок ст. №1	
# Березовская ГРЭС энергоблоки ст. №3,4,5	
# Лукомльская ГРЭС энергоблоки ст. №1-8		

# Минская ТЭЦ-3	
# Минская ТЭЦ-4		
# Светлогорская ТЭЦ		
# Новополоцкая ТЭЦ	
# Могилевская ТЭЦ-2		
# Бобруйская  ТЭЦ-2	
# Гродненская   ТЭЦ-2	
# Мозырская   ТЭЦ-2	
# Гомельская  ТЭЦ-2	

        # +

        def add_Minskay_tec_5(self):
            station_name = 'Минская ТЭЦ-5'
            block_creator = self.block_creator
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            # ТК-330-240-3М
            # M701F  (270)
            # TC2F  (129.6)
            # турбины	719.6	МВт	
            # в/о котлы	100	Гкал/час	
            ###############################################################
            tk_330_1 = block_creator.get_tk_330(global_id(), local_id(), station_name, 0)
            if self.allowSiemens:
                ccgt_399_1 = block_creator.get_ccgt_399(global_id(), local_id(), station_name, 0)
            # hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(), station_name, 100 * 1.163, hw_bus, 0)
            ###############################################################
            hw_bus = steam_bus = None
            hw_sink = steam_sink = None
            ###############################################################
            el_turb_no_siemens = [tk_330_1]
            el_turb_siemens = [ccgt_399_1] if self.allowSiemens else []
            el_turb = el_turb_no_siemens + el_turb_siemens
            hw_chp_turb = None
            hw_gas_boilers = None
            hw_el_boilers = None
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
            
        # +      
        def add_Berezovskay_gres(self):
            station_name = 'Березовская ГРЭС'
            block_creator = self.block_creator
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            # К-160-130 (165)
            # К-160-130-2ПР1 (165)
            # К-175/180-12,8 (180)
            # ГТЭ-25НГ80
            # ГТЭ-25НГ80
            # SGT-700 (29.06)
            # SGT5-4000F (285,87)
            # LZN140-12,78/2,937/ 0,391  (141,13)
            # В/о ЭК	25.8	Гкал/час
            # турбины	1095.12	МВт
            ###############################################################
            k_160_1 = block_creator.get_k_160(global_id(), local_id(), station_name, 0.01)
            k_160_2 = block_creator.get_k_160(global_id(), local_id(), station_name, 0.03)
            k_175_1 = block_creator.get_k_175(global_id(), local_id(), station_name, 0)
            ocgt_25_1 = block_creator.get_ocgt_25(global_id(), local_id(), station_name, 0.01)
            ocgt_25_2 = block_creator.get_ocgt_25(global_id(), local_id(), station_name, 0.02)
            if self.allowSiemens:
                ccgt_427_1 = block_creator.get_ccgt_427(global_id(), local_id(), station_name, 0)
                ocgt_29_1 = block_creator.get_ocgt_29(global_id(), local_id(), station_name, 0)
            ###############################################################
            hw_bus = steam_bus = None
            hw_sink = steam_sink = None
            ###############################################################
            el_turb_no_siemens = [k_160_1, k_160_2, k_175_1, ocgt_25_1, ocgt_25_2]
            el_turb_siemens = [ccgt_427_1, ocgt_29_1] if self.allowSiemens else []
            el_turb = el_turb_no_siemens + el_turb_siemens
            hw_chp_turb = None
            hw_gas_boilers = None
            hw_el_boilers = None
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
  
        # + 
        def add_Lukomolskay_gres(self, heat_water_demand_data = None):
            station_name = 'Лукомольская ГРЭС'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            # steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = None
            # steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # турбоагрегаты, котлы и электрокотлы
            # К-300-240-6МР(315) # К-300-240-6МР(315) # К-300-240-6МР(315) # К-300-240-9МР(310) 
            # К-300-240-1 (300)   # К-300-240-1 (300)   # К-300-240-1 (300)   # К-300-240-1(300) 
            # SGT5-PAC 4000F- 286 МВт  N141-563/551 - 141 МВт
            # эк - 68.8 гкал/ч  пвк - нет
            ###############################################################
            k_315_1 = block_creator.get_k_315(global_id(), local_id(), station_name, 0.001)
            k_315_2 = block_creator.get_k_315(global_id(), local_id(), station_name, 0.002)
            k_315_3 = block_creator.get_k_315(global_id(), local_id(), station_name, 0.003)
            k_310_4 = block_creator.get_k_310(global_id(), local_id(), station_name, 0.004)
            k_300_5 = block_creator.get_k_300(global_id(), local_id(), station_name, 0.005)
            k_300_6 = block_creator.get_k_300(global_id(), local_id(), station_name, 0.006)
            k_300_7 = block_creator.get_k_300(global_id(), local_id(), station_name, 0.007)
            k_300_8 = block_creator.get_k_300(global_id(), local_id(), station_name, 0.008)
            if self.allowSiemens:
                ccgt_427_1 = block_creator.get_ccgt_427(global_id(), local_id(), station_name, 0)
            ###############################################################
            el_boilers_hw = None
            back_hw_gas_boilers = None
            # el_boilers_hw = block_creator.get_el_boilers(next(), station_name, 1.163 * 68.8, hw_bus, hw_name , 0)
            # фейковые дорогие источники тепла
            # back_hw_gas_boilers = block_creator.get_gas_boilers(next() ,station_name, 10_000, hw_bus, hw_name, 9999)
            # тепловые потребители - sink
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = None
            # steam_sink = create_sink_abs(label = set_label(
            # station_name, steam_name, 'потребитель'),
            # input_flow = steam_bus,
            # demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb_no_siemens = [k_315_1, k_315_2, k_315_3, k_310_4, k_300_5, k_300_6, k_300_7, k_300_8]
            el_turb_siemens = [ccgt_427_1] if self.allowSiemens else []
            el_turb = el_turb_no_siemens + el_turb_siemens
            hw_chp_turb = None
            hw_gas_boilers = back_hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
            
            
       # +      
        def add_Minskay_tec_3(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Минская ТЭЦ-3'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            turbine_T_factory = self.turbine_T_factory
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            global_id = self.inc_global_id
            local_id = counter.next
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # ПТ-60-130/13
            # ПТ-60-130/13
            # Т-100-130
            # GT 13E2
            # Т-53/67-8,0
            # турбины	442	МВт	
            # в/о котлы	940	Гкал/час	
            # В/о ЭК	86	Гкал/час	
            ###############################################################
            [pt_t_60_el_1, pt_p_60_1, pt_t_60_1] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus, 0.01)
            [pt_t_60_el_2, pt_p_60_2, pt_t_60_2] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus, 0.02)
            t_100_1 = turbine_T_factory.get_t_100(global_id(), local_id(), station_name, hw_bus, 0)
            # не сделано
            ccgt_chp_222 = block_creator.get_ccgt_сhp_222(global_id(), local_id(), station_name, steam_bus, hw_bus, 0.01)
            hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(), station_name, 940 * 1.163, hw_bus, 0)
            el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, 86 * 1.163, hw_bus, 0)
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb = [pt_t_60_el_1, pt_t_60_el_2, t_100_1, ccgt_chp_222]
            hw_chp_turb = [pt_t_60_1, pt_t_60_2, t_100_1, ccgt_chp_222]
            hw_gas_boilers = hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = [pt_p_60_1, pt_p_60_2]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
    
        # + 
        def add_Minskay_tec_4(self, heat_water_demand_data):
            # добавить паровую нагрзука для пт-60
            station_name = 'Минская ТЭЦ-4'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            turbine_T_factory = self.turbine_T_factory
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            global_id = self.inc_global_id
            local_id = counter.next
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            # steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # турбоагрегаты, котлы и электрокотлы
            # ПТ-60-130/13    # Т-110/120-130   # Т-110/120-130
            # Т-250/300-240-2 # Т-250/300-240-2 # Т-255/305-240-5
            # эк - 137 гкал/ч  пвк - нет
            # group_options = {'station_order': 0, 'station_type': 'ТЭЦ' }
            ###############################################################
            # плановые остановки могут определяться здесь
            ###############################################################
            # pt_t_60 = block_creator.get_pt_60_t(global_id(), local_id(), station_name, hw_bus) 
            [pt_t_60_el_1, pt_p_60_1, pt_t_60_1] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            t_250_1 = turbine_T_factory.get_t_250(global_id(), local_id(), station_name, hw_bus, 0.01) # 2
            t_250_2 = turbine_T_factory.get_t_250(global_id(), local_id(), station_name, hw_bus, 0.02) # 3
            t_255_1 = turbine_T_factory.get_t_250(global_id(), local_id(), station_name, hw_bus, 0.03) # 4
            t_110_1 = turbine_T_factory.get_t_110(global_id(), local_id(), station_name, hw_bus, 0.04)
            t_110_2 = turbine_T_factory.get_t_110(global_id(), local_id(), station_name, hw_bus, 0.05)
            el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, 1.163 * 137.6 * 10, hw_bus , 0)
            # фейковые дорогие источники тепла
            # back_hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 10_000, hw_bus, 9999)
            # back_steam_gas_boilers = block_creator.get_gas_boilers(next(),station_name, 10_000, hw_bus, 9999)
            # тепловые потребители - sink
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            # выяснить внутренние паровые нужды тэц-4
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = 120)
            ###############################################################
            el_turb = [pt_t_60_el_1, t_250_1, t_250_2, t_255_1, t_110_1, t_110_2]
            hw_chp_turb = [pt_t_60_1, t_250_1, t_250_2, t_255_1, t_110_1, t_110_2]
            hw_gas_boilers = None
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = [pt_p_60_1]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 

            return station_name
            
            
        # +       
        def add_Svetlogorskay_tec(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Cветлогорская ТЭЦ'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            turbine_T_factory = self.turbine_T_factory
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # Р-15-90/10 +
            # ТР-16-10
            # Т-14/25-10
            # ПТ-60-130/13 +
            # Р-50-130-1ПР1 +
            # турбины	155	МВт
            ###############################################################
            p_50_1 = block_creator.get_p_50(global_id(), local_id(), station_name, steam_bus)
            [pt_t_60_el_1, pt_p_60_1, pt_t_60_1] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            р_15_1 = block_creator.get_p_15(global_id(), local_id(), station_name, steam_bus)
            [tr_16_el_1, tr_16_p_1, tr_16_t_1] = block_creator.get_tp_16(global_id(), local_id(), station_name, steam_bus, hw_bus)
            t_14_1 = turbine_T_factory.get_t_14(global_id(), local_id(), station_name, hw_bus)
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb = [p_50_1, pt_t_60_el_1, р_15_1, tr_16_el_1, t_14_1]
            hw_chp_turb = [pt_t_60_1, tr_16_t_1, t_14_1]
            hw_gas_boilers = None
            hw_el_boilers = None
            steam_chp_turb = [pt_p_60_1, tr_16_p_1, p_50_1]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name

            
        # +            
        def add_Novopockay_tec(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Новополоцкая ТЭЦ'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # турбоагрегаты, котлы и электрокотлы
            # ПТ-60-130/13  # ПТ-60-130/13  # ПТ-50-130/7  # Р-50-130/13
            # Р-50-130/13    # пвк - нет    # эк - нет
            ###############################################################
            [pt_t_60_el_1, pt_p_60_1, pt_t_60_1] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            [pt_t_60_el_2, pt_p_60_2, pt_t_60_2] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            [pt_t_50_el_1, pt_p_50_1, pt_t_50_1] = block_creator.get_pt_50(global_id(), local_id(), station_name, steam_bus, hw_bus)
            p_50_1 = block_creator.get_p_50(global_id(), local_id(), station_name, steam_bus)
            p_50_2 = block_creator.get_p_50(global_id(), local_id(), station_name, steam_bus)
            # фейковые дорогие источники тепла
            back_hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 10_000, hw_bus, 9999)
            back_steam_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 10_000, steam_bus, 9999)
            # тепловые потребители - sink
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb = [pt_t_60_el_1, pt_t_60_el_2, pt_t_50_el_1, p_50_1, p_50_2]
            hw_chp_turb = [pt_t_60_1, pt_t_60_2, pt_t_50_1]
            hw_gas_boilers = back_hw_gas_boilers
            hw_el_boilers = None
            steam_chp_turb = [pt_p_60_1, pt_p_60_2, pt_p_50_1, p_50_1, p_50_2]
            steam_gas_boilers = back_steam_gas_boilers
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
            

         # +          
        def add_Mogilevskay_tec_2(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Могилевская ТЭЦ-2'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # ПТ-65-130/21 (60 - ограничение)
            # ПТ-50-130/7
            # Р-50-130/22/8
            # ПТ-135/165-130/21
            # SST-060 (2.3 МВт)
            # турбины	302.3	МВт
            # в/о котлы	400	Гкал/час	
            # В/о ЭК	34.4	Гкал/час	
            ###############################################################
            [pt_65_el_1, pt_p_65_1, pt_t_65_1]= block_creator.get_pt_65(global_id(), local_id(), station_name, 0)
            [pt_50_el_1, pt_p_50_1, pt_t_50_1]= block_creator.get_pt_50(global_id(), local_id(), station_name, 0)
            [pt_135_el_1, pt_p_135_1, pt_t_135_1]= block_creator.get_pt_135(global_id(), local_id(), station_name, 0)
            p_50_1 = block_creator.get_p_50(global_id(), local_id(), station_name, 0)
            if self.allowSiemens:
                small_ocgt = block_creator.get_ocgt_small_2_3(global_id(), local_id(), station_name, 0)
            hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 400 * 1.163, hw_bus, 0)
            el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, 1.163 * 34.4, hw_bus, 0)
            # back_steam_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 10_000, steam_bus, 9999)
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb_no_siemens = [pt_65_el_1, pt_50_el_1, pt_135_el_1, p_50_1]
            el_turb_siemens = [small_ocgt] if self.allowSiemens else []
            el_turb = el_turb_no_siemens + el_turb_siemens
            hw_chp_turb = [pt_t_65_1, pt_t_50_1, pt_t_135_1]
            hw_gas_boilers = hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = [pt_p_65_1, pt_p_50_1, pt_p_135_1]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
            ###############################################################
            
            ###############################################################            
        # +   
        def add_Bobryskay_tec_2(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Бобруйская ТЭЦ-2'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # ПТ-60-130/22
            # ПТ-60-130/13
            # ПТ-60-130/22
            # SST-110 (2,6)
            # турбины	182.6	МВт
            #   в/о котлы	460	Гкал/час	
            # В/о ЭК	25.8	Гкал/час	
            ###############################################################
            [pt_t_60_el_1, pt_p_60_1, pt_t_60_1] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            [pt_t_60_el_2, pt_p_60_2, pt_t_60_2] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            [pt_t_60_el_3, pt_p_60_3, pt_t_60_3] = block_creator.get_pt_60(global_id(), local_id(), station_name, steam_bus, hw_bus)
            if self.allowSiemens:
                small_ocgt = block_creator.get_ocgt_small_2_6(global_id(), local_id(), station_name, 0)
            hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 460 * 1.163, hw_bus, 0)
            el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, 25.8 * 1.163, hw_bus, 0)
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb_no_siemens = [pt_t_60_el_1, pt_t_60_el_2, pt_t_60_el_3]
            el_turb_siemens = [small_ocgt] if self.allowSiemens else []
            el_turb = el_turb_no_siemens + el_turb_siemens
            hw_chp_turb = [pt_t_60_1, pt_t_60_2, pt_t_60_3]
            hw_gas_boilers = hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = [pt_p_60_1, pt_p_60_2, pt_p_60_3]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name

        # + 
        def add_Grodnenskay_tec_2(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Гродненская ТЭЦ-2'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # ПТ-70-12,8/1,28
            # ПТ-70-12,8/1,28
            # Р-50-130/13
            # ТГ-0,75 ПА/6,3Р14/4
            # PG 9171E
            # турбины	312.45	МВт
            # в/о котлы	380	Гкал/час	
            # в/о ЭК	51.6	Гкал/час	
            ###############################################################
            [pt_t_70_el_1, pt_p_70_1, pt_t_70_1] = block_creator.get_pt_70(global_id(), local_id(), station_name, steam_bus, hw_bus)
            [pt_t_70_el_2, pt_p_70_2, pt_t_70_2] = block_creator.get_pt_70(global_id(), local_id(), station_name, steam_bus, hw_bus)
            p_50_1 = block_creator.get_p_50(global_id(), local_id(), station_name, 0)
            # не сделано
            ocgt_chp = block_creator.get_ocgt_chp_121(global_id(), local_id(), station_name, 0)
            hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 380 * 1.163, hw_bus, 0)
            el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, 51.6 * 1.163, hw_bus, 0)
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb = [pt_t_70_el_1, pt_t_70_el_2, p_50_1, ocgt_chp]
            hw_chp_turb = [pt_t_70_1, pt_t_70_2]
            hw_gas_boilers = hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = [pt_p_70_1, pt_p_70_2, p_50_1, ocgt_chp]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
            
        # +        
        def add_Mozyrskay_tec_2(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Мозырская ТЭЦ-2'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # ПТ-70-130/40/13
            # ПТ-135/165-130/15
            # турбины	205	МВт
            ###############################################################
            [pt_t_70_el_1, pt_p_70_1, pt_t_70_1] = block_creator.get_pt_70(global_id(), local_id(), station_name, steam_bus, hw_bus)
            [pt_t_135_el_1, pt_p_135_1, pt_t_135_1] = block_creator.get_pt_135(global_id(), local_id(), station_name, steam_bus, hw_bus)
            hw_gas_boilers = None
            el_boilers_hw = None
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            el_turb = [pt_t_70_el_1, pt_t_135_el_1]
            hw_chp_turb = [pt_t_70_1, pt_t_135_1]
            hw_gas_boilers = hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = [pt_p_70_1, pt_p_135_1]
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name


                        
        # +                 
        def add_Gomelskay_tec_2(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Гомельская ТЭЦ-2'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            turbine_T_factory = self.turbine_T_factory
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            global_id = self.inc_global_id
            local_id = counter.next
            ###############################################################
            hw_name = 'гвс'
            steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # Т-180/210-130-1
            # Т-180/210-130-1
            # Т-180/210-130-1
            # в/о котлы	540	Гкал/час	
            # В/о ЭК	68.8	Гкал/час	
            ###############################################################
            t_180_1 = turbine_T_factory.get_t_180(global_id(), local_id(), station_name, 0.01)
            t_180_2 = turbine_T_factory.get_t_180(global_id(), local_id(), station_name, 0.02)
            t_180_3 = turbine_T_factory.get_t_180(global_id(), local_id(), station_name, 0.03)
            hw_gas_boilers = block_creator.get_gas_boilers(global_id(), local_id(),station_name, 540 * 1.163, hw_bus, 0)
            el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, 68.8 * 1.163, hw_bus, 0)
            ###############################################################
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = heat_water_demand_data)
            steam_sink = create_sink_abs(label = set_label(
            station_name, steam_name, 'потребитель'),
            input_flow = steam_bus,
            demand_absolute_data = steam_demand_data)
            ###############################################################
            el_turb = [t_180_1, t_180_2, t_180_3]
            hw_chp_turb = [t_180_1, t_180_2, t_180_3]
            hw_gas_boilers = hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = []
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
 
        
         # +            
        def add_block_staion_natural_gas(self, fixed_el_load_data_rel):
            station_name = 'Блок-станции(газ)'
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            block_stations_install_power = 200 if self.reduce_block_station_power else 630
            block_stations = self.block_creator.get_block_station_natural_gas(
                global_index = global_id(),
                local_index = local_id(),
                nominal_value = block_stations_install_power,
                station_name = station_name,
                fixed_el_load_data_rel= fixed_el_load_data_rel
            )
            
            ###############################################################
            hw_bus  = steam_bus = None
            hw_sink = steam_sink = None
            ###############################################################
            el_turb = [block_stations]
            hw_chp_turb = None
            hw_gas_boilers = None
            hw_el_boilers = None
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
        
        # +                        
        def add_renewables_fixed(self, fixed_wind_rel, fixed_solar_rel, fixed_hydro_rel):
            # сделать варинат без фиксированной нагрузки
            station_name = 'ВИЭ'
            counter = Custom_counter()
            global_id = self.inc_global_id
            local_id = counter.next
            
            if self.allowRenewables:
                hydro_renewables = self.block_creator.get_hydro_renewables(
                    global_index = global_id(),
                    local_index = local_id(),
                    nominal_value = 95.3,
                    station_name = station_name,
                    fixed_el_load_data_rel= fixed_hydro_rel
                )
                
                wind_renewables = self.block_creator.get_wind_renewables(
                    global_index = global_id(),
                    local_index = local_id(),
                    nominal_value = 125.8,
                    station_name = station_name,
                    fixed_el_load_data_rel= fixed_wind_rel
                )
                
                solar_renewables = self.block_creator.get_solar_renewables(
                    global_index = global_id(),
                    local_index = local_id(),
                    nominal_value = 160.7,
                    station_name = station_name,
                    fixed_el_load_data_rel= fixed_solar_rel
                )
                ###############################################################
            hw_bus  = steam_bus = None
            hw_sink = steam_sink = None
            ###############################################################
            el_renewables = [hydro_renewables, wind_renewables, solar_renewables] if self.allowRenewables else []
            el_turb = [] + el_renewables
            hw_chp_turb = None
            hw_gas_boilers = None
            hw_el_boilers = None
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name
                                   
                                            
            
        # +    
        def add_small_chp(self, fixed_el_load_data_rel):
            station_name = 'Малые ТЭЦ'
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            create_buses = self.bus_creator.create_buses
            hw_name = 'гвс'
            hw_bus = create_buses(set_label(station_name, hw_name))
            heat_to_power = 1.9
            
            nominal_el_value = 470
            small_chp = block_creator.get_small_chp(global_id(),local_id(),
                                nominal_el_value, station_name, hw_bus ,fixed_el_load_data_rel)

            
            el_boilers_hw = gas_boilers_hw = None
            if self.small_chp_active_part < 1:
                boilers_power = (1 - self.small_chp_active_part) * heat_to_power * nominal_el_value
                if self.small_chp_replace_el_boiler:
                    el_boilers_hw = block_creator.get_el_boilers(global_id(), local_id(), station_name, boilers_power, hw_bus, 0)
                if self.small_chp_replace_gas_boiler:
                    gas_boilers_hw = block_creator.get_gas_boilers(global_id(), local_id(), station_name, boilers_power, hw_bus, 0)
                    
             

            hw_load_abs = pd.DataFrame(fixed_el_load_data_rel)
            hw_load_abs = hw_load_abs * heat_to_power * 470
            hw_load_abs = hw_load_abs['Малые ТЭЦ'].values.tolist()
            hw_sink = create_sink_abs(label = set_label(
            station_name, hw_name, 'потребитель'),
            input_flow = hw_bus,
            demand_absolute_data = hw_load_abs)
            ###############################################################
            steam_bus = None
            steam_sink = None
            ###############################################################
            el_turb = [small_chp]
            hw_chp_turb = [small_chp]
            hw_gas_boilers = None if not gas_boilers_hw else gas_boilers_hw
            hw_el_boilers = None if not el_boilers_hw else el_boilers_hw
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            return station_name

                        
        # +  
        def add_Bel_npp(self):
            station_name = 'Белорусская АЭС'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            ###############################################################
            # hw_name = None
            # hw_name = 'гвс'
            # steam_name = 'пар'
            # hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = None
            hw_bus = None
            ###############################################################
            # турбоагрегаты, котлы и электрокотлы
            # ВВЭР-1200(1170) # ВВЭР-1200(1170)
            ###############################################################
            vver_1200_1 = block_creator.get_vver_1200(global_id(), local_id(), station_name, -999)
            vver_1200_2 = block_creator.get_vver_1200(global_id(), local_id(), station_name, -999)
            # новый блок аэс
            ###############################################################
            hw_sink = steam_sink = None
            ###############################################################
            el_turb = [vver_1200_1, vver_1200_2]
            hw_chp_turb = None
            hw_gas_boilers = None
            hw_el_boilers = None
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': hw_chp_turb,
                                    'гвс-кот-источник': hw_gas_boilers,
                                    'гвс-эк-источник': hw_el_boilers
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': steam_chp_turb,
                                    'пар-кот-источник': steam_gas_boilers,
                                    'пар-эк-источник': steam_el_boilers,
                                    }
                },
                'потоки':  {
                                'гвс-поток': hw_bus, 
                                'пар-поток': steam_bus,
                },
                'потребители':{
                                'гвс-потребитель': hw_sink,
                                'пар-потребитель': steam_sink
                }} 
            
            return station_name
            
            
        def add_district_boilers(self, heat_water_demand_data):
            station_name = 'Котельные ЖКХ'
            # create_buses = self.bus_creator.create_buses
            # block_creator = self.block_creator
            # create_sink_abs = self.sink_creator.create_sink_absolute_demand
            # counter = Custom_counter()
            # local_id = counter.next
            # global_id = self.inc_global_id
            # ###############################################################
            # # hw_name = None
            # # hw_name = 'гвс'
            # # steam_name = 'пар'
            # # hw_bus = create_buses(set_label(station_name, hw_name))
            # steam_bus = None
            # hw_bus = None
            # pass
            pass


         
        def add_district_boilers_Belenergo(self, heat_water_demand_data, steam_demand_data):
            station_name = 'Районные котельные Белэнерго'
            pass
            
            
            
        def add_new_npp(self):
            station_name = 'Новые АЭС'
            block_creator = self.block_creator
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
                        
            vver_toi_1 = None
            if self.vver_toi_flag:
                vver_toi_1 = block_creator.get_vver_toi(global_id(), local_id(), station_name, 0)            

            vver_600_1 = None
            if self.vver_600_flag:
                vver_600_1 = block_creator.get_vver_600(global_id(), local_id(), station_name, 0)
            
            ritm_200_lst = []
            if self.ritm_200_count:
                for i in range(1, self.ritm_200_count + 1):
                    ritm_200_1 = block_creator.get_ocgt_25(global_id(), local_id(), station_name, 0)
                    ritm_200_lst.append(ritm_200_1)
            
            el_turb = []

            if vver_toi_1:
                el_turb = el_turb + ritm_200_1.append(vver_toi_1)            

            if vver_600_1:
                el_turb = el_turb + ritm_200_1.append(vver_600_1)
            
            install_power = self.get_install_power_blocklist(el_turb)
            
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': None,
                                    'гвс-кот-источник': None,
                                    'гвс-эк-источник': None
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': None,
                                    'пар-кот-источник': None,
                                    'пар-эк-источник': None,
                                    }
                },
                'потоки':  {
                                'гвс-поток': None, 
                                'пар-поток': None,
                },
                'потребители':{
                                'гвс-потребитель': None,
                                'пар-потребитель': None
                }} 
            
            return station_name
            
            
                        
            
            
        def add_new_ocgt(self):
            station_name = 'Новые ГТУ'
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            
            ocgt_25_lst = []
            ocgt_100_lst = []
            ocgt_125_lst = []
            
            if self.new_ocgt_count_options['гту-25']:
                for i in range(1, self.new_ocgt_count_options['гту-25'] + 1):
                    ocgt_25_1 = block_creator.get_ocgt_25(global_id(), local_id(), station_name, 0)
                    ocgt_25_lst.append(ocgt_25_1)
                        
            if self.new_ocgt_count_options['гту-100']:
                for i in range(1, self.new_ocgt_count_options['гту-100'] + 1):
                    ocgt_100_1 = block_creator.get_ocgt_100(global_id(), local_id(), station_name, 0)
                    ocgt_100_lst.append(ocgt_100_1)
                    
                        
            if self.new_ocgt_count_options['гту-125']:
                for i in range(1, self.new_ocgt_count_options['гту-125'] + 1):
                    ocgt_125_1 = block_creator.get_ocgt_125(global_id(), local_id(), station_name, 0)
                    ocgt_125_lst.append(ocgt_125_1)
            

            el_turb = ocgt_25_lst + ocgt_125_lst + ocgt_100_lst

            install_power = self.get_install_power_blocklist(el_turb)
            
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': None,
                                    'гвс-кот-источник': None,
                                    'гвс-эк-источник': None
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': None,
                                    'пар-кот-источник': None,
                                    'пар-эк-источник': None,
                                    }
                },
                'потоки':  {
                                'гвс-поток': None, 
                                'пар-поток': None,
                },
                'потребители':{
                                'гвс-потребитель': None,
                                'пар-потребитель': None
                }} 
            
            return station_name
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
            
        # def add_Fake_station(self):
        #     station_name = 'Фейковая станция'
        #     ###############################################################
        #     block_creator = self.block_creator
        #     counter = Custom_counter()
        #     next = counter.next
        #     ###############################################################
        #     # hw_name = None
        #     # hw_name = 'гвс'
        #     # steam_name = 'пар'
        #     # hw_bus = create_buses(set_label(station_name, hw_name))
        #     steam_bus = None
        #     hw_bus = None
        #     ###############################################################
        #     # турбоагрегаты, котлы и электрокотлы
        #     # ВВЭР-1200(1170) # ВВЭР-1200(1170)
        #     ###############################################################
        #     expense_el = block_creator.get_dummy_source(next(), station_name,
        #     'дорогой_источник_электроэнергии', self.global_output_flow, 9999)
        #     ###############################################################
        #     hw_sink = steam_sink = None
        #     ###############################################################
        #     el_turb = [expense_el]
        #     hw_chp_turb = None
        #     hw_gas_boilers = None
        #     hw_el_boilers = None
        #     steam_chp_turb = None
        #     steam_gas_boilers = None
        #     steam_el_boilers = None
        #     install_power = self.get_install_power_blocklist(el_turb)
        #     ###############################################################
        #     self.active_stations_data[station_name] = {
        #         'установленная мощность': install_power,
        #         'э-источники': el_turb,
        #         'гвс-источники': {
        #             'гвс-тэц-источник': hw_chp_turb,
        #             'гвс-кот-источник': hw_gas_boilers,
        #             'гвс-эк-источник': hw_el_boilers
        #             },
        #         'пар-источники': {
        #             'пар-тэц-источник': steam_chp_turb,
        #             'пар-кот-источник': steam_gas_boilers,
        #             'пар-эк-источник': steam_el_boilers,
        #         },
        #         'гвс-поток': hw_bus, 
        #         'пар-поток': steam_bus,
        #         'гвс-потребитель': hw_sink,
        #         'пар-потребитель': steam_sink
        #         } 
            
        #     return station_name          


        def add_natural_gas_source(self, usd_per_1000_m3):
            self.global_gas_source = self.block_creator.get_natural_gas_source('природный_газ_источник', usd_per_1000_m3)
            self.natural_gas_price = usd_per_1000_m3
            
            
        def add_electricity_source(self, nominal_value ,usd_per_Mwth):
            station_name = 'Дорогой источник электроэнергии'
            counter = Custom_counter()
            local_id = counter.next
            global_id = self.inc_global_id
            expense_el_block = self.block_creator.get_electricity_source(global_id(), local_id(), nominal_value, station_name, usd_per_Mwth)
            el_turb = [expense_el_block]
            install_power = self.get_install_power_blocklist(el_turb)
            ###############################################################
            self.active_stations_data[station_name] = {
                'установленная мощность': install_power,
                'источники': {
                                'э-источники': el_turb,
                                'гвс-источники': {
                                    'гвс-тэц-источник': None,
                                    'гвс-кот-источник': None,
                                    'гвс-эк-источник': None
                                    },
                                'пар-источники': {
                                    'пар-тэц-источник': None,
                                    'пар-кот-источник': None,
                                    'пар-эк-источник': None,
                                    }
                },
                'потоки':  {
                                'гвс-поток': None, 
                                'пар-поток': None,
                },
                'потребители':{
                                'гвс-потребитель': None,
                                'пар-потребитель': None
                }} 
            return station_name



