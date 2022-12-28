from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt

 

# создать турбину типа Т
# создать турбину типа Р
# создать турбину типа ПТ
# создать электрокотел
# создать метод быстрого построения графиков
# сделать метод создания станции
#  (добавить в э все турбины,электрокотлы, станции со всеми настройками)


def get_blocks_method_by_energy_system(energy_system):

	def create_back_Trasformer(label, input_flow, output_flow, variable_costs):
 		 # добавить проверки 
		tr =  solph.components.Transformer(
		label = label,
		inputs = {input_flow: solph.Flow()},output_flow = {output_flow: solph.Flow(variable_costs = variable_costs)}
		)
		energy_system.add(tr)
		
	def get_bus_list_by_name(*bus_list):
		res = []
		for bus_name in bus_list:
			res.append(solph.Bus(bus_name))
			energy_system.add(res[-1])
		return res

	def create_source(label, output_flow, variable_costs):
		ng = solph.constraints.Source(label=label, outputs = {output_flow: solph.Flow(variable_costs = variable_costs)} )
		energy_system.add(ng)
		return ng
	
	def create_sink_absolute_demand(label, input_flow, demand_absolute_data):
		sink = solph.components.Sink(label=label, inputs = {input_flow: solph.Flow(nominal_value=1, fix = demand_absolute_data)})
		energy_system.add(sink)
		return sink	

	def create_sink_fraction_demand(label, input_flow, demand_profile, peak_load):
		sink = solph.components.Sink(label=label, inputs = {input_flow: solph.Flow(nominal_value = peak_load, fix = demand_profile)})
		energy_system.add(sink)
		return sink


	def create_simple_transformer(label, nominal_value, input_flow, output_flow, efficiency, variable_costs):
		tr = solph.components.Transformer(
		label=label, 
  	inputs = {input_flow: solph.Flow()},
		outputs = {output_flow: solph.Flow(nominal_value = nominal_value, variable_costs = variable_costs)},
		conversion_factors = {input_flow: 1 / efficiency, output_flow: 1}
		)
		energy_system.add(tr)
		return tr

	def create_simple_transformer_nonconvex(label, nominal_value, min_power_fraction, input_flow, output_flow, efficiency, variable_costs):
		tr = solph.components.Transformer(
		label=label, 
		inputs = {input_flow: solph.Flow()},
		outputs = {output_flow: solph.Flow( nominal_value = nominal_value, min = min_power_fraction, variable_costs = variable_costs, nonconvex = solph.NonConvex())},
		conversion_factors = {input_flow: 1 / efficiency, output_flow: 1}
		)
		energy_system.add(tr)
		return tr

	def create_NPP_block(label, nominal_value, min_power_fraction, output_flow, variable_costs):
			npp_block = solph.components.Source(
			label = label,
			outputs = {output_flow: solph.Flow(nominal_value = nominal_value, min = min_power_fraction, nonconvex = solph.NonConvex( ), variable_costs = variable_costs)}
			)
			energy_system.add(npp_block)
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
		return tr

	def create_pt_turbine(label, nominal_el_value, min_power_fraction, input_flow, output_flow_el, output_flow_T, output_flow_P, nominal_input_t, nominal_input_P, efficiency_T, efficiency_P, heat_to_el_P, heat_to_el_T, variable_costs = 0, boiler_efficiency = 1):
		heat_water_bus = solph.Bus( label + 'heat_water_bus')
		steam_bus = solph.Bus( label + 'steam_bus')
		electricity_inner_bus = solph.Bus(label + 'electricity_inner_bus')

		P_mode_tr = solph.components.Transformer (
    label =  'P_mode_tr',
		inputs = {natural_gas_global_bus: solph.Flow(nominal_value = 305.38)},
		outputs = {chp_pt_60_electricity_inner_bus: solph.Flow(),
								steam_bus: solph.Flow()
               },
		conversion_factors = {natural_gas_global_bus: (1 + 3.8) / 0.91, chp_pt_60_electricity_inner_bus: 1, steam_bus: 3.8 }
 ) 


	return [create_back_Trasformer, get_bus_list_by_name, create_source]
    
	
    
  


  
  

  
    
  
  
  
 