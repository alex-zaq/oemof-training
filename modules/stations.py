from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.wrapper_generic_blocks import *
 

# создать турбину типа Т
# создать турбину типа Р
# создать турбину типа ПТ
# создать электрокотел
# создать метод быстрого построения графиков
# сделать метод создания станции
#  (добавить в э все турбины,электрокотлы, станции со всеми настройками)


def get_station_method_by_energysystem(es, bl_lst, glob_gas_flow, glob_el_flow, station_list):

	def get_T_250(station_name, output_flow_T):
		create_T_turb = get_chp_method_by_energy_system(es, bl_lst, 'Т')
		t = create_T_turb(
     		label = station_name +'_T-250',
				nominal_el_value = 250,
				min_power_fraction = 0.5,
				nominal_input_T = 350,
				input_flow = glob_gas_flow,
				output_flow_el = glob_el_flow,
				output_flow_T = output_flow_T,
				efficiency_T = 0.82,
				heat_to_el_T = 1.9,
				efficiency_full_condensing_mode = 0.41,
				variable_costs = 0,
				boiler_efficiency = 1)
		return t

	def get_PT_60_T(station_name, output_flow_T):
		create_PT_T_turb = get_chp_method_by_energy_system(es, bl_lst, 'ПТ-Т')
		return create_PT_T_turb(
     		label = station_name +'ПТ-60',
				nominal_el_value = 60,
				min_power_fraction = 0.4,
				input_flow = glob_gas_flow,
				output_flow_el = glob_el_flow,
				output_flow_T = output_flow_T,
				efficiency_T = 0.91,
				heat_to_el_T = 2.02,
				variable_costs = 0,
				boiler_efficiency = 1)

	def create_test_station (heat_water_demand_data, steam_demand_date, planning_outage_options):
		station_name = 'Тестовая станция'
		hw_bus_name = 'Отопление+ГВС'
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, 'абс')
  
		# тепловые спросы - bus
		###############################################################
		test_station_hw_bus = create_buses(station_name +'_' + station_name)

		# турбоагрегаты, котлы и электрокотлы - transformer
		###############################################################
		t_250_1 = get_T_250(station_name, test_station_hw_bus)
  
  
		chp_turbines = [t_250_1]
		# тепловые потребители - sink
		###############################################################
		minskay_tec_4_hw_sink = create_abs_demand(
		label = station_name + ' ' + hw_bus_name, 
		input_flow = test_station_hw_bus,
		demand_absolute_data = heat_water_demand_data)
	
		return [{'эл':chp_turbines,'ГВС':chp_turbines},{'ГВС':test_station_hw_bus, 'Пар': None}]  
     
  
  
	def create_Minskay_tec_4(heat_water_demand_data, steam_demand_date = None, planning_outage_options = None):
		station_name = 'Минская ТЭЦ-4'
		hw_bus_name = 'Отопление+ГВС'
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, 'абс')
  
		# тепловые спросы - bus
		###############################################################
		minskay_tec_4_hw_bus = create_buses(station_name +'_' + station_name)

		# турбоагрегаты, котлы и электрокотлы - transformer
		###############################################################
		pt_t_60 = get_PT_60_T(station_name, minskay_tec_4_hw_bus)
		t_250_1 = get_T_250(station_name, minskay_tec_4_hw_bus)
		t_250_2 = get_T_250(station_name, minskay_tec_4_hw_bus)
  
		сhp_turbines = [pt_t_60, t_250_1, t_250_2]
		# тепловые потребители - sink
		###############################################################
		minskay_tec_4_hw_sink = create_abs_demand(
		label = station_name + ' ' + hw_bus_name, 
		input_flow = minskay_tec_4_hw_bus,
		demand_absolute_data = heat_water_demand_data)
	
		return [{'эл':сhp_turbines,'ГВС':сhp_turbines},{'ГВС':minskay_tec_4_hw_bus, 'Пар': None}]

	station_dict = {
		"Минская ТЭЦ-4": create_Minskay_tec_4,
		"Тестовая станция": create_test_station
	}

	if not isinstance(station_list, list):
		if station_list in station_dict:
			return station_dict[station_list]
	else:
		raise Exception('параметр не является списком')

	if len(station_list) == 0:
		raise Exception('cписок станций пуст')
	
	res = []
	for station in station_list:
		if station in station_dict:
			res += [station_dict[station]]
		
	if len(res) != 0:
		return res
	else:
		raise Exception('не определено ни одной станции')
	
		

	
 		
    
	
    
  


  
  

  
    
  
  
  
 