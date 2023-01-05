from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from modules.helpers import set_label

 
# создать электрокотел
# создать метод быстрого построения графиков
# сделать метод создания станции
#  (добавить в э все турбины,электрокотлы, станции со всеми настройками)

# получить sources
# получить simple transtormers
# получить sink
# получить bus 
# получить chp turbines
# получить npp

# разделать на функции по типам действий



##################################################################################################################
# Методы получения объектов bus различных типов
##################################################################################################################    
def get_sources_methods_by_energy_system(energy_system, block_collection):
	def create_source(label, output_flow, variable_costs):
		ng = solph.components.Source(label=label, outputs = {output_flow: solph.Flow(variable_costs = variable_costs)} )
		energy_system.add(ng)
		block_collection.append(ng)
		return ng
	return create_source
    
def get_sinks_method_by_energy_system(energy_system, block_collection, sink_type):
	def create_sink_absolute_demand(label, input_flow, demand_absolute_data):
		sink = solph.components.Sink(label=label, inputs = {input_flow: solph.Flow(nominal_value=1, fix = demand_absolute_data)})
		energy_system.add(sink)
		block_collection.append(sink)
		return sink	
	def create_sink_fraction_demand(label, input_flow, demand_profile, peak_load):
		sink = solph.components.Sink(label=label, inputs = {input_flow: solph.Flow(nominal_value = peak_load, fix = demand_profile)})
		energy_system.add(sink)
		block_collection.append(sink)
		return sink

	res_dict = {
		'abs': create_sink_absolute_demand,
		'rel': create_sink_fraction_demand,
	}

	if not isinstance(sink_type, list):
		if sink_type in res_dict:
			return res_dict[sink_type]
		else:
			raise Exception('параметр не является списком')

	if len(sink_type) == 0:
		raise Exception('cписок типов спросов пуст')
		
	res = []
	for sink in sink_type:
		if sink in res_dict:
			res += [res_dict[sink]]
   
	if len(res) != 0:
		return res
	else:
		raise Exception('не определено ни одного спроса')
  
  
##################################################################################################################
# Методы получения источников одного вида энергии (с одним входом) различных типов 
##################################################################################################################
def get_simple_transformers_method_by_energy_system(energy_system, block_collection, block_type):
	def create_simple_transformer(
		index,
		station_name,
		station_type,
		block_name,
		block_type,
		commodity_tag,
		nominal_value,
		input_flow,
		output_flow,
		efficiency,
		variable_costs):
		tr = solph.components.Transformer(
		label= set_label(station_name, block_name, str(index)), 
  	inputs = {input_flow: solph.Flow()},
		outputs = {output_flow: solph.Flow(nominal_value = nominal_value, variable_costs = variable_costs)},
		conversion_factors = {input_flow: 1 / efficiency, output_flow: 1},
		group_options = {'станция': station_name, 'тип станции': station_type, 'блок': block_name, 'тип блока': block_type, 'вид тепла': commodity_tag}
		)
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr
	def create_simple_transformer_nonconvex(
		index,
		station_name,
		station_type,
		block_name,
		block_type,
		commodity_tag,
		nominal_value,
		min_power_fraction,
		input_flow,
		output_flow,
		efficiency,
		variable_costs):
		tr = solph.components.Transformer(
		label= set_label(station_name, block_name, str(index)), 
		inputs = {input_flow: solph.Flow()},
		outputs = {output_flow: solph.Flow( nominal_value = nominal_value, min = min_power_fraction, variable_costs = variable_costs, nonconvex = solph.NonConvex())},
		conversion_factors = {input_flow: 1 / efficiency, output_flow: 1},
				group_options = {'станция': station_name, 'тип станции': station_type, 'блок': block_name, 'тип блока': block_type, 'вид тепла': commodity_tag}
		)
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr
	def create_NPP_block(
		index,
		station_name,
		block_name,
		nominal_value,
		min_power_fraction,
		output_flow,
		variable_costs):
			npp_block = solph.components.Source(
			label= set_label(station_name, block_name, str(index)), 
			outputs = {output_flow: solph.Flow(nominal_value = nominal_value, min = min_power_fraction, nonconvex = solph.NonConvex(), variable_costs = variable_costs)},
			group_options = {'станция': station_name, 'тип станции': 'АЭС', 'блок': block_name, 'тип блока': 'АЭС', 'вид тепла': 'нет'}
			)
			energy_system.add(npp_block)
			block_collection.append(npp_block) 
			return npp_block
	def create_offset_transformer(
		index,
		station_name,
		station_type,
		block_name,
		block_type,
		commodity_tag,
		nominal_value,
		input_flow,
		output_flow,
		efficiency_min,
		efficiency_max,
		min_power_fraction,
		variable_costs = 0,
		boiler_efficiency = 1):
		P_out_max = nominal_value     										 # absolute nominal output power
		P_out_min = nominal_value * min_power_fraction     # absolute minimal output power
		P_in_min = P_out_min / (efficiency_min * boiler_efficiency)
		P_in_max = P_out_max / (efficiency_max * boiler_efficiency)
		c1 = (P_out_max-P_out_min) / (P_in_max-P_in_min)
		c0 = P_out_max - c1 * P_in_max

		tr = solph.components.OffsetTransformer(
			label= set_label(station_name, block_name, str(index)), 
   		inputs = {input_flow: solph.Flow(
			nominal_value = P_in_max,
			max = 1,
			min = P_in_min/P_in_max,
			nonconvex = solph.NonConvex())},
			outputs = {output_flow: solph.Flow(variable_costs = variable_costs)},
			coefficients = [c0, c1],
			group_options = {'станция': station_name, 'тип станции': station_type, 'блок': block_name, 'тип блока': block_type, 'вид тепла': commodity_tag}
		)
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr

	res_dict = {
	'simple': create_simple_transformer,
	'simple_nonconvex': create_simple_transformer_nonconvex,
	'offset': create_offset_transformer,
	'NPP': create_NPP_block,
}

	if not isinstance(block_type, list):
		if block_type in res_dict:
			return res_dict[block_type]
		else:
			raise Exception('параметр не является списком')

	if len(block_type) == 0:
		raise Exception('cписок типов турбин пуст')
		
	res = []
	for block in block_type:
		if block in res_dict:
			res += [res_dict[block]]
		
	if len(res) != 0:
		return res
	else:
		raise Exception('не определено ни одной турбины')
		
	     

