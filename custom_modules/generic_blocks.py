from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from custom_modules.helpers import set_label
from copy import deepcopy

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

        def __init__(self, es) -> None:
            # self.block_collection = block_collection
            self.es = es

        def create_simple_transformer(
            self,
            nominal_value,
            input_flow,
            output_flow,
            efficiency,
            variable_costs,
            group_options
            ):
            tr = solph.components.Transformer(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow: solph.Flow(nominal_value = nominal_value, variable_costs = variable_costs)},
            conversion_factors = {input_flow: 1 / efficiency, output_flow: 1},
            )
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(tr) 
            return tr
    
        def create_simple_transformer_with_fixed_load(
            self,
            nominal_value,
            input_flow,
            output_flow,
            efficiency,
            variable_costs,
            extra_variable_cost,
            group_options,
            fixed_el_load_data_rel
        ):
            tr = solph.components.Transformer(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
            inputs = {input_flow: solph.Flow(variable_costs = extra_variable_cost )},
            outputs = {output_flow: solph.Flow(nominal_value = nominal_value, fix = fixed_el_load_data_rel, variable_costs = variable_costs)},
            conversion_factors = {input_flow: 1 / efficiency, output_flow: 1},
            )
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(tr) 
            return tr
    
    
        def create_simple_transformer_nonconvex(
            self,
            nominal_value,
            min_power_fraction,
            input_flow,
            output_flow,
            efficiency,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            group_options):
            tr = solph.components.Transformer(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
            inputs = {input_flow: solph.Flow()},
            outputs = { output_flow: solph.Flow( nominal_value = nominal_value, min = min_power_fraction, variable_costs = not_fuel_var_cost + extra_variable_cost, 
            nonconvex = solph.NonConvex(
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        )
                        )},
                       
            conversion_factors = {input_flow: 1 / efficiency, output_flow: 1}
            )
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(tr) 
            return tr

        def create_offset_transformer(
            self,
            nominal_value,
            input_flow,
            output_flow,
            efficiency_min,
            efficiency_max,
            min_power_fraction,
            boiler_efficiency ,
            not_fuel_var_cost,
            extra_variable_cost,
            # minimum_uptime,
            # minimum_downtime,
            start_up_options,
            group_options
            ):
            P_out_max = nominal_value     										 # absolute nominal output power
            P_out_min = nominal_value * min_power_fraction                       # absolute minimal output power
            P_in_min = P_out_min / (efficiency_min * boiler_efficiency)
            P_in_max = P_out_max / (efficiency_max * boiler_efficiency)
            c1 = (P_out_max-P_out_min) / (P_in_max-P_in_min)
            c0 = P_out_max - c1 * P_in_max

            tr = solph.components.OffsetTransformer(
                label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
                inputs = {input_flow: solph.Flow(
                nominal_value = P_in_max,
                max = 1,
                min = P_in_min/P_in_max,
                # fix = fixedGenerationData,
                nonconvex = solph.NonConvex(
                                        initial_status = start_up_options['initial_status'],
                                        # initial_status = 1,
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns'],
                                        # minimum_uptime = minimum_uptime,
                                        # minimum_downtime = minimum_downtime
                                        ))},
                outputs = {output_flow: solph.Flow(variable_costs = not_fuel_var_cost + extra_variable_cost)},
                coefficients = [c0, c1],
            )
            # print(tr.max_up_down())
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(tr) 
            return tr

        def create_NPP_block(
            self,
            nominal_el_value,
            min_power_fraction,
            output_flow,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            group_options):
            npp_block = solph.components.Source(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
            outputs = {output_flow: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, nonconvex = solph.NonConvex(
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        ), variable_costs = not_fuel_var_cost + extra_variable_cost,)},
            group_options = group_options
            )
            npp_block.group_options = group_options
            self.es.add(npp_block)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(npp_block) 
            return npp_block

        def create_chp_PT_turbine(
            self,
            nominal_el_value,
            min_power_fraction,
            input_flow,
            output_flow_el, 
            output_flow_T, 
            output_flow_P,
            # nominal_input_t,
            # nominal_input_P,
            efficiency_P,
            efficiency_T,
            heat_to_el_P,
            heat_to_el_T,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            boiler_efficiency,
            group_options):

        # кпд котла?
            el_inner_bus = Generic_buses(self.es).create_buses(set_label(group_options['station_name'],
                group_options['block_name'], group_options['local_index'], 'электричество-промежуточное'))

            P_mode_tr = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index'], 'П_режим'),
            inputs = {input_flow: solph.Flow()},
            outputs = {el_inner_bus: solph.Flow(nominal_el_value = nominal_el_value),
                                    output_flow_P: solph.Flow()
                                    },
            conversion_factors = {input_flow: (1 + heat_to_el_P) / (efficiency_P * boiler_efficiency), el_inner_bus: 1, output_flow_P: heat_to_el_P},

            )
            P_mode_tr.group_options = deepcopy(group_options)

            T_mode_tr = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index'], 'Т_режим'),
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow_T: solph.Flow(),
                                    el_inner_bus: solph.Flow(nominal_el_value = nominal_el_value)
                                },
            conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), el_inner_bus: 1, output_flow_T: heat_to_el_T},
            )
            T_mode_tr.group_options = deepcopy(group_options)
            
            main_output_tr = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']),
            inputs = {el_inner_bus: solph.Flow()},
            outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, nonconvex = solph.NonConvex(
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        ), variable_costs = not_fuel_var_cost + extra_variable_cost)},
            group_options = group_options
            )
            main_output_tr.group_options = deepcopy(group_options)
            self.es.add(P_mode_tr, T_mode_tr, main_output_tr)
            # if isinstance(self.block_collection, list):
            #     self.block_collection.append(P_mode_tr)
            #     self.block_collection.append(T_mode_tr)
            #     self.block_collection.append(main_output_tr)
            return [main_output_tr, P_mode_tr, T_mode_tr]
   
        def create_chp_PT_turbine_full_P_mode(
            self,
            nominal_el_value,
            min_power_fraction,
            input_flow,
            output_flow_el,
            output_flow_P,
            nominal_input_P,
            efficiency_P,
            heat_to_el_P,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            boiler_efficiency,
            group_options):
            
            # кпд котла?
            # nominal_input_P ?
            pt_full_P_mode = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index'], 'электроэнергия_чистый_П_режим'),

            inputs = {input_flow: solph.Flow(nominal_value = nominal_input_P)},
        outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = not_fuel_var_cost + extra_variable_cost,
                                        nonconvex = solph.NonConvex(
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        )),
                                    output_flow_P: solph.Flow()
                                },
            conversion_factors = {input_flow: (1 + heat_to_el_P) / (efficiency_P * boiler_efficiency), output_flow_el: 1, output_flow_P: heat_to_el_P},
            )
            pt_full_P_mode.group_options = group_options
            self.es.add(pt_full_P_mode)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(pt_full_P_mode)
            return pt_full_P_mode

        def create_chp_PT_turbine_full_T_mode(
            self,
            nominal_el_value,
            min_power_fraction,
            input_flow,
            output_flow_el,
            output_flow_T,
            nominal_input_T,
            efficiency_T,
            heat_to_el_T,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            boiler_efficiency,
            group_options):
        # кпд котла?
            pt_full_T_mode = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index'], 'электроэнергия_чистый_Т_режим'),
            inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T, )},
            outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = not_fuel_var_cost + extra_variable_cost,
                                        nonconvex = solph.NonConvex( 
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        )),
                                output_flow_T: solph.Flow()
                                },
            conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
            )
            pt_full_T_mode.group_options = group_options
            self.es.add(pt_full_T_mode)
            # if isinstance(self.block_collection, list):
                #  self.block_collection.append(pt_full_T_mode)
            return pt_full_T_mode

        def create_chp_T_turbine_detail(
            self,
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
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            boiler_efficiency,
            group_options):
        # кпд котла?
            
            # 669.175 - useful
            
            
            
            el_eff = (efficiency_T / (1+ heat_to_el_T)) * boiler_efficiency
            hw_eff = (heat_to_el_T * el_eff )
            # print(hw_eff/el_eff)
            efficiency_full_condensing_mode = efficiency_full_condensing_mode - efficiency_full_condensing_mode * (1- boiler_efficiency)
            # print(efficiency_full_condensing_mode)
            # print((nominal_el_value + nominal_el_value * heat_to_el_T) / (el_eff + hw_eff))
            # nominal_input_T = max_el_value/efficiency_full_condensing_mode
            nominal_input_T = (nominal_el_value + nominal_el_value * heat_to_el_T) / (el_eff + hw_eff)
            # print(nominal_input_T)
                       
            p = nominal_el_value * min_power_fraction
            update_min_fraction = p/max_el_value
            # print(max_el_value*update_min_fraction)
            
            
            T_turbine = solph.components.ExtractionTurbineCHP (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']),
            inputs = {input_flow: solph.Flow(nominal_value = nominal_input_T)},
            outputs = {output_flow_el: solph.Flow(nominal_value = max_el_value, min = update_min_fraction, variable_costs = not_fuel_var_cost + extra_variable_cost,
                                        nonconvex = solph.NonConvex(   
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        )),
                                    output_flow_T: solph.Flow()
                                    },
            conversion_factors = {output_flow_el: el_eff, output_flow_T: hw_eff},
            conversion_factor_full_condensation = {output_flow_el: efficiency_full_condensing_mode},
            )
            T_turbine.group_options = group_options
            self.es.add(T_turbine)
            # if isinstance(self.block_collection, list):
                #  self.block_collection.append(T_turbine)
            return T_turbine
        
        
        def create_chp_T_turbine_simple(
            self,
            nominal_el_value,
            min_power_fraction, 
            input_flow,
            output_flow_el,
            output_flow_T,
            heat_to_el_T,
            efficiency_T,
            boiler_efficiency,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            group_options):
            tr = solph.components.Transformer(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']),
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow_el: solph.Flow( nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = not_fuel_var_cost + extra_variable_cost,
                                    nonconvex = solph.NonConvex(                      
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        )),
                            output_flow_T: solph.Flow()},
            conversion_factors = {input_flow: (1 + heat_to_el_T) /(efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
            ) 
            tr.group_options = group_options
            self.es.add(tr)
            return tr
        
        
        def create_ccgt_chp_detail(
                self,
                nominal_el_value,
                min_power_fraction,
                input_flow,
                output_flow_el,
                output_flow_T,
                efficiency_T,
                heat_to_el_T,
                efficiency_full_condensing_mode,
                not_fuel_var_cost,
                extra_variable_cost,
                start_up_options,
                boiler_efficiency,
                group_options):
            
            el_inner_bus = Generic_buses(self.es).create_buses(set_label(group_options['station_name'],
            group_options['block_name'], group_options['local_index'], 'электричество-промежуточное'))

            ccgt_inner_condensing = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index'], 'конденсационный режим'),
            inputs = {input_flow: solph.Flow()},
            outputs = {el_inner_bus: solph.Flow(nominal_el_value = nominal_el_value)},
            conversion_factors = {input_flow: 1 / efficiency_full_condensing_mode, el_inner_bus: 1},

            )
            ccgt_inner_condensing.group_options = deepcopy(group_options)



            ccgt_hw_part = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index'], 'теплофикационный режим'),
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow_T: solph.Flow(),
                                    el_inner_bus: solph.Flow(nominal_el_value = nominal_el_value)
                                },
            conversion_factors = {input_flow: (1 + heat_to_el_T) / (efficiency_T * boiler_efficiency), el_inner_bus: 1, output_flow_T: heat_to_el_T},
            )
            ccgt_hw_part.group_options = deepcopy(group_options)
                        
            
            
            ccgt_el_part = solph.components.Transformer (
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']),
            inputs = {el_inner_bus: solph.Flow()},
            outputs = {output_flow_el: solph.Flow(nominal_value = nominal_el_value, min = min_power_fraction, nonconvex = solph.NonConvex(
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']), 
                                        variable_costs = not_fuel_var_cost + extra_variable_cost)},
                                        group_options = group_options
            )
            ccgt_el_part.group_options = deepcopy(group_options)
            self.es.add(ccgt_inner_condensing, ccgt_el_part, ccgt_hw_part)
            return [ccgt_el_part, ccgt_hw_part]
            
        
        
        def create_simple_chp_with_fixed_load(
            self,
            nominal_el_value,
            input_flow,
            output_flow_el,
            output_flow_T,
            heat_to_el_T,
            efficiency_T,
            boiler_efficiency,
            not_fuel_var_cost,
            fixed_load_rel,
            group_options):
            tr = solph.components.Transformer(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']),
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow_el: solph.Flow( nominal_value = nominal_el_value, variable_costs = not_fuel_var_cost, fix = fixed_load_rel),
                            output_flow_T: solph.Flow()},
            conversion_factors = {input_flow: (1 + heat_to_el_T) /(efficiency_T * boiler_efficiency), output_flow_el: 1, output_flow_T: heat_to_el_T},
            ) 
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                #  self.block_collection.append(tr)
            return tr

        def create_back_pressure_turbine(
            self,
            nominal_el_value,
            min_power_fraction, 
            input_flow,
            output_flow_el,
            output_flow_P,
            heat_to_el_P,
            efficiency_P,
            boiler_efficiency,
            not_fuel_var_cost,
            extra_variable_cost,
            start_up_options,
            group_options):
            tr = solph.components.Transformer(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']),
            inputs = {input_flow: solph.Flow()},
            outputs = {output_flow_el: solph.Flow( nominal_value = nominal_el_value, min = min_power_fraction, variable_costs = not_fuel_var_cost + extra_variable_cost, nonconvex = solph.NonConvex(                        
                                        initial_status = start_up_options['initial_status'],
                                        startup_costs =  start_up_options['start_up_cost'], 
                                        shutdown_costs = start_up_options['shout_down_cost'],
                                        maximum_startups = start_up_options['maximum_startups'],
                                        maximum_shutdowns = start_up_options['maximum_shutdowns']
                                        )),
                            output_flow_P: solph.Flow()},
            conversion_factors = {input_flow: (1 + heat_to_el_P) /(efficiency_P * boiler_efficiency), output_flow_el: 1, output_flow_P: heat_to_el_P},
            ) 
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                #  self.block_collection.append(tr)
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

        def __init__(self, es) -> None:
            # self.block_collection = block_collection
            self.es = es
        
        def create_source(self, nominal_value, output_flow, variable_costs, group_options):
            source = solph.components.Source(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
            outputs = {output_flow: solph.Flow(nominal_value=nominal_value,  variable_costs = variable_costs)} 
            )
            source.group_options = group_options
            self.es.add(source)
            # if isinstance(self.block_collection, list):
                #  self.block_collection.append(source)
            return source
        
        def create_source_with_fixed_load(
            self,
            nominal_value,
            output_flow,
            variable_costs,
            group_options,
            fixed_el_load_data_rel
        ):
            tr = solph.components.Source(
            label= set_label(group_options['station_name'], group_options['block_name'], group_options['local_index']), 
            outputs = {output_flow: solph.Flow(nominal_value = nominal_value, fix = fixed_el_load_data_rel, variable_costs = variable_costs)},
            )
            tr.group_options = group_options
            self.es.add(tr)
            # if isinstance(self.block_collection, list):
                # self.block_collection.append(tr) 
            return tr
    

        def create_resource(self, label, output_flow, variable_costs):
            source = solph.components.Source(
            label= label, 
            outputs = {output_flow: solph.Flow(variable_costs = variable_costs)} )
            self.es.add(source)
            # if isinstance(self.block_collection, list):
                #  self.block_collection.append(source)
            return source
            

      
      
      
      

   
   