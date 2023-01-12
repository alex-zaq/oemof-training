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
                               'кот':'кот', 'ввэр':'ввэр', 'ммр':'ммр',
                               'виэ-солнце':'виэ-солнце','виэ-вода':'виэ-вода',
                               'виэ-ветер':'виэ-ветер'
                               }


        def get_block_collection(self):
            return self.block_collection
        
        
        def get_default_group_options_by_block_type (self, block_type):
            return {
                    'station_order':0,
                    'block_order':self.block_type[block_type],
                    'station_type': 'нет типа станции'
            }
   
        def get_el_boilers(self, index, station_name, install_power, output_flow, variable_costs, group_options = None):
            block_type = self.block_type['эк']
            # heat_demand_type  = output_flow.heat_demand_group_name if hasattr(output_flow, 'heat_demand_type') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_simple_transformer(
            nominal_value = install_power,
            input_flow = self.global_el_flow,
            output_flow = output_flow,
            efficiency = 0.99,
            variable_costs = variable_costs,
            group_options = {
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': install_power
            })
            
        def get_gas_boilers(self, index, station_name, install_power, output_flow, variable_costs, group_options):
            block_type = self.block_type['кот']
            # heat_demand_type  = output_flow.heat_demand_group_name if hasattr(output_flow, 'heat_demand_type') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_simple_transformer(
            nominal_value = install_power,
            input_flow = self.global_natural_gas_flow ,
            output_flow = output_flow,
            efficiency = 0.90,
            variable_costs = variable_costs,
            group_options = {
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': block_type,
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': install_power
            }
            )
            
            
        def get_ocgt_120(self, index,station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['гту']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'ГТУ-120',
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 120
            })    
            
            
            
        def get_k_160(self, index, station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 160,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.378,
                efficiency_max = 0.423,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'К-160',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 160              
                }  
            )
            
            
        def get_k_175(self, index,station_name, station_type,  group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 175,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.42,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'К-175',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 175   
                }   
            )
        def get_k_300(self, index, station_name, group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 300,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.42,
                efficiency_max = 0.469,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'К-300',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None ,
                'nominal_value': 300   
                }    
            )
               
        def get_k_310(self, index,station_name, station_type,  group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 310,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.42,
                efficiency_max = 0.48,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'К-310',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order':None,
                'nominal_value': 310   
                }      
            )
                        #  минимум?  
        def get_k_315(self, index, station_name, station_type , group_options = None, planning_outage = None):
            block_type = self.block_type['к']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 315,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.42,
                efficiency_max = 0.49,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 0.9,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'К-315',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 315   
                }    
            )
                       
            
            
        def get_ccgt_399(self, index, station_name, statio ,  group_options = None, planning_outage = None):
            block_type = self.block_type['пгу-кэс']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                nominal_value = 399,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.43,
                efficiency_max = 0.56,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПГУ-399',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 399   
                }    
            )
        def get_ccgt_427(self, index, station_name,  group_options = None, planning_outage = None):
            block_type = self.block_type['пгу-кэс']
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_offset_transformer(
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.43,
                efficiency_max = 0.59,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1,  
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПГУ-427',
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
            
        def get_ocgt_chp_121(self, index, station_name, output_flow_T, output_flow_P, planning_outage = None):
            pass

            
        def get_t_250(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            # heat_demand_type  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_type') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
                boiler_efficiency = 1,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'Т-250',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 250   
                }    
                
            )
            
        def get_t_180(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            # heat_demand_type  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_type') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'Т-180',
            'block_type': block_type,
            'heat_demand_type': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 180   
            }   
            ) 
                        
            
        def get_t_110(self, index, station_name, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            # heat_demand_type  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_type') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'Т-110',
                'block_type': block_type,
                'heat_demand_type': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 110   
                } 
            )
   
                       
        def get_t_100(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['т']
            # heat_demand_type  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_chp_T_turbine(
            index = index,
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
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'Т-110',
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
        def get_pt_50(self, index, station_name, output_flow_P, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            # heat_type_hw  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # heat_type_steam  = output_flow_P.heat_demand_group_name if hasattr(output_flow_P, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
            return self.g_block_creator.create_chp_PT_turbine(
            nominal_el_value = 50,
            min_power_fraction = 0.4,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_P = output_flow_P,
            output_flow_T = output_flow_T,
            nominal_input_P = 280,
            nominal_input_t = 140,
            efficiency_P = 0.89,
            efficiency_T = 0.89,
            heat_to_el_P = 3.8,
            heat_to_el_T = 2.02,
            variable_costs = 0,
            boiler_efficiency = 1,
            group_options = {
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'ПТ-50',
            'block_type': block_type,
            'heat_demand_type_hw': None,
            'heat_demand_type_steam': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 50   
            } 
            )     
                   
        def get_pt_50_p(self, index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            # heat_type_steam  = output_flow_P.heat_demand_group_name if hasattr(output_flow_P, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'ПТ-50_П',
            'block_type': block_type,
            'heat_demand_type_steam': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 50   
            } 
            )

        def get_pt_50_t(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            # heat_type_hw  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'ПТ-50_Т',
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
        def get_pt_60(self, index, station_name, output_flow_P, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            # heat_type_hw  = output_flow_T.heat_demand_group_name if hasattr(output_flow_T, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # heat_type_steam  = output_flow_P.heat_demand_group_name if hasattr(output_flow_P, 'heat_demand_group_name') else 'не задан тепловой спрос'
            # group_options = self.get_default_group_options_by_block_type(block_type) if not group_options else group_options
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-60',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 60   
            } 
            )
   
        def get_pt_60_p(self, index, station_name, output_flow_P, group_options = None, planning_outage = None):
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
                boiler_efficiency = 1, 
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-60_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 60   
            } 
            )
   
        def get_pt_60_t(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                block_name = 'ПТ-60_Т',
                nominal_el_value = 60,
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-60_Т',
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
        def get_pt_65(self, index, station_name, output_flow_P, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                block_name = 'ПТ-65',
                nominal_el_value = 65,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                nominal_input_P = 300,
                nominal_input_t = 150,
                efficiency_P = 0.91,
                efficiency_T = 0.91,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 1,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-65',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 65   
            } 
            )
   
        def get_pt_65_p(self, index, station_name, output_flow_P, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 65,
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-65_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 65   
            } 
            )
   
        def get_pt_65_t(self, index, station_name, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                index = index,
                nominal_el_value = 65,
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-65_Т',
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
        def get_pt_70(self, index, station_name, output_flow_P, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                nominal_el_value = 70,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                nominal_input_P = 300,
                nominal_input_t = 150,
                efficiency_P = 0.91,
                efficiency_T = 0.91,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 1,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-70',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 70   
            } 
            )
   
        def get_pt_70_p(self, index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 70,
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-70_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 70   
            } 
            )
   
        def get_pt_70_t(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                nominal_el_value = 70,
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-70_Т',
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
        def get_pt_135(self, index, station_name, output_flow_P, output_flow_T, group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine(
                nominal_el_value = 135,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                output_flow_T = output_flow_T,
                nominal_input_P = 300,
                nominal_input_t = 150,
                efficiency_P = 0.91,
                efficiency_T = 0.91,
                heat_to_el_P = 3.8,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 1,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-135',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 135   
            } 
            )
   
        def get_pt_135_p(self, index, station_name, output_flow_P,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                nominal_el_value = 135,
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
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ПТ-135_П',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 135   
            } 
            )
   
        def get_pt_135_t(self, index, station_name, output_flow_T,  group_options = None, planning_outage = None):
            block_type = self.block_type['пт']
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                nominal_el_value = 135,
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
                'index': index,
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
            
            
        def get_p_50(self, index, station_name, output_flow_P,  group_options = None, planning_outage = None):
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
            boiler_efficiency = 1,
            group_options = {
            'index': index,
            'station_name': station_name,
            'station_type': None,
            'block': 'Р-50',
            'block_type': block_type,
            'heat_demand_type_hw': None,
            'heat_demand_type_steam': None,
            'station_order': None,
            'block_order': None,
            'nominal_value': 135   
            } 
            )
 ##################################################################################
 # ВВЭР-1200
 ##################################################################################
        def get_vver_1200(self, index, station_name, variable_costs,  group_options = None, planning_outage = None):
            block_type = self.block_type['ввэр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 1170,
                min_power_fraction = 0.75,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ВВЭР-1200',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 1170   
            } 
            )
