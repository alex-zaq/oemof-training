from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from enum import Enum
from custom_modules.helpers import set_label
from custom_modules.generic_blocks import Generic_blocks, Generic_sources
from custom_modules.helpers import *


class Specific_blocks:



        def __init__(self, es, global_natural_gas_flow, global_el_flow, block_collection = None):
            self.block_collection = block_collection
            self.global_natural_gas_flow = global_natural_gas_flow
            self.global_el_flow = global_el_flow
            self.es = es
            self.g_block_creator = Generic_blocks(es, self.block_collection)
            self.g_source_creator = Generic_sources(es, self.block_collection)
            self.station_type = {'тэц':'тэц', 'кэс':'кэс', 'аэс':'аэс',
                                 'блок-станции':'блок-станции', 'виэ':'виэ'
                                 }
            self.block_type = {'р':'р', 'т':'т', 'пт':'пт', 'к':'к',
                               'пгу-кэс':'пгу-кэс', 'пгу-тэц':'пгу-тэц',
                               'гту':'гту','гту-тэц':'гту-тэц', 'эк':'эк',
                               'кот':'кот', 'ввэр':'ввэр', 'ммр':'ммр','блок-станции-газ':'блок-станции-газ',
                               'виэ-солнце':'виэ-солнце','виэ-вода':'виэ-вода',
                               'виэ-ветер':'виэ-ветер', 'фейк':'фейк', 'ресурс':'ресурс'
                               }


        def get_block_collection(self):
            return self.block_collection
        
        
 
   
        def get_el_boilers(self, global_index, local_index, station_name, nominal_value, output_flow, variable_costs, group_options = None):
            block_type = self.block_type['эк']
            return self.g_block_creator.create_simple_transformer(
            nominal_value = nominal_value,
            input_flow = self.global_el_flow,
            output_flow = output_flow,
            efficiency = 0.99,
            variable_costs = variable_costs,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': nominal_value
            })
                       
               
        # def get_el_steam_boilers(self, global_index, local_index, station_name, nominal_value, output_flow, variable_costs, group_options = None):
        #     block_type = self.block_type['эк']
        #     return self.g_block_creator.create_simple_transformer(
        #     nominal_value = nominal_value,
        #     input_flow = self.global_el_flow,
        #     output_flow = output_flow,
        #     efficiency = 0.99,
        #     variable_costs = variable_costs,
        #     group_options = {
        #     'global_index': str(global_index),
        #     'local_index': str(local_index),
        #     'station_name': station_name,
        #     'station_type': None,
        #     'block_name': block_type,
        #     'block_type': block_type,
        #     'heat_demand_type': None,
        #     'station_order': None,
        #     'block_order': None,
        #     'nominal_value': nominal_value
        #     })
            
            
        def get_gas_boilers(self,global_index, local_index, station_name, nominal_value, output_flow, variable_costs, group_options = None):
            block_type = self.block_type['кот']
            return self.g_block_creator.create_simple_transformer(
            nominal_value = nominal_value,
            input_flow = self.global_natural_gas_flow ,
            output_flow = output_flow,
            efficiency = 0.90,
            variable_costs = variable_costs,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': nominal_value
            }
            )
            
            
        def get_ocgt_120(self,global_index, local_index,station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['гту']
            return self.g_block_creator.create_offset_transformer(
            nominal_value = 120,
            input_flow = self.global_natural_gas_flow,
            output_flow = self.global_el_flow,
            efficiency_min = 0.25,
            efficiency_max = 0.40,
            min_power_fraction = 0.25,
            variable_costs = 0,
            boiler_efficiency = 1,  
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'ГТУ-120',
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 120
            })    
            
            
            
        def get_k_160(self,global_index, local_index, station_name, variable_costs, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 160,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.378,
                efficiency_max = 0.423,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                # variable_costs = variable_costs,
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'К-160',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 160              
                }  
            )
            
            
        def get_k_175(self,global_index, local_index,station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 175,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.42,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'К-175',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 175   
                }   
            )
        def get_k_300(self,global_index, local_index, station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 300,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.42,
                efficiency_max = 0.469,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'К-300',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None ,
                'nominal_value': 300   
                }    
            )
               
        def get_k_310(self,global_index, local_index,station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 310,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.42,
                efficiency_max = 0.48,
                min_power_fraction = 0.36,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'К-310',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order':None,
                'nominal_value': 310   
                }      
            )
                        #  минимум?  
        def get_k_315(self,global_index, local_index, station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 315,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.42,
                efficiency_max = 0.49,
                min_power_fraction = 0.36,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'К-315',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 315   
                }    
            )
                       
            
            
        def get_ccgt_399(self,global_index, local_index, station_name,  group_options = None, planning_outage = None):
            block_type = self.block_type['пгу-кэс']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 399,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.43,
                efficiency_max = 0.56,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1,
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПГУ-399',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 399   
                }    
            )
        def get_ccgt_427(self,global_index, local_index, station_name,  group_options = None, planning_outage = None):
            block_type = self.block_type['пгу-кэс']
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 427,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.43,
                efficiency_max = 0.59,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1,  
                initial_status= 1,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПГУ-427',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 427   
                }    
            )
             
            
        # def get_ccgt_сhp_222(self, index, station_name, output_flow_T, planning_outage = None, ):
        #     return self.g_block_creator.create_chp_T_turbine(
        #         index = index,
        #         station_name = station_name,
        #         block_name = 'ПГУ-Т',
        #         nominal_el_value = 250,
        #         max_el_value = 300,
        #         min_power_fraction = 0.5,
        #         nominal_input_T = 750,
        #         input_flow = self.global_natural_gas_flow,
        #         output_flow_el = self.global_el_flow,
        #         output_flow_T = output_flow_T,
        #         efficiency_T = 0.9,
        #         heat_to_el_T = 1.6767,
        #         efficiency_full_condensing_mode = 0.41,
        #         variable_costs = 0,
        #         boiler_efficiency = 1
                
        #     )
            
        def get_ocgt_chp_121(self,global_index, local_index, station_name, output_flow_T, output_flow_P, planning_outage = None):
            pass

            
        def get_t_250(self,global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            return self.g_block_creator.create_chp_T_turbine(
                nominal_el_value = 250,
                max_el_value = 300,
                min_power_fraction = 0.5,
                nominal_input_T = 750,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.9,
                heat_to_el_T = 1.6767,
                efficiency_full_condensing_mode = 0.41,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'Т-250',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 250   
                }    
                
            )
            
        def get_t_180(self,global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            return self.g_block_creator.create_chp_T_turbine(
            nominal_el_value = 180,
            min_power_fraction = 0.5,
            nominal_input_T = 350,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_T = output_flow_T,
            efficiency_T = 0.82,
            heat_to_el_T = 1.9,
            efficiency_full_condensing_mode = 0.4,
            variable_costs = 0,
            boiler_efficiency = 0.9,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'Т-180',
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 180   
            }   
            ) 
                        
            
        def get_t_110(self,global_index, local_index, station_name, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            return self.g_block_creator.create_chp_T_turbine(
                nominal_el_value = 110,
                max_el_value = 120,
                min_power_fraction = 0.35,
                nominal_input_T = 333,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.9,
                heat_to_el_T = 1.85,
                efficiency_full_condensing_mode = 0.39,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'Т-110',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 110   
                } 
            )
   
                       
        def get_t_100(self,global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            return self.g_block_creator.create_chp_T_turbine(
            index = local_index,
            station_name = station_name,
            block_name = 'Т-100',
            nominal_el_value = 100,
            min_power_fraction = 0.5,
            nominal_input_T = 350,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_T = output_flow_T,
            efficiency_T = 0.82,
            heat_to_el_T = 1.9,
            efficiency_full_condensing_mode = 0.41,
            variable_costs = 0,
            boiler_efficiency = 1,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'Т-110',
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 100   
            } 
            )
            
