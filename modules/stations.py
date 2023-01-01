from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.wrapper_generic_blocks import *
from collections import namedtuple as nt
from modules.helpers import set_label
from modules.helpers import counter
 



# газовые котлы - гвс
# газовые котлы - пар
# электрокотлы  - гвс
# электрокотлы  - пар


# ВИЭ

# турбины КЭС
			# 


# ПГУ КЭС
# тубины ТЭЦ
# малые ТЭЦ
# блок-станции(газ)
# ядерные реакторы


# проблемные энергоисточники
# ТК-330 - минская тэц-5
# ГТУ-125 - гродненская тэц-5
# ПГУ-222 - минская тэц-3





def get_station_method_by_energysystem(es, bl_lst, glob_gas_flow, glob_el_flow, station_list):
  
  
	index = 0
  
	def reset_index():
		nonlocal index 
		index = 0
		
	def inc_index():
		nonlocal index
		index = index + 1
		return index
        
	def get_renewables_source(renewables_type, install_power, fixed_load_profile):
		pass
  
	def get_el_boilers_hw(station_name, install_power, output_flow_T):
		pass

	def get_el_boilers_steam(station_name, install_power, output_flow_P):
		pass
  
	def get_gas_boilers_hw(station_name, install_power, output_flow_T):
		pass

	def get_gas_boilers_steam(station_name, install_power, output_flow_P):
		pass

	def get_small_chp(station_name, install_power, fixed_load_profile):
		pass
  
	def get_K_300(station_name, planning_outage):
		pass
 
	def get_K_160(station_name, planning_outage):
		pass

	def get_CCGT_427(station_name, planning_outage):
		pass	

	def get_CCGT_399(station_name, planning_outage):
		pass
    
    

	def get_t_250(station_name, output_flow_T):
		create_T_turb = get_chp_method_by_energy_system(es, bl_lst, 'Т')
		t = create_T_turb(
				index = inc_index(),
				station_name = station_name,
				block_name = 'Т-250',
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

	def get_t_110(station_name, output_flow_T):
		create_T_turb = get_chp_method_by_energy_system(es, bl_lst, 'Т')
		return create_T_turb(
				index = inc_index(),
				station_name = station_name,
				block_name = 'Т-110',
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

	def get_pt_60_t(station_name, output_flow_T):
		create_pt_60_t_turb = get_chp_method_by_energy_system(es, bl_lst, 'ПТ-Т')
		return create_pt_60_t_turb(
				index = inc_index(),
				station_name = station_name,
				block_name = 'ПТ-60',
				nominal_el_value = 60,
				min_power_fraction = 0.4,
				input_flow = glob_gas_flow,
				output_flow_el = glob_el_flow,
				output_flow_T = output_flow_T,
				nominal_input_T = 200,
				efficiency_T = 0.91,
				heat_to_el_T = 2.02,
				variable_costs = 0,
				boiler_efficiency = 1)

	def get_pt_60(station_name, output_flow_P, output_flow_T):
		create_pt_turb = get_chp_method_by_energy_system(es, bl_lst, 'ПТ')
		return create_pt_turb(
				index = inc_index(),
				station_name = station_name,
				block_name = 'ПТ-60',
				nominal_el_value = 60,
				min_power_fraction = 0.4,
				input_flow = glob_gas_flow,
				output_flow_el = glob_el_flow,
				output_flow_T = output_flow_T,
				output_flow_P = output_flow_P,
				nominal_input_t = 150,
				nominal_input_P = 300,
				efficiency_T = 0.91,
				efficiency_P = 0.91,
				heat_to_el_T = 2.02,
				heat_to_el_P = 3.8,
				variable_costs = 0,
				boiler_efficiency = 1)
  
	def get_p_50(station_name, output_flow_P):
		create_back_pressure_turb = get_chp_method_by_energy_system(es, bl_lst, 'Р')
		return create_back_pressure_turb(
				index = inc_index(),
				station_name = station_name,
				block_name = 'Р-50',
				nominal_el_value = 50,
				min_power_fraction = 0.35,
				input_flow = glob_gas_flow,
				output_flow_el = glob_el_flow,
				output_flow_P = output_flow_P,
				efficiency_P = 0.91,
				heat_to_el_P = 3.8,
				variable_costs = 0,
				boiler_efficiency = 1)
  
	def get_block_station_natural_gas(station_name):
		create_block_station_natural_gas = get_simple_transformers_method_by_energy_system(es, bl_lst, 'simple')
		return create_block_station_natural_gas(
			index = inc_index(),
			station_name = station_name,
			block_name = 'Блок-станции(газ)',
   
		)
  
	def get_vver_1200(station_name, variable_costs, full_load = False):
		create_npp_vver_1200 = get_simple_transformers_method_by_energy_system(es, bl_lst, 'NPP')
		return create_npp_vver_1200(
			index = inc_index(),
			station_name = station_name,
			station_type = 'АЭС',
			block_type = 'ВВЭР-1200',
			nominal_value = 1170,
			min_power_fraction = 1 if full_load else 0.75,
			output_flow = glob_el_flow,
			variable_costs = variable_costs
		)

  
	def get_vver_toi(station_name, variable_costs, full_load = False):
		create_npp_vver_toi = get_simple_transformers_method_by_energy_system(es, bl_lst, 'NPP')
		return create_npp_vver_toi(
			index = inc_index(),
			station_name = station_name,
			station_type = 'АЭС',
			block_type = 'ВВЭР-ТОИ',
			nominal_value = 1255,
			min_power_fraction = 1 if full_load else 0.5,
			output_flow = glob_el_flow,
			variable_costs = variable_costs
		)
  

	def create_test_station (station_name, heat_water_demand_data, steam_demand_date, planning_outage):
		reset_index()
		station_name = station_name
		hw_bus_name = 'Отопление+ГВС'
		create_source = get_sources_methods_by_energy_system(es, bl_lst)
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, 'абс')
  		# тепловые спросы - bus
		###############################################################
		hw_bus = create_buses(set_label(station_name, station_name))
		
		# турбоагрегаты, котлы и электрокотлы - transformer
		###############################################################
		t_250_1 = get_t_250(station_name, hw_bus)
		heat_source = create_source(set_label(station_name, 'дорогой источник ГВС'), hw_bus, 9999) 

		# тепловые потребители - sink
		###############################################################
		hw_sink = create_abs_demand(
		label = set_label(station_name, hw_bus_name, 'sink'),
		input_flow = hw_bus,
		demand_absolute_data = heat_water_demand_data)
		###############################################################
		el_tr_lst = [t_250_1]
		hw_tr_lst = [t_250_1, heat_source]
		steam_tr_lst = None
		hw_bus_lst = hw_bus
		steam_bus_lst = None
  

		return ({'эл': el_tr_lst,'ГВС': hw_tr_lst, 'Пар': steam_tr_lst},{'ГВС': hw_bus_lst, 'Пар': None})
     
  
  
	def create_Minskay_tec_4(station_name, heat_water_demand_data, steam_demand_date = None, planning_outage = None):
	#  startup options, planning outage
		reset_index()
		hw_bus_name = 'Отопление+ГВС'
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, sink_type= 'abs')
		create_simple_tr = get_simple_transformers_method_by_energy_system(es, bl_lst, block_type= 'simple')
		# тепловые спросы - bus
		###############################################################
		hw_bus = create_buses(set_label(station_name, hw_bus_name))
		steam_bus = None
		# турбоагрегаты, котлы и электрокотлы - transformer
		###############################################################
		pt_t_60 = get_pt_60_t(station_name, hw_bus)
		t_250_1 = get_t_250(station_name, hw_bus)
		t_250_2 = get_t_250(station_name, hw_bus)
		t_250_3 = get_t_250(station_name, hw_bus)
		t_110_1 = get_t_250(station_name, hw_bus)
		t_110_2 = get_t_250(station_name, hw_bus)
		el_boiler = create_simple_tr(set_label(station_name,'ЭК'), 1.163 * 137.6, glob_el_flow, hw_bus, 0.99, 0)
		# тепловые потребители - sink
		###############################################################
		hw_sink = create_abs_demand(
		label = set_label(station_name, hw_bus_name, 'sink'), 
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

	def create_Novopolockay_tec(station_name, heat_water_demand_data, steam_demand_date = None, planning_outage = None):
		#  startup options, planning outage
			reset_index()
			hw_bus_name = 'гвс'
			steam_bus_name = 'пар'
			create_buses = get_buses_method_by_energy_system(es)
			create_abs_demand = get_sinks_method_by_energy_system(es, bl_lst, sink_type= 'abs')
			create_simple_tr = get_simple_transformers_method_by_energy_system(es, bl_lst, block_type= 'simple')
			# тепловые спросы - bus
			###############################################################
			hw_bus = create_buses(set_label(station_name, hw_bus_name))
			steam_bus = create_buses(set_label(station_name, steam_bus_name))
			# турбоагрегаты, котлы и электрокотлы - transformer
			###############################################################
			[pt_60_el_1, pt_60_t_1, pt_60_p_1] = get_pt_60(station_name,steam_bus, hw_bus)
			[pt_60_el_2, pt_60_t_2, pt_60_p_2] = get_pt_60(station_name,steam_bus, hw_bus)
			[pt_60_el_3, pt_60_t_3, pt_60_p_3] = get_pt_60(station_name,steam_bus, hw_bus)
			p_50_1 = get_p_50(station_name, steam_bus)
			p_50_2 = get_p_50(station_name, steam_bus)
			# тепловые потребители - sink
			###############################################################
			hw_sink = create_abs_demand(
			label =  set_label(station_name, hw_bus_name, 'sink'), 
			input_flow = hw_bus,
			demand_absolute_data = heat_water_demand_data)
			###############################################################
			el = [pt_60_el_1, pt_60_el_2, pt_60_el_3, p_50_1, p_50_2]
			hw_chp = [pt_60_t_1, pt_60_t_2, pt_60_t_3]
			steam_chp = [pt_60_p_1, pt_60_p_2, pt_60_p_3, p_50_1, p_50_2]
			hw_gas_boilers = None
			hw_el_boilers = None
			steam_gas_boilers = None
			steam_el_boilers = None
			###############################################################
		# sink?
			return ({'э': el,
						'гвс-тэц': hw_chp, 'гвс-кот': hw_gas_boilers, 'гвс-эк': hw_el_boilers,
						'пар-тэц': steam_chp,'пар-кот': steam_gas_boilers, 'пар-эк': steam_el_boilers},
						{'гвс': hw_bus, 'пар': steam_bus})



	station_dict = {
		'Минская ТЭЦ-4': create_Minskay_tec_4,
		'Новополоцкая ТЭЦ':create_Novopolockay_tec,
		'Тестовая станция': create_test_station
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
	
		

	
 		
    
	
    
  


  
  

  
    
  
  
  
 