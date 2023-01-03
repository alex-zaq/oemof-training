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
# from modules.helpers import counter
 

def get_station_method_by_energysystem(es, global_block_list, glob_gas_flow, glob_el_flow, station_list):
  
	index = 0
	def reset_index():
		nonlocal index 
		index = 0
	def inc_index():
		nonlocal index
		index = index + 1
		return index
  
  
#################################################################################
# Электрокотел (пар, гвс)
#################################################################################
	def get_el_boilers(station_name, install_power, output_flow, commodity_tag, variable_costs):
		create_el_boilers = get_simple_transformers_method_by_energy_system(es, global_block_list, 'simple')
		return create_el_boilers (
			index = inc_index(),
			station_name = station_name,
			station_type = None,
			block_name = set_label('ЭК', commodity_tag),
			block_type =  set_label('ЭК', commodity_tag),
			commodity_tag = commodity_tag,
			nominal_value = install_power,
			input_flow = glob_el_flow,
			output_flow = output_flow,
			efficiency = 0.99,
			variable_costs = variable_costs,
		)
##################################################################################################################################################################
# Газовый котел (пар, гвс)
#################################################################################
	def get_gas_boilers(station_name, install_power, output_flow, commodity_tag, variable_costs):
		create_gas_boilers = get_simple_transformers_method_by_energy_system(es, global_block_list, 'simple')
		return create_gas_boilers (
		index = inc_index(),
		station_name = station_name,
		station_type = None,
		block_name = set_label('КОТ', commodity_tag),
		block_type =  set_label('КОТ', commodity_tag),
		commodity_tag = commodity_tag,
		nominal_value = install_power,
		input_flow = glob_gas_flow,
		output_flow = output_flow,
		efficiency = 0.90,
		variable_costs = variable_costs,
		)
#################################################################################
# конденсационные турбины ГРЭС Белэнерго  (электроэнергия)
#################################################################################
	def get_k_160(station_name, planning_outage):
		create_k_160 = get_simple_transformers_method_by_energy_system(es, global_block_list, 'offset')
		return create_k_160(
			index = inc_index(),
			station_name = station_name,
			station_type = 'КЭС',
			block_name = 'К-160',
			block_type = 'К',
			commodity_tag = None,
			nominal_value = 160,
			input_flow = glob_gas_flow,
			output_flow = glob_el_flow,
			efficiency_min = 0.39,
			efficiency_max = 0.42,
			min_power_fraction = 0.4,
			variable_costs = 0,
			boiler_efficiency = 1   
		)

	def get_k_175(station_name, planning_outage):
		create_k_175 = get_simple_transformers_method_by_energy_system(es, global_block_list, 'offset')
		return create_k_175(
			index = inc_index(),
			station_name = station_name,
			station_type = 'КЭС',
			block_name = 'К-175',
			block_type = 'К',
			commodity_tag = None,
			nominal_value = 175,
			input_flow = glob_gas_flow,
			output_flow = glob_el_flow,
			efficiency_min = 0.39,
			efficiency_max = 0.43,
			min_power_fraction = 0.4,
			variable_costs = 0,
			boiler_efficiency = 1   
		)

	def get_k_300(station_name, planning_outage):
		create_k_300 = get_simple_transformers_method_by_energy_system(es, global_block_list, 'offset')
		return create_k_300(
		index = inc_index(),
		station_name = station_name,
		station_type = 'КЭС',
		block_name = 'К-300',
		block_type = 'К',
		commodity_tag = None,
		nominal_value = 300,
		input_flow = glob_gas_flow,
		output_flow = glob_el_flow,
		efficiency_min = 0.39,
		efficiency_max = 0.44,
		min_power_fraction = 0.4,
		variable_costs = 0,
		boiler_efficiency = 1   
	)