##################################################################################
 # ВВЭР-ТОИ
 ##################################################################################
        def get_vver_toi(self, index, station_name, variable_costs, group_options = None, planning_outage = None):
            block_type = self.block_type['ввэр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 1255,
                min_power_fraction = 0.75,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ВВЭР-ТОИ',
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
        def get_vver_600(self, index, station_name, variable_costs,  group_options = None, planning_outage = None):
            block_type = self.block_type['ввэр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 600,
                min_power_fraction = 0.65,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'ВВЭР-600',
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
        def get_ritm_200(self, index, station_name, variable_costs,  group_options = None, planning_outage = None):
            block_type = self.block_type['ммр']
            return self.g_block_creator.create_NPP_block(
                nominal_el_value = 50,
                min_power_fraction = 0.65,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
                group_options = {
                'index': index,
                'station_name': station_name,
                'station_type': None,
                'block': 'РИТМ-200',
                'block_type': block_type,
                'heat_demand_type_hw': None,
                'heat_demand_type_steam': None,
                'station_order': None,
                'block_order': None,
                'nominal_value': 50   
            } 
            )





        # def get_dummy_source(self, index, station_name, label ,output_flow, variable_costs = 9999):
        #     return self.g_source_creator.create_source(
        #             label=set_label(station_name ,'Dummy', label, str(index)),
        #             output_flow=output_flow,
        #             variable_costs = variable_costs,
        #             group_options = {
        #             'index': index,
        #             'station_name': station_name,
        #             'station_type': None,
        #             'block': 'ПТ-60_П',
        #             'block_type': block_type,
        #             'heat_demand_type_hw': None,
        #             'heat_demand_type_steam': None,
        #             'station_order': None,
        #             'block_order': None,
        #             'nominal_value': None   
        #     })
            
        
        

   
   
   
   
   
        
 
 