def get_buses_method_by_energy_system(energy_system):
  # проверки
	def get_bus_list_by_name(*bus_list):
		res = []
		for bus_name in bus_list:
			res.append(solph.Bus(bus_name))
		energy_system.add(*res)
		if len(res) == 1:
			return res[0]
		return res
	return get_bus_list_by_name
    
    
##################################################################################################################
# Методы получения турбин ТЭЦ различных типов    
##################################################################################################################
def get_chp_method_by_energy_system(energy_system, block_collection, turbine_type):
	def create_chp_PT_turbine(
		index,
		station_name,
		block_name,
		nominal_el_value,
		min_power_fraction,
		input_flow,
		output_flow_el, 
		output_flow_T, 
		output_flow_P,
		nominal_input_t,
		nominal_input_P,
		efficiency_T,
		efficiency_P,
		heat_to_el_P,
		heat_to_el_T,
		variable_costs = 0,
		boiler_efficiency = 1):
    
		# кпд котла?
		create_bus = get_buses_method_by_energy_system(energy_system)
		# el_inner_bus = create_bus(str(index) + '_' + label + '_электричество-промежуточное')
		el_inner_bus = create_bus(set_label(station_name, block_name, str(index), 'электричество-промежуточное'))
  
		P_mode_tr = solph.components.Transformer (
    label= set_label(station_name, block_name, str(index), 'П_режим'),
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_P)},
		outputs = {el_inner_bus: solph.Flow(),
								output_flow_P: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_P) / efficiency_P, el_inner_bus: 1, output_flow_P: heat_to_el_P},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'пт', 'вид тепла': 'пар'}
		
  )

		T_mode_tr = solph.components.Transformer (
    label= set_label(station_name, block_name, str(index), 'Т_режим'),
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_t)},
		outputs = {output_flow_T: solph.Flow(),
								el_inner_bus: solph.Flow()
             },
  	conversion_factors = {input_flow: (1 + heat_to_el_T) / efficiency_T, el_inner_bus: 1, output_flow_T: heat_to_el_T},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'пт', 'вид тепла': 'гвс' }
   )

		main_output_tr = solph.components.Transformer (
		label= set_label(station_name, block_name, str(index), 'электроэнергия'),
		inputs = {el_inner_bus: solph.Flow()},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, nonconvex = solph.NonConvex(), variable_costs = variable_costs)},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'пт', 'вид тепла': 'электричество'}
  ) 

		energy_system.add(P_mode_tr, T_mode_tr, main_output_tr)
		block_collection.append(P_mode_tr)
		block_collection.append(T_mode_tr)
		block_collection.append(main_output_tr)
		return [main_output_tr, P_mode_tr, T_mode_tr]

	def create_chp_PT_turbine_full_P_mode(
		index,
		station_name,
		block_name,
		nominal_el_value,
		min_power_fraction,
		input_flow,
		output_flow_el,
		output_flow_P,
		nominal_input_P,
		efficiency_P,
		heat_to_el_P,
		variable_costs = 0,
   boiler_efficiency = 1):
		# кпд котла?
		pt_full_P_mode = solph.components.Transformer (
		label= set_label(station_name, block_name, str(index), 'электроэнергия_чистый_П_режим'),
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_P)},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs),
								output_flow_P: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_P) / (efficiency_P * boiler_efficiency), output_flow_el: 1, output_flow_P: heat_to_el_P},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'пт', 'вид тепла': 'пар'}
  )
		energy_system.add(pt_full_P_mode)
		block_collection.append(pt_full_P_mode) 
		return pt_full_P_mode

	def create_chp_PT_turbine_full_T_mode(
		index,
		station_name,
		block_name,
		nominal_el_value,
		min_power_fraction,
		input_flow,
		output_flow_el,
		output_flow_T,
		nominal_input_T,
		efficiency_T,
		heat_to_el_T,
		variable_costs = 0,
		boiler_efficiency = 1):
		# кпд котла?
		pt_full_T_mode = solph.components.Transformer (
		label= set_label(station_name, block_name, str(index), 'электроэнергия_чистый_Т_режим'),
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T)},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs),
								output_flow_T: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'пт', 'вид тепла': 'гвс'}
  )
		energy_system.add(pt_full_T_mode)
		block_collection.append(pt_full_T_mode) 
		return pt_full_T_mode

	def create_chp_T_turbine(
		index,
		station_name,
		block_name,
		nominal_el_value,
		min_power_fraction,
		input_flow,
		output_flow_el,
		output_flow_T,
		nominal_input_T,
		efficiency_T,
		heat_to_el_T,
		efficiency_full_condensing_mode,
		variable_costs = 0,
		boiler_efficiency = 1):
		# кпд котла?
     
		T_turbine = solph.components.ExtractionTurbineCHP (
		label= set_label(station_name, block_name, str(index)),
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T)},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs),
								output_flow_T: solph.Flow()
               },
  	conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
		conversion_factor_full_condensation = {output_flow_el: efficiency_full_condensing_mode},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'т', 'вид тепла': 'гвс'}
   )
		energy_system.add(T_turbine)
		block_collection.append(T_turbine) 
		return T_turbine


	def create_back_pressure_turbine(
		index,
		station_name,
		block_name,
		nominal_el_value,
		min_power_fraction, 
		input_flow,
		output_flow_el,
		output_flow_P,
		heat_to_el_P,
		efficiency_P,
		boiler_efficiency = 1,
		variable_costs = 0):
		tr = solph.components.Transformer(
		label= set_label(station_name, block_name, str(index)),
		inputs = {input_flow: solph.Flow()},
		outputs = {output_flow_el: solph.Flow( nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs, nonconvex = solph.NonConvex()),
							output_flow_P: solph.Flow()},
		conversion_factors = {input_flow: (1 + heat_to_el_P) /(efficiency_P * boiler_efficiency), output_flow_el: 1, output_flow_P: heat_to_el_P},
		group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'р', 'вид тепла': 'пар'}
  ) 
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr

	res_dict = {
		'ПТ': create_chp_PT_turbine,
		'Т': create_chp_T_turbine,
		'Р': create_back_pressure_turbine,
		'ПТ-Т': create_chp_PT_turbine_full_T_mode,
		'ПТ-П': create_chp_PT_turbine_full_P_mode,
	}

	if not isinstance(turbine_type, list):
		if turbine_type in res_dict:
			return res_dict[turbine_type]
		else:
			raise Exception('параметр не является списком')

	if len(turbine_type) == 0:
		raise Exception('cписок типов турбин пуст')
		
	res = []
	for turb_type in turbine_type:
		if turb_type in res_dict:
			res += [res_dict[turb_type]]
   
	if len(res) != 0:
		return res
	else:
		raise Exception('не определено ни одной турбины')
   
     
    

    
  

 
    
				
   
    
			

  
  

  
    
  
  
  
 