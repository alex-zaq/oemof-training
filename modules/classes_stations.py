from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from modules.helpers import set_label
from modules.classes_specific_blocks import Specific_blocks
from modules.classes_generic_blocks import Generic_sinks, Generic_buses
from modules.helpers import Custom_counter, set_label



class Stations_creator:
  
		def __init__(self, es, global_input_flow, global_output_flow) -> None:
			self.es = es
			self.__block_collection = []
			self.__input_flow = global_input_flow
			self.__ouinput_flow = global_output_flow
			self.block_creator = Specific_blocks(es, self.__block_collection, global_input_flow, global_output_flow)
			self.sink_creator = Generic_sinks(es)
			self.bus_creator = Generic_buses(es)
			# self.counter = Custom_counter()
			
        
		def get_block_collection(self):
			return self.__block_collection        
		def get_block_creator(self):
			return self.__block_creater
		def get_blocks_by_station_type(self):
			pass
		def get_blocks_by_block_type(self):
			pass
        
        
		def create_Minskay_tec_4(
					self,
					heat_water_demand_data,
					steam_demand = None,
					planning_outage = None
				):
			station_name = 'Минская ТЭЦ-4'
			###############################################################
			create_buses = self.bus_creator.create_buses
			block_creator = self.block_creator
			create_sink_abs = self.sink_creator.create_sink_absolute_demand
			counter = Custom_counter()
			next = counter.next
			###############################################################
			hw_bus_name = 'гвс'
			hw_bus = create_buses(set_label(station_name, hw_bus_name))
			steam_bus = None
			###############################################################
			# турбоагрегаты, котлы и электрокотлы - transformer
			###############################################################
			pt_t_60 = block_creator.get_pt_60_t(next(), station_name, hw_bus)
			t_250_1 = block_creator.get_t_250(next(), station_name, hw_bus)
			t_250_2 = block_creator.get_t_250(next(), station_name, hw_bus)
			t_250_3 = block_creator.get_t_250 (next(), station_name, hw_bus)
			t_110_1 = block_creator.get_t_110 (next(), station_name, hw_bus)
			t_110_2 = block_creator.get_t_110 (next(), station_name, hw_bus)
			el_boilers_hw = block_creator.get_el_boilers(next(), station_name, 1.163 * 137.6, hw_bus, 'гвс' , 0)
			# тепловые потребители - sink
			###############################################################
			hw_sink = create_sink_abs(
			label = set_label(station_name, hw_bus_name, 'sink'), 
			input_flow = hw_bus,
			demand_absolute_data = heat_water_demand_data)
			###############################################################
			el = [pt_t_60, t_250_1, t_250_2, t_250_3, t_110_1, t_110_2]
			hw_chp = [pt_t_60, t_250_1, t_250_2, t_250_3, t_110_1, t_110_2]
			hw_gas_boilers = None
			hw_el_boilers = [el_boilers_hw]
			steam_chp = None
			steam_gas_boilers = None
			steam_el_boilers = None
   
			self.Minskay_tec4 = (
     {'э': el,'гвс-тэц': hw_chp, 'гвс-кот': hw_gas_boilers, 'гвс-эк': hw_el_boilers,
			'пар-тэц': steam_chp,'пар-кот': steam_gas_boilers, 'пар-эк': steam_el_boilers},
			{'гвс': hw_bus, 'пар': steam_bus}
     )
   
			return self.Minskay_tec4