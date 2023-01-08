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



class Energy_system_creator:
  
        def __init__(self, es, global_input_flow, global_output_flow):
            self.es = es
            self.__block_collection = []
            self.__input_flow = global_input_flow
            self.__ouinput_flow = global_output_flow
            self.block_creator = Specific_blocks(es, self.__block_collection, global_input_flow, global_output_flow)
            self.sink_creator = Generic_sinks(es)
            self.bus_creator = Generic_buses(es)
            self.active_stations_data = {}
			
        
        def get_block_collection(self):
            return self.__block_collection        
        def get_block_creator(self):
            return self.__block_creater
        def get_blocks_by_station_type(self):
            pass
        def get_blocks_by_block_type(self):
            pass
        
        def get_hw_buses_for_model_stations(self):
            all_hw_buses = []
            for k, _ in self.active_stations_data:
                if self.active_stations_data[k]['гвс'] != None:
                    all_hw_buses += [self.active_stations_data[k]['гвс']]
                
        def get_steam_buses_for_model_stations(self):
            all_steam_buses = []
            for k, _ in self.active_stations_data:
                if self.active_stations_data[k]['пар'] != None:
                    all_steam_buses += [self.active_stations_data[k]['пар']]
                
        

        def add_Minskay_tec_4(self, heat_water_demand_data, steam_demand_data = None, planning_outage = None):
            station_name = 'Минская ТЭЦ-4'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            next = counter.next
            ###############################################################
            hw_name = 'гвс'
            # steam_name = 'пар'
            hw_bus = create_buses(set_label(station_name, hw_name))
            steam_bus = None
            # steam_bus = create_buses(set_label(station_name, steam_name))
            ###############################################################
            # турбоагрегаты, котлы и электрокотлы
            # ПТ-60-130/13    # Т-110/120-130   # Т-110/120-130
            # Т-250/300-240-2 # Т-250/300-240-2 # Т-255/305-240-5
            # эк - 137 гкал/ч  пвк - нет
            ###############################################################
            pt_t_60 = block_creator.get_pt_60_t(next(), station_name, hw_bus)
            t_250_1 = block_creator.get_t_250(next(), station_name, hw_bus)
            t_250_2 = block_creator.get_t_250(next(), station_name, hw_bus)
            t_255_1 = block_creator.get_t_255 (next(), station_name, hw_bus)
            t_110_1 = block_creator.get_t_110 (next(), station_name, hw_bus)
            t_110_2 = block_creator.get_t_110 (next(), station_name, hw_bus)
            el_boilers_hw = block_creator.get_el_boilers(next(), station_name, 1.163 * 137.6, hw_bus, 'гвс' , 0)
            # фейковые дорогие источники тепла
            back_hw_gas_boilers = block_creator.get_gas_boilers(next(),station_name, 10_000, hw_bus, hw_name, 9999)
            # back_steam_gas_boilers = block_creator.get_gas_boilers(next(),station_name, 10_000, hw_bus, steam_name, 9999)
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
            el_turb = [pt_t_60, t_250_1, t_250_2, t_255_1, t_110_1, t_110_2]
            hw_chp_turb = [pt_t_60, t_250_1, t_250_2, t_255_1, t_110_1, t_110_2]
            hw_gas_boilers = back_hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            ###############################################################
            self.active_stations_data[station_name] = {
                'э-тэц-источник': el_turb,
                'гвс-тэц-источник': hw_chp_turb,
                'гвс-кот-источник': hw_gas_boilers,
                'гвс-эк-источник': hw_el_boilers,
                'пар-тэц-источник': steam_chp_turb,
                'пар-кот-источник': steam_gas_boilers,
                'пар-эк-источник': steam_el_boilers,
                'гвс-поток': hw_bus, 
                'пар-поток': steam_bus,
                'гвс-потребитель': hw_sink,
                'пар-потребитель': steam_sink
                }  
        
        def add_Novopockay_tec(self, heat_water_demand_data,steam_demand_data = None, planning_outage = None):
            station_name = 'Новополоцкая ТЭЦ'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            next = counter.next
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
            [pt_t_60_el_1, pt_p_60_1, pt_t_60_1] = block_creator.get_pt_60(next(), station_name, steam_bus, hw_bus)
            [pt_t_60_el_2, pt_p_60_2, pt_t_60_2] = block_creator.get_pt_60(next(), station_name, steam_bus, hw_bus)
            [pt_t_50_el_1, pt_p_50_1, pt_t_50_1] = block_creator.get_pt_50(next(), station_name, steam_bus, hw_bus)
            p_50_1 = block_creator.get_p_50(next(), station_name, steam_bus)
            p_50_2 = block_creator.get_p_50(next(), station_name, steam_bus)
            # фейковые дорогие источники тепла
            back_hw_gas_boilers = block_creator.get_gas_boilers(next(),station_name, 10_000, hw_bus, hw_name, 9999)
            back_steam_gas_boilers = block_creator.get_gas_boilers(next(),station_name, 10_000, hw_bus, steam_name, 9999)
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
            steam_chp_turb = [pt_p_60_1, pt_p_60_2, pt_p_50_1]
            steam_gas_boilers = back_steam_gas_boilers
            steam_el_boilers = None
            ###############################################################
            self.active_stations_data[station_name] = {
                'э-тэц-источник': el_turb,
                'гвс-тэц-источник': hw_chp_turb,
                'гвс-кот-источник': hw_gas_boilers,
                'гвс-эк-источник': hw_el_boilers,
                'пар-тэц-источник': steam_chp_turb,
                'пар-кот-источник': steam_gas_boilers,
                'пар-эк-источник': steam_el_boilers,
                'гвс-поток': hw_bus, 
                'пар-поток': steam_bus,
                'гвс-потребитель': hw_sink,
                'пар-потребитель': steam_sink
                } 
                        
        def add_Lukomolskay_gres(self, heat_water_demand_data = None, planning_outage = None):
            station_name = 'Лукомольская ГРЭС'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            next = counter.next
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
            k_315_1 = block_creator.get_k_315(next(), station_name)
            k_315_2 = block_creator.get_k_315(next(), station_name)
            k_315_3 = block_creator.get_k_315(next(), station_name)
            k_310_4 = block_creator.get_k_310(next(), station_name)
            k_300_5 = block_creator.get_k_300(next(), station_name)
            k_300_6 = block_creator.get_k_300(next(), station_name)
            k_300_7 = block_creator.get_k_300(next(), station_name)
            k_300_8 = block_creator.get_k_300(next(), station_name)
            ccgt_427 = block_creator.get_ccgt_427(next(), station_name)
            ###############################################################
            el_boilers_hw = block_creator.get_el_boilers(next(), station_name, 1.163 * 68.8, hw_bus, hw_name , 0)
            # фейковые дорогие источники тепла
            back_hw_gas_boilers = block_creator.get_gas_boilers(next(),station_name, 10_000, hw_bus, hw_name, 9999)
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
            el_turb = [k_315_1, k_315_2, k_315_3, k_310_4, k_300_5, k_300_6, k_300_7, k_300_8, ccgt_427]
            hw_chp_turb = None
            hw_gas_boilers = back_hw_gas_boilers
            hw_el_boilers = el_boilers_hw
            steam_chp_turb = None
            steam_gas_boilers = None
            steam_el_boilers = None
            ###############################################################
            self.active_stations_data[station_name] = {
                'э-тэц-источник': el_turb,
                'гвс-тэц-источник': hw_chp_turb,
                'гвс-кот-источник': hw_gas_boilers,
                'гвс-эк-источник': hw_el_boilers,
                'пар-тэц-источник': steam_chp_turb,
                'пар-кот-источник': steam_gas_boilers,
                'пар-эк-источник': steam_el_boilers,
                'гвс-поток': hw_bus, 
                'пар-поток': steam_bus,
                'гвс-потребитель': hw_sink,
                'пар-потребитель': steam_sink
                }  
            
            

        def add_Bel_npp(self,planning_outage = None):
            station_name = 'Белорусская АЭС'
            ###############################################################
            create_buses = self.bus_creator.create_buses
            block_creator = self.block_creator
            create_sink_abs = self.sink_creator.create_sink_absolute_demand
            counter = Custom_counter()
            next = counter.next
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
            vver_1200_1 = block_creator.get_vver_1200(next(), station_name, -999)
            vver_1200_2 = block_creator.get_vver_1200(next(), station_name, -999)
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
            ###############################################################
            self.active_stations_data[station_name] = {
                'э-тэц-источник': el_turb,
                'гвс-тэц-источник': hw_chp_turb,
                'гвс-кот-источник': hw_gas_boilers,
                'гвс-эк-источник': hw_el_boilers,
                'пар-тэц-источник': steam_chp_turb,
                'пар-кот-источник': steam_gas_boilers,
                'пар-эк-источник': steam_el_boilers,
                'гвс-поток': hw_bus, 
                'пар-поток': steam_bus,
                'гвс-потребитель': hw_sink,
                'пар-потребитель': steam_sink
                }  
                     