##################################################################################   
# ПТ - 50
################################################################################## 
        def get_pt_50(self,global_index, local_index, station_name, output_flow_P, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
            nominal_el_value = 50,
            min_power_fraction = 0.4,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_P = output_flow_P,
            output_flow_T = output_flow_T,
            efficiency_P = 0.89,
            efficiency_T = 0.89,
            heat_to_el_P = 3.8,
            heat_to_el_T = 2.02,
            variable_costs = 0,
            boiler_efficiency = 1,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'ПТ-50',
            'block_type': block_type,
            'heat_demand_type_hw': None,
            'heat_demand_type_steam': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 50   
            } 
            )     
                   
        def get_pt_50_p(self, global_index, local_index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
            nominal_el_value = 50,
            min_power_fraction = 0.4,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_P = output_flow_P,
            nominal_input_P = 300,
            efficiency_P = 0.91,
            heat_to_el_P = 3.8,
            variable_costs = 0,
            boiler_efficiency = 1,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'ПТ-50_П',
            'block_type': block_type,
            'heat_demand_type_steam': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 50   
            } 
            )

        def get_pt_50_t(self, global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
            nominal_el_value = 50,
            min_power_fraction = 0.4,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_T = output_flow_T,
            nominal_input_T = 200,
            efficiency_T = 0.91,
            heat_to_el_T = 2.02,
            variable_costs = 0,
            boiler_efficiency = 1,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'ПТ-50_Т',
            'block_type': block_type,
            'heat_demand_type_hw': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 50   
            } 
            )
