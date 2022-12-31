from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.wrapper_generic_blocks import *
from collections import namedtuple as nt
 

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
     		group_options = station_name +'_T-250',
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

	def get_T_110(station_name, output_flow_T):
		create_T_turb = get_chp_method_by_energy_system(es, bl_lst, 'Т')
		t = create_T_turb(
     		label = station_name +'_T-110',
				nominal_el_value = 110,
				min_power_fraction = 0.35,
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

	def create_test_station (station_name, heat_water_demand_data, steam_demand_date, planning_outage_options):
		station_name = station_name
		hw_bus_name = 'Отопление+ГВС'
		create_source = get_sources_methods_by_energy_system(es, bl_lst)
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, 'абс')
  		# тепловые спросы - bus
		###############################################################
		hw_bus = create_buses(station_name +'_' + station_name)
		# турбоагрегаты, котлы и электрокотлы - transformer
		###############################################################
		t_250_1 = get_T_250(station_name, hw_bus)
		heat_source = create_source(station_name+'_дорогой источник ГВС', hw_bus, 9999) 
		# тепловые потребители - sink
		###############################################################
		hw_sink = create_abs_demand(
		label = station_name + ' ' + hw_bus_name, 
		input_flow = hw_bus,
		demand_absolute_data = heat_water_demand_data)
		###############################################################
		el_tr_lst = [t_250_1]
		hw_tr_lst = [t_250_1, heat_source]
		steam_tr_lst = None
		hw_bus_lst = hw_bus
		steam_bus_lst = None
  

		return ({'эл': el_tr_lst,'ГВС': hw_tr_lst, 'Пар': steam_tr_lst},{'ГВС': hw_bus_lst, 'Пар': None})
     
  
  
	def create_Minskay_tec_4(heat_water_demand_data, steam_demand_date = None, planning_outage_options = None):
  #  startup options, planning outage
		station_name = 'Минская ТЭЦ-4'
		hw_bus_name = 'Отопление+ГВС'
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, sink_type= 'abs')
		create_simple_tr = get_simple_transformers_method_by_energy_system(es, bl_lst, block_type= 'simple')
		# тепловые спросы - bus
		###############################################################
		hw_bus = create_buses(station_name +'_' + hw_bus_name)
		steam_bus = None
		# турбоагрегаты, котлы и электрокотлы - transformer
		###############################################################
		pt_t_60 = get_PT_60_T(station_name, hw_bus)
		t_250_1 = get_T_250(station_name, hw_bus)
		t_250_2 = get_T_250(station_name, hw_bus)
		t_250_3 = get_T_250(station_name, hw_bus)
		t_110_1 = get_T_110(station_name, hw_bus)
		t_110_2 = get_T_110(station_name, hw_bus)
		el_boiler = create_simple_tr(station_name+'_ЭК', 1.163 * 137.6, glob_el_flow, hw_bus, 0.99, 0)
		# тепловые потребители - sink
		###############################################################
		hw_sink = create_abs_demand(
		label = station_name + '_' + hw_bus_name, 
		input_flow = hw_bus,
		demand_absolute_data = heat_water_demand_data)
		###############################################################
		el = [pt_t_60, t_250_1, t_250_2, t_250_3, t_110_1, t_110_2]
		hw_chp = [pt_t_60, t_250_1, t_250_2, t_250_3, t_110_1, t_110_2]
		hw_gas_boilers = None
		hw_el_boilers = [el_boiler]
		steam_chp = None
		steam_gas_boilers = None
		steam_el_boilers = None
		###############################################################
	# sink?
		return ({'э': el,
           'гвс-тэц': hw_chp, 'гвс-кот': hw_gas_boilers, 'гвс-эк': hw_el_boilers,
           'пар-тэц': steam_chp,'пар-кот': steam_gas_boilers, 'пар-эк': steam_el_boilers},
          {'гвс': hw_bus, 'пар': steam_bus})



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
	
		

	
 		
    
	
    
  


  
  

  
    
  
  
  
 