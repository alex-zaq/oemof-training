from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
 

# создать турбину типа Т
# создать турбину типа Р

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

    
def get_sources_methods_by_energy_system(energy_system, block_collection):
	def create_source(label, output_flow, variable_costs):
		ng = solph.components.Source(label=label, outputs = {output_flow: solph.Flow(variable_costs = variable_costs)} )
		energy_system.add(ng)
		block_collection.append(ng)
		return ng
	return [create_source]
    
def get_sinks_method_by_energy_system(energy_system, block_collection):
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
	return [create_sink_absolute_demand, create_sink_fraction_demand]
  
  
##################################################################################################################
# Методы получения источников одного вида энергии     
##################################################################################################################
def get_simple_transformers_method_by_energy_system(energy_system, block_collection):
	def create_simple_transformer(label, nominal_value, input_flow, output_flow, efficiency, variable_costs):
		tr = solph.components.Transformer(
		label=label, 
  	inputs = {input_flow: solph.Flow()},
		outputs = {output_flow: solph.Flow(nominal_value = nominal_value, variable_costs = variable_costs)},
		conversion_factors = {input_flow: 1 / efficiency, output_flow: 1}
		)
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr
	def create_simple_transformer_nonconvex(label, nominal_value, min_power_fraction, input_flow, output_flow, efficiency, variable_costs):
		tr = solph.components.Transformer(
		label=label, 
		inputs = {input_flow: solph.Flow()},
		outputs = {output_flow: solph.Flow( nominal_value = nominal_value, min = min_power_fraction, variable_costs = variable_costs, nonconvex = solph.NonConvex())},
		conversion_factors = {input_flow: 1 / efficiency, output_flow: 1}
		)
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr
	def create_NPP_block(label, nominal_value, min_power_fraction, output_flow, variable_costs):
			npp_block = solph.components.Source(
			label = label,
			outputs = {output_flow: solph.Flow(nominal_value = nominal_value, min = min_power_fraction, nonconvex = solph.NonConvex( ), variable_costs = variable_costs)}
			)
			energy_system.add(npp_block)
			block_collection.append(npp_block) 
			return npp_block
	def create_offset_transformer(label, nominal_value, input_flow, output_flow, efficiency_min, efficiency_max, min_power_fraction, variable_costs = 0, boiler_efficiency = 1):
		P_out_max = nominal_value     										 # absolute nominal output power
		P_out_min = nominal_value * min_power_fraction     # absolute minimal output power
		P_in_min = P_out_min / (efficiency_min * boiler_efficiency)
		P_in_max = P_out_max / (efficiency_max * boiler_efficiency)
		c1 = (P_out_max-P_out_min)/(P_in_max-P_in_min)
		c0 = P_out_max - c1*P_in_max

		tr = solph.components.OffsetTransformer(
			label=label, inputs = {input_flow: solph.Flow(
			nominal_value = nominal_value,
			max = 1,
			min = P_in_min/P_in_max,
			nonconvex = solph.NonConvex())},
			outputs = {output_flow: solph.Flow(variable_costs = variable_costs)},
			coefficients = [c0, c1]
		)
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr
 
	return [create_simple_transformer, create_simple_transformer_nonconvex, create_NPP_block, create_offset_transformer]
    

def get_buses_method_by_energy_system(energy_system):
	def get_bus_list_by_name(*bus_list):
		res = []
		for bus_name in bus_list:
			res.append(solph.Bus(bus_name))
		energy_system.add(*res)
		return res
	return [get_bus_list_by_name]
    
    