##################################################################################   
# ПТ - 60
##################################################################################   
        def get_pt_60(self,global_index, local_index, station_name, output_flow_P, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                nominal_el_value = 60,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                efficiency_P = 0.9,
                efficiency_T = 0.9,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-60',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 60   
            } 
            )
   
        def get_pt_60_p(self,global_index, local_index, station_name, output_flow_P, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 60,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                nominal_input_P = 300,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 0.9, 
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-60_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 60   
            } 
            )
   
        def get_pt_60_t(self,global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                nominal_el_value = 60,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                nominal_input_T = 200,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-60_Т',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 60   
            } 
            )

##################################################################################   
# ПТ - 65
##################################################################################    
        def get_pt_65(self,global_index, local_index, station_name, output_flow_P, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                nominal_el_value = 65,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                efficiency_P = 0.91,
                efficiency_T = 0.91,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-65',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 65   
            } 
            )
   
        def get_pt_65_p(self,global_index, local_index, station_name, output_flow_P, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 65,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-65_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 65   
            } 
            )
   
        def get_pt_65_t(self,global_index, local_index, station_name, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                nominal_el_value = 65,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-65_Т',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 65   
            } 
            )
##################################################################################   
# ПТ - 70
##################################################################################    
        def get_pt_70(self,global_index, local_index, station_name, output_flow_P, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                nominal_el_value = 70,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                efficiency_P = 0.91,
                efficiency_T = 0.91,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-70',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 70   
            } 
            )
   
        def get_pt_70_p(self,global_index, local_index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 70,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-70_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 70   
            } 
            )
   
        def get_pt_70_t(self,global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                nominal_el_value = 70,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-70_Т',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 70   
            } 
            )
##################################################################################
# ПТ - 135
##################################################################################   
        def get_pt_135(self,global_index, local_index, station_name, output_flow_P, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                nominal_el_value = 135,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                efficiency_P = 0.91,
                efficiency_T = 0.91,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-135',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 135   
            } 
            )
   
        def get_pt_135_p(self, global_index, local_index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 135,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ПТ-135_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 135   
            } 
            )
   
        def get_pt_135_t(self, global_index, local_index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                nominal_el_value = 135,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-135_Т',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 135   
            })
            
            
        def get_p_50(self, global_index, local_index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['р']
            return self.g_block_creator.create_back_pressure_turbine(
            nominal_el_value = 50,
            min_power_fraction = 0.35,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_P = output_flow_P,
            efficiency_P = 0.91,
            heat_to_el_P = 3.8,
            variable_costs = 0,
            boiler_efficiency = 0.9,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': 'Р-50',
            'block_type': block_type,
            'heat_demand_type_hw': None,
            'heat_demand_type_steam': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 50   
            } 
            )
 ##################################################################################
 # ВВЭР-1200
 ##################################################################################
        def get_vver_1200(self, global_index, local_index, station_name, variable_costs,  group_options = None, planning_outage = None):
            block_type = self.block_type['ввэр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 1200,
                min_power_fraction = 0.75,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ВВЭР-1200',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 1200   
            } 
            )