#################################################################################
# парогазовые установки ГРЭС Белэнерго (электроэнергия)
#################################################################################
	def get_ccgt_399(station_name, planning_outage):
		create_ccgt_399 = get_simple_transformers_method_by_energy_system(es, global_block_list, 'offset')
		return create_ccgt_399(
		index = inc_index(),
		station_name = station_name,
		station_type = 'КЭС',
		block_name = 'ПГУ-399',
		block_type = 'ПГУ-КЭС',
		commodity_tag = None,
		nominal_value = 399,
		input_flow = glob_gas_flow,
		output_flow = glob_el_flow,
		efficiency_min = 0.43,
		efficiency_max = 0.56,
		min_power_fraction = 0.4,
		variable_costs = 0,
		boiler_efficiency = 1   
	)

	def get_ccgt_427(station_name, planning_outage):
		create_ccgt_427 = get_simple_transformers_method_by_energy_system(es, global_block_list, 'offset')
		return create_ccgt_427(
		index = inc_index(),
		station_name = station_name,
		station_type = 'КЭС',
		block_name = 'ПГУ-427',
		block_type = 'ПГУ-КЭС',
		commodity_tag = None,
		nominal_value = 427,
		input_flow = glob_gas_flow,
		output_flow = glob_el_flow,
		efficiency_min = 0.43,
		efficiency_max = 0.59,
		min_power_fraction = 0.4,
		variable_costs = 0,
		boiler_efficiency = 1   
	)
#################################################################################
# теплофикационные турбины крупных ТЭЦ Белэнерго (электроэнергия, гвс, пар)
#################################################################################
	def get_t_250(station_name, output_flow_T):
		create_T_turb = get_chp_method_by_energy_system(es, global_block_list, 'Т')
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
		create_T_turb = get_chp_method_by_energy_system(es, global_block_list, 'Т')
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
		create_pt_60_t_turb = get_chp_method_by_energy_system(es, global_block_list, 'ПТ-Т')
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
		create_pt_turb = get_chp_method_by_energy_system(es, global_block_list, 'ПТ')
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
  
	def get_pt_135(station_name, output_flow_P, output_flow_T):
		create_pt_turb = get_chp_method_by_energy_system(es, global_block_list, 'ПТ')
		return create_pt_turb(
		index = inc_index(),
		station_name = station_name,
		block_name = 'ПТ-135',
		nominal_el_value = 135,
		min_power_fraction = 0.4,
		input_flow = glob_gas_flow,
		output_flow_el = glob_el_flow,
		output_flow_T = output_flow_T,
		output_flow_P = output_flow_P,
		nominal_input_t = 300,
		nominal_input_P = 600,
		efficiency_T = 0.91,
		efficiency_P = 0.91,
		heat_to_el_T = 2.02,
		heat_to_el_P = 3.8,
		variable_costs = 0,
		boiler_efficiency = 1)

  
	def get_p_50(station_name, output_flow_P):
		create_back_pressure_turb = get_chp_method_by_energy_system(es, global_block_list, 'Р')
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
  
	def get_ccgt_chp_222(station_name, planning_outage):  # теплофикационная ПГУ
		pass	
#################################################################################
# Блок-станции(газ) (электроэнергия)
#################################################################################
	def get_block_station_ng(station_name):
		create_block_station_natural_gas = get_simple_transformers_method_by_energy_system(es, global_block_list, 'simple')
		return create_block_station_natural_gas(
			index = inc_index(),
			station_name = station_name,
			block_name = 'Блок-станции(газ)',
		)
#################################################################################
# Малые ТЭЦ Белэнерго (электроэнергия, гвс, пар?)
#################################################################################  
	def get_small_chp(station_name, install_power, fixed_load_profile):
		pass
#################################################################################
# АЭС (электроэнергия)
#################################################################################
	def get_vver_1200(station_name, variable_costs, full_load = False):
		create_npp_vver_1200 = get_simple_transformers_method_by_energy_system(es, global_block_list, 'NPP')
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
		create_npp_vver_toi = get_simple_transformers_method_by_energy_system(es, global_block_list, 'NPP')
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
################################################################################# 
# Опциональные энергоисточники
################################################################################# 
	def get_vver_600(station_name):
		pass	
 
	def get_npp_300(station_name):
		pass	
  
	def get_smr_ritm_200(station_name):
		pass	

	def get_storage(station_name, capacity, eff_in, eff_out):
		pass

	def get_renewables_source(renewables_type, install_power, fixed_load_profile):
		pass

	def get_ocgt_25(station_name):
		pass
			
	def get_ocgt_100(station_name):
		pass
			
	def get_ocgt_125(station_name):
		pass			