##################################################################################################################
# Методы получения турбин ТЭЦ различных типов    
##################################################################################################################
def get_chp_method_by_energy_system(energy_system, block_collection, turbine_type = None):
	def create_chp_PT_turbine(label, nominal_el_value, min_power_fraction, input_flow, output_flow_el, output_flow_T, output_flow_P, nominal_input_t, nominal_input_P, efficiency_T, efficiency_P, heat_to_el_P, heat_to_el_T, variable_costs = 0, boiler_efficiency = 1):
    
		# кпд котла?
		[el_inner_bus] = get_buses_method_by_energy_system(energy_system).get_bus_list_by_name(label + 'el_inner_bus')
  
		P_mode_tr = solph.components.Transformer (
    label =  label + 'P_mode',
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_P)},
		outputs = {el_inner_bus: solph.Flow(),
								output_flow_P: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_P) / efficiency_P, el_inner_bus: 1, output_flow_P: heat_to_el_P})

		T_mode_tr = solph.components.Transformer (
    label = label + 'T_mode',
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_t)},
		outputs = {output_flow_T: solph.Flow(),
								el_inner_bus: solph.Flow()
             },
  	conversion_factors = {input_flow: (1 + heat_to_el_T) / efficiency_T, el_inner_bus: 1, output_flow_T: heat_to_el_T})

		main_output_tr = solph.components.Transformer (
    label = label + 'main_output',
		inputs = {el_inner_bus: solph.Flow()},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, nonconvex = solph.NonConvex(), variable_costs = variable_costs)}) 

		energy_system.add(P_mode_tr, T_mode_tr, main_output_tr)
		block_collection.append(P_mode_tr, T_mode_tr, main_output_tr) 

	def create_chp_PT_turbine_full_P_mode(label, nominal_el_value, min_power_fraction, input_flow, output_flow_el, output_flow_P, nominal_input_P, efficiency_P, heat_to_el_P, variable_costs = 0, boiler_efficiency = 1):
		# кпд котла?
		pt_full_P_mode = solph.components.Transformer (
    label =  label + 'main_output_full_P_mode',
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_P)},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs),
								output_flow_P: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_P) / (efficiency_P * boiler_efficiency), output_flow_el: 1, output_flow_P: heat_to_el_P})
		energy_system.add(pt_full_P_mode)
		block_collection.append(pt_full_P_mode) 
		return pt_full_P_mode

	def create_chp_PT_turbine_full_T_mode(label, nominal_el_value, min_power_fraction, input_flow, output_flow_el, output_flow_T, nominal_input_T, efficiency_T, heat_to_el_T, variable_costs = 0, boiler_efficiency = 1):
		# кпд котла?
		pt_full_T_mode = solph.components.Transformer (
    label =  label + 'main_output_full_P_mode',
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T)},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs),
								output_flow_T: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T})
		energy_system.add(pt_full_T_mode)
		block_collection.append(pt_full_T_mode) 
		return pt_full_T_mode

	def create_chp_T_turbine(label, nominal_el_value, min_power_fraction, input_flow, output_flow_el, output_flow_T, nominal_input_T, efficiency_T, heat_to_el_T,efficiency_full_condensing_mode, variable_costs = 0, boiler_efficiency = 1):
		# кпд котла?
     
		T_turbine = solph.components.ExtractionTurbineCHP (
    label =  label,
		inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T)},
		outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = variable_costs),
								output_flow_T: solph.Flow()
               },
		conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
		conversion_factor_full_condensation = efficiency_full_condensing_mode
	
   )
		energy_system.add(T_turbine)
		block_collection.append(T_turbine) 
		return T_turbine


	def create_back_pressure_turbine(label, nominal_value, min_power_fraction, input_flow, output_flow_el, output_flow_P, heat_to_el_P, efficiency_P, boiler_efficiency = 1 , variable_costs = 0):
		tr = solph.components.Transformer(
		label=label, 
		inputs = {input_flow: solph.Flow()},
		outputs = {output_flow_el: solph.Flow( nominal_value = nominal_value, min = min_power_fraction, variable_costs = variable_costs, nonconvex = solph.NonConvex()),
							output_flow_P: solph.Flow()},
		conversion_factors = {input_flow: (1 + heat_to_el_P) /(efficiency_P * boiler_efficiency), output_flow_el: 1, output_flow_P: heat_to_el_P}) 
		energy_system.add(tr)
		block_collection.append(tr) 
		return tr

	if turbine_type:
		if turbine_type == 'ПТ':
			return [create_chp_PT_turbine, create_chp_PT_turbine_full_P_mode, create_chp_PT_turbine_full_T_mode]
		elif turbine_type == 'Т':
			return [create_chp_T_turbine]
		elif turbine_type == 'Р':
			return [create_back_pressure_turbine]
 
	return [create_chp_PT_turbine, create_chp_PT_turbine_full_P_mode, create_chp_PT_turbine_full_T_mode,create_chp_T_turbine,create_back_pressure_turbine]
    
				
   
    
			

  
  

  
    
  
  
  
 