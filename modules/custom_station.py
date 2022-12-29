from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.custom_blocks import *
 

# создать турбину типа Т
# создать турбину типа Р
# создать турбину типа ПТ
# создать электрокотел
# создать метод быстрого построения графиков
# сделать метод создания станции
#  (добавить в э все турбины,электрокотлы, станции со всеми настройками)


def get_station_method_by_energysystem(energy_system, block_collection):
	def create_Minskay_tec_4(input_fuel_flow, output_el_flow, heat_water_profile, shut_down_options):
		name = 'Минская ТЭЦ-4'
		heat_water_bus_name = 'Отопление+ГВС'
		
		[create_buses] = get_buses_method_by_energy_system(energy_system)
		[create_abs_demand, _] = get_sinks_method_by_energy_system(energy_system, block_collection)
		[create_pt_turbine] = get_chp_method_by_energy_system(energy_system, block_collection)
  
  
		[Minskay_tec_4_heat_water_bus] = create_buses(
		name +'_' + heat_water_bus_name)
		 
		Minskay_tec_4_heat_water_sink = create_abs_demand(
		label = name + ' ' + heat_water_bus_name, 
		input_flow = Minskay_tec_4_heat_water_bus,
		demand_absolute_data = heat_water_profile)
	
		# pt_60 = create_pt_turbine('ПТ-60('+name+')', nominal_el_value = 60, min_power_fraction = 0.4, input_flow = input_fuel_flow,  )
	

		return [Minskay_tec_4_blocks, Minskay_tec_4_buses,]
  
  

	
 		
    
	
    
  


  
  

  
    
  
  
  
 