##################################################################################
 # ВВЭР-ТОИ
 ##################################################################################
        def get_vver_toi(self, global_index, local_index, station_name, variable_costs, group_options = None, planning_outage = None):
            block_type = self.block_type['ввэр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 1255,
                min_power_fraction = 0.75,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ВВЭР-ТОИ',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 1255   
            } 
            )
 ##################################################################################
 # ВВЭР-600
 ##################################################################################
        def get_vver_600(self, global_index, local_index, station_name, variable_costs,  group_options = None, planning_outage = None):
            block_type = self.block_type['ввэр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 600,
                min_power_fraction = 0.65,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'ВВЭР-600',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 600   
            } 
            )
 ##################################################################################
 # РИТМ-200
 ##################################################################################
        def get_ritm_200(self,global_index, local_index, station_name, variable_costs,  group_options = None, planning_outage = None):
            block_type = self.block_type['ммр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 50,
                min_power_fraction = 0.65,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'РИТМ-200',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 50   
            } 
            )

        def get_block_station_natural_gas(self, global_index, local_index, nominal_value, station_name, fixed_el_load_data_rel, variable_costs = 0):
            block_type = self.block_type['блок-станции-газ']
            return self.g_block_creator.create_simple_transformer_with_fixed_load(
            nominal_value = nominal_value,
            input_flow = self.global_natural_gas_flow ,
            output_flow = self.global_el_flow,
            efficiency = 0.90,
            variable_costs = variable_costs,
            fixed_el_load_data_rel = fixed_el_load_data_rel,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': nominal_value
            }
            )
            
            
        def get_wind_renewables(self, global_index, local_index, nominal_value, station_name, fixed_el_load_data_rel, variable_costs = 0):
            block_type = self.block_type['виэ-ветер']
            return self.g_source_creator.create_source_with_fixed_load(
            nominal_value = nominal_value,
            output_flow = self.global_el_flow,
            variable_costs = variable_costs,
            fixed_el_load_data_rel = fixed_el_load_data_rel,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': nominal_value
            })
            
        def get_solar_renewables(self, global_index, local_index, nominal_value, station_name, fixed_el_load_data_rel, variable_costs = 0):
            block_type = self.block_type['виэ-солнце']
            return self.g_source_creator.create_source_with_fixed_load(
            nominal_value = nominal_value,
            output_flow = self.global_el_flow,
            variable_costs = variable_costs,
            fixed_el_load_data_rel = fixed_el_load_data_rel,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': nominal_value
            })
            
        def get_hydro_renewables(self, global_index, local_index, nominal_value, station_name, fixed_el_load_data_rel, variable_costs = 0):
            block_type = self.block_type['виэ-вода']
            return self.g_source_creator.create_source_with_fixed_load(
            nominal_value = nominal_value,
            output_flow = self.global_el_flow,
            variable_costs = variable_costs,
            fixed_el_load_data_rel = fixed_el_load_data_rel,
            group_options = {
            'global_index': str(global_index),
            'local_index': str(local_index),
            'station_name': station_name,
            'station_type': None,
            'block_name': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': nominal_value
            })








        def get_natural_gas_source(self, label, usd_per_1000_m3):
            return self.g_source_creator.create_resource(
                label = label,
                output_flow = self.global_natural_gas_flow,
                variable_costs= set_natural_gas_price(usd_per_1000_m3),
            )


        
        def get_electricity_source(self,global_index, local_index, nominal_value, station_name, usd_per_Mwth):
            block_type =self.block_type['фейк']
            return self.g_source_creator.create_source(
                nominal_value = nominal_value,
                output_flow = self.global_el_flow,
                variable_costs= usd_per_Mwth,
                group_options = {
                'global_index': str(global_index),
                'local_index': str(local_index),
                'station_name': station_name,
                'station_type': None,
                'block_name': 'источник_электроэнергии',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': nominal_value   
                }
            )


        

        def get_custom_dummy_source(self, global_index, local_index, station_name, block_name, output_flow, variable_costs):
            block_type = self.block_type['фейк']
            return self.g_source_creator.create_source(
                    output_flow=output_flow,
                    variable_costs = variable_costs,
                    group_options = {
                    'global_index': str(global_index),
                    'local_index': str(local_index),
                    'station_name': station_name,
                    'station_type': None,
                    'block_name': block_name,
                    'block_type': block_type,
                    'heat_demand_type_hw': None,
                    'heat_demand_type_steam': None,
                    'station_order': None,
                    'block_order': None,
                    'nominal_value': None   
                } )
                
            
        

   
   
   
   
   
        
 
 