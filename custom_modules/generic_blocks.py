from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from custom_modules.helpers import set_label

class Generic_buses:
  
        def __init__(self, es) -> None:
            self.es = es

        
        def create_buses(self, *bus_list):
            res = []
            for bus_name in bus_list:
                res.append(solph.Bus(bus_name))
            self.es.add(*res)
            if len(res) == 1:
                return res[0]
            return res

class Generic_blocks:

        def __init__(self, es, block_collection) -> None:
            self.block_collection = block_collection
            self.es = es

        def create_simple_transformer(
            self,
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
            variable_costs
            ):
            tr = solph.components.Transformer(
            label= set_label(station_name, block_name, str(index)), 
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow: solph.Flow(nominal_value = nominal_value, variable_costs = variable_costs)},
            conversion_factors = {input_flow: 1 / efficiency, output_flow: 1},
            group_options = {'станция': station_name, 'тип станции': station_type, 'блок': block_name, 'тип блока': block_type, 'вид тепла': commodity_tag}
            )
            self.es.add(tr)
            if isinstance(self.block_collection, list):
                self.block_collection.append(tr) 
            return tr
    
        def create_simple_transformer_nonconvex(
            self,
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
                    group_options = {'станция': station_name, 'тип станции': station_type, 'блок': block_name, 'тип блока': block_type, 'вид тепла': commodity_tag, 'мощность':nominal_value, 'приоритет станции' : None}
            )
            self.es.add(tr)
            if isinstance(self.block_collection, list):
                self.block_collection.append(tr) 
            return tr

        def create_offset_transformer(
            self,
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
            boiler_efficiency = 1,
            ):
            P_out_max = nominal_value     										 # absolute nominal output power
            P_out_min = nominal_value * min_power_fraction                       # absolute minimal output power
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
                # fix = fixedGenerationData,
                nonconvex = solph.NonConvex())},
                outputs = {output_flow: solph.Flow(variable_costs = variable_costs)},
                coefficients = [c0, c1],
                group_options = {'станция': station_name, 'тип станции': station_type, 'блок': block_name, 'тип блока': block_type, 'вид тепла': commodity_tag}
            )
            self.es.add(tr)
            if isinstance(self.block_collection, list):
                self.block_collection.append(tr) 
            return tr

        def create_NPP_block(
            self,
            index,
            station_name,
            block_name,
            nominal_el_value,
            min_power_fraction,
            output_flow,
            variable_costs):
            npp_block = solph.components.Source(
            label= set_label(station_name, block_name, str(index)), 
            outputs = {output_flow: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, nonconvex = solph.NonConvex(), variable_costs = variable_costs)},
            group_options = {'станция': station_name, 'тип станции': 'АЭС', 'блок': block_name, 'тип блока': 'АЭС', 'вид тепла': 'нет'}
            )
            self.es.add(npp_block)
            if isinstance(self.block_collection, list):
                self.block_collection.append(npp_block) 
            return npp_block

        def create_chp_PT_turbine(
            self,
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
            el_inner_bus = Generic_buses(self.es).create_buses(set_label(station_name, block_name, str(index), 'электричество-промежуточное'))

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

            self.es.add(P_mode_tr, T_mode_tr, main_output_tr)
            if isinstance(self.block_collection, list):
                self.block_collection.append(P_mode_tr)
                self.block_collection.append(T_mode_tr)
                self.block_collection.append(main_output_tr)
            return [main_output_tr, P_mode_tr, T_mode_tr]
   
        def create_chp_PT_turbine_full_P_mode(
            self,
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
            self.es.add(pt_full_P_mode)
            if isinstance(self.block_collection, list):
                 self.block_collection.append(pt_full_P_mode)
            return pt_full_P_mode

        def create_chp_PT_turbine_full_T_mode(
            self,
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
            self.es.add(pt_full_T_mode)
            if isinstance(self.block_collection, list):
                 self.block_collection.append(pt_full_T_mode)
            return pt_full_T_mode

        def create_chp_T_turbine(
            self,
            index,
            station_name,
            block_name,
            nominal_el_value,
            max_el_value,
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
            
            # 669.175 - useful
            
            
            
            el_eff = (efficiency_T / (1+ heat_to_el_T)) * boiler_efficiency
            hw_eff = (heat_to_el_T * el_eff )
            # print(hw_eff/el_eff)
            efficiency_full_condensing_mode = efficiency_full_condensing_mode - efficiency_full_condensing_mode * (1- boiler_efficiency)
            # print(efficiency_full_condensing_mode)
            nominal_input_T = max_el_value/efficiency_full_condensing_mode
            # print(nominal_input_T)
                       
            p = nominal_el_value * min_power_fraction
            update_min_fraction = p/max_el_value
            # print(max_el_value*update_min_fraction)
            
            
            T_turbine = solph.components.ExtractionTurbineCHP (
            label= set_label(station_name, block_name, str(index)),
            inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T)},
            outputs = {output_flow_el: solph.Flow(nominal_value = max_el_value, min = update_min_fraction, variable_costs = variable_costs, nonconvex = solph.NonConvex()),
                                    output_flow_T: solph.Flow()
                                    },
            # conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
            conversion_factors = {output_flow_el: el_eff, output_flow_T: hw_eff},
            conversion_factor_full_condensation = {output_flow_el: efficiency_full_condensing_mode},
            group_options = {'станция': station_name, 'тип станции':'тэц', 'блок': block_name, 'тип блока': 'т', 'вид тепла': 'гвс'}
            )
            self.es.add(T_turbine)
            if isinstance(self.block_collection, list):
                 self.block_collection.append(T_turbine)
            return T_turbine

        def create_back_pressure_turbine(
            self,
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
            self.es.add(tr)
            if isinstance(self.block_collection, list):
                 self.block_collection.append(tr)
            return tr

        
class Generic_sinks:

        def __init__(self, es) -> None:
            # self.block_collection = block_collection
            self.es = es		

        def create_sink_absolute_demand(self, label, input_flow, demand_absolute_data):
            sink = solph.components.Sink(label=label, inputs = {input_flow: solph.Flow(nominal_value=1, fix = demand_absolute_data)})
            self.es.add(sink)
            # self.block_collection.append(sink)
            return sink	
        def create_sink_fraction_demand(self, label, input_flow, demand_profile, peak_load):
            sink = solph.components.Sink(label=label, inputs = {input_flow: solph.Flow(nominal_value = peak_load, fix = demand_profile)})
            self.es.add(sink)
            # self.block_collection.append(sink)
            return sink

class Generic_sources:

        def __init__(self, es, block_collection = None) -> None:
            self.block_collection = block_collection
            self.es = es
        
        def create_source(self, label, output_flow, variable_costs):
            source = solph.components.Source(label=label, outputs = {output_flow: solph.Flow(variable_costs = variable_costs)} )
            self.es.add(source)
            if isinstance(self.block_collection, list):
                 self.block_collection.append(source)
            return source

      
      
      
      

   
   