################################################################################# 
################################################################################# 
  
  

	def create_test_station (station_name, heat_water_demand_data, steam_demand_date, planning_outage):
		'тестовая станция'		
		reset_index()
		station_name = station_name
		hw_bus_name = 'Отопление+ГВС'
		create_source = get_sources_methods_by_energy_system(es, global_block_list)
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, global_block_list, 'абс')
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
     
  
  
	def create_Minskay_tec_4(station_name, heat_water_demand_data, steam_demand = None, planning_outage = None):
		'Минская ТЭЦ-4'
		reset_index()
		hw_bus_name = 'гвс'
		create_buses = get_buses_method_by_energy_system(es)
		create_abs_demand = get_sinks_method_by_energy_system(es, global_block_list, sink_type= 'abs')
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
		el_boilers_hw = get_el_boilers(station_name, 1.163 * 137.6, hw_bus, 'гвс' , 0)
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
		hw_el_boilers = [el_boilers_hw]
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
			'Новополоцкая ТЭЦ'
		#  startup options, planning outage
			reset_index()
			hw_bus_name = 'гвс'
			steam_bus_name = 'пар'
			create_buses = get_buses_method_by_energy_system(es)
			create_abs_demand = get_sinks_method_by_energy_system(es, global_block_list, sink_type= 'abs')
			create_simple_tr = get_simple_transformers_method_by_energy_system(es, global_block_list, block_type= 'simple')
			# тепловые спросы - bus
			###############################################################
			hw_bus = create_buses(set_label(station_name, hw_bus_name))
			steam_bus = create_buses(set_label(station_name, steam_bus_name))
			# турбоагрегаты, котлы и электрокотлы - transformer
			###############################################################
			# пт-60 - 3 шт. р-50 - 2 шт.
			###############################################################
			[pt_60_el_1, pt_60_t_1, pt_60_p_1] = get_pt_60(station_name, steam_bus, hw_bus)
			[pt_60_el_2, pt_60_t_2, pt_60_p_2] = get_pt_60(station_name, steam_bus, hw_bus)
			[pt_60_el_3, pt_60_t_3, pt_60_p_3] = get_pt_60(station_name, steam_bus, hw_bus)
			p_50_1 = get_p_50(station_name, steam_bus)
			p_50_2 = get_p_50(station_name, steam_bus)
			el_boilers_steam = get_el_boilers(station_name, 1.163 * 137.6, steam_bus, 'пар' , 0)
			gas_boilers_steam = get_gas_boilers(station_name, 500, steam_bus, 'пар', 0 )
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
			steam_gas_boilers = [gas_boilers_steam]
			steam_el_boilers = [el_boilers_steam]
			###############################################################
		# sink?
			return ({'э': el,
						'гвс-тэц': hw_chp, 'гвс-кот': hw_gas_boilers, 'гвс-эк': hw_el_boilers,
						'пар-тэц': steam_chp,'пар-кот': steam_gas_boilers, 'пар-эк': steam_el_boilers},
						{'гвс': hw_bus, 'пар': steam_bus})


	def create_Bel_Npp(station_name, planning_outage = None):
		'Белорусская АЭС'
		reset_index()
		vver_1200_1 = get_vver_1200(station_name, -999, True)
		vver_1200_2 = get_vver_1200(station_name, -999, True)
		el = [vver_1200_1, vver_1200_2]
		return el
   

	station_dict = {
		'Минская ТЭЦ-4': create_Minskay_tec_4,
		'Новополоцкая ТЭЦ':create_Novopolockay_tec,
		'Белорусская АЭС': create_Bel_Npp,
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
	
		

	
 		
    
	
    
  


  
  

  
    
  
  
  
 