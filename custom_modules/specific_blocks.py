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

        def __init__(self, es, global_natural_gas_flow, global_el_flow, block_collection = None) -> None:
            self.block_collection = block_collection
            self.global_natural_gas_flow = global_natural_gas_flow
            self.global_el_flow = global_el_flow
            self.es = es
            self.g_block_creator = Generic_blocks(es, self.block_collection)
            self.g_source_creator = Generic_sources(es, block_collection)

        def get_block_collection(self):
            return self.block_collection
   
        def get_el_boilers(self, index, station_name, install_power, output_flow, commodity_tag, variable_costs):
            return self.g_block_creator.create_simple_transformer(
                    index = index,
                    station_name = station_name,
                    station_type = None,
                    block_name = set_label('ЭК', commodity_tag),
                    block_type =  set_label('ЭК', commodity_tag),
                    commodity_tag = commodity_tag,
                    nominal_value = install_power,
                    input_flow = self.global_el_flow,
                    output_flow = output_flow,
                    efficiency = 0.99,
                    variable_costs = variable_costs,
            )
        def get_gas_boilers(self, index, station_name, install_power, output_flow, commodity_tag, variable_costs):
            return self.g_block_creator.create_simple_transformer(
                    index = index,
                    station_name = station_name,
                    station_type = None,
                    block_name = set_label('ЭК', commodity_tag),
                    block_type =  set_label('ЭК', commodity_tag),
                    commodity_tag = commodity_tag,
                    nominal_value = install_power,
                    input_flow = self.global_natural_gas_flow ,
                    output_flow = output_flow,
                    efficiency = 0.90,
                    variable_costs = variable_costs,
            )
        def get_k_160(self, index,station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
            index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'К-160',
                block_type = 'К',
                commodity_tag = None,
                nominal_value = 160,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.42,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
        def get_k_175(self, index,station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
            index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'К-175',
                block_type = 'К',
                commodity_tag = None,
                nominal_value = 175,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.42,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
        def get_k_300(self, index,station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
                index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'К-300',
                block_type = 'К',
                commodity_tag = None,
                nominal_value = 300,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.42,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
               
        def get_k_310(self, index,station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
                index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'К-300(310)',
                block_type = 'К',
                commodity_tag = None,
                nominal_value = 310,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.43,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
                           
        def get_k_315(self, index,station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
                index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'К-300(315)',
                block_type = 'К',
                commodity_tag = None,
                nominal_value = 315,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.39,
                efficiency_max = 0.44,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
                       
            
            
        def get_ccgt_399(self, index, station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
                index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'ПГУ-399',
                block_type = 'ПГУ-КЭС',
                commodity_tag = None,
                nominal_value = 399,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.43,
                efficiency_max = 0.56,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
        def get_ccgt_427(self, index, station_name, planning_outage = None):
            return self.g_block_creator.create_offset_transformer(
                index = index,
                station_name = station_name,
                station_type = 'КЭС',
                block_name = 'ПГУ-427',
                block_type = 'ПГУ-КЭС',
                commodity_tag = None,
                nominal_value = 427,
                input_flow = self.global_natural_gas_flow,
                output_flow = self.global_el_flow,
                efficiency_min = 0.43,
                efficiency_max = 0.59,
                min_power_fraction = 0.4,
                variable_costs = 0,
                boiler_efficiency = 1  
            )
            
        def get_cogt_chp_121(self, index, station_name, output_flow_T, output_flow_P, planning_outage = None):
            pass

            
        def get_ccgt_сhp_222(self, index, station_name, output_flow_T, planning_outage = None, ):
            pass
            
        def get_t_255(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_T_turbine(
                index = index,
                station_name = station_name,
                block_name = 'Т-255',
                nominal_el_value = 250,
                min_power_fraction = 0.5,
                nominal_input_T = 350,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.82,
                heat_to_el_T = 1.9,
                efficiency_full_condensing_mode = 0.41,
                variable_costs = 0,
                boiler_efficiency = 1
            )
    
            
        def get_t_250(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_T_turbine(
                index = index,
                station_name = station_name,
                block_name = 'Т-250',
                nominal_el_value = 300,
                min_power_fraction = 0.5,
                nominal_input_T = 732,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.91,
                heat_to_el_T = 1.6767,
                efficiency_full_condensing_mode = 0.41,
                variable_costs = 0,
                boiler_efficiency = 0.9
            )
            
        def get_t_180(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_T_turbine(
            index = index,
            station_name = station_name,
            block_name = 'Т-180',
            nominal_el_value = 250,
            min_power_fraction = 0.5,
            nominal_input_T = 350,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_T = output_flow_T,
            efficiency_T = 0.82,
            heat_to_el_T = 1.9,
            efficiency_full_condensing_mode = 0.41,
            variable_costs = 0,
            boiler_efficiency = 1
            ) 
            
            
            
        def get_t_110(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_T_turbine(
                index = index,
                station_name = station_name,
                block_name = 'Т-110',
                nominal_el_value = 110,
                min_power_fraction = 0.35,
                nominal_input_T = 350,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                efficiency_T = 0.82,
                heat_to_el_T = 1.9,
                efficiency_full_condensing_mode = 0.41,
                variable_costs = 0,
                boiler_efficiency = 1
            )
   
                       
        def get_t_100(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_T_turbine(
            index = index,
            station_name = station_name,
            block_name = 'Т-100',
            nominal_el_value = 250,
            min_power_fraction = 0.5,
            nominal_input_T = 350,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_T = output_flow_T,
            efficiency_T = 0.82,
            heat_to_el_T = 1.9,
            efficiency_full_condensing_mode = 0.41,
            variable_costs = 0,
            boiler_efficiency = 1
            )
            
##################################################################################   
# ПТ - 50
################################################################################## 
        def get_pt_50(self, index, station_name, output_flow_P, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine(
            index = index,
            station_name = station_name,
            block_name = 'ПТ-50',
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
            boiler_efficiency = 1
            )     
                   
        def get_pt_50_p(self, index, station_name, output_flow_P):
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
            index = index,
            station_name = station_name,
            block_name = 'ПТ-50_П',
            nominal_el_value = 50,
            min_power_fraction = 0.4,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_P = output_flow_P,
            nominal_input_P = 300,
            efficiency_P = 0.91,
            heat_to_el_P = 3.8,
            variable_costs = 0,
            boiler_efficiency = 1
            )

        def get_pt_50_t(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
            index = index,
            station_name = station_name,
            block_name = 'ПТ-50_Т',
            nominal_el_value = 50,
            min_power_fraction = 0.4,
            input_flow = self.global_natural_gas_flow,
            output_flow_el = self.global_el_flow,
            output_flow_T = output_flow_T,
            nominal_input_T = 200,
            efficiency_T = 0.91,
            heat_to_el_T = 2.02,
            variable_costs = 0,
            boiler_efficiency = 1
            )
##################################################################################   
# ПТ - 60
##################################################################################   
        def get_pt_60(self, index, station_name, output_flow_P, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-60',
                nominal_el_value = 60,
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
                boiler_efficiency = 1
            )
   
        def get_pt_60_p(self, index, station_name, output_flow_P):
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-60_П',
                nominal_el_value = 60,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                nominal_input_P = 300,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 1
            )
   
        def get_pt_60_t(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                index = index,
                station_name = station_name,
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
                boiler_efficiency = 1
            )

##################################################################################   
# ПТ - 65
##################################################################################    
        def get_pt_65(self, index, station_name, output_flow_P, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine(
                index = index,
                station_name = station_name,
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
                boiler_efficiency = 1
            )
   
        def get_pt_65_p(self, index, station_name, output_flow_P):
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-65_П',
                nominal_el_value = 65,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                nominal_input_P = 300,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 1
            )
   
        def get_pt_65_t(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-65_Т',
                nominal_el_value = 65,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                nominal_input_T = 200,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 1
            )
##################################################################################   
# ПТ - 70
##################################################################################    
        def get_pt_70(self, index, station_name, output_flow_P, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-70',
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
                boiler_efficiency = 1
            )
   
        def get_pt_70_p(self, index, station_name, output_flow_P):
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-70_П',
                nominal_el_value = 70,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                nominal_input_P = 300,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 1
            )
   
        def get_pt_70_t(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-70_Т',
                nominal_el_value = 70,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                nominal_input_T = 200,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 1
            )
##################################################################################
# ПТ - 135
##################################################################################   
        def get_pt_135(self, index, station_name, output_flow_P, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-135',
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
                boiler_efficiency = 1
            )
   
        def get_pt_135_p(self, index, station_name, output_flow_P):
            return self.g_block_creator.create_chp_PT_turbine_full_P_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-135_П',
                nominal_el_value = 135,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                nominal_input_P = 300,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 1
            )
   
        def get_pt_135_t(self, index, station_name, output_flow_T):
            return self.g_block_creator.create_chp_PT_turbine_full_T_mode(
                index = index,
                station_name = station_name,
                block_name = 'ПТ-135_Т',
                nominal_el_value = 135,
                min_power_fraction = 0.4,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_T = output_flow_T,
                nominal_input_T = 200,
                efficiency_T = 0.91,
                heat_to_el_T = 2.02,
                variable_costs = 0,
                boiler_efficiency = 1
            )
 ##################################################################################
 # ВВЭР-1200
 ##################################################################################
        def get_vver_1200(self, index, station_name, variable_costs, planning_outage = None):
            return self.g_block_creator.create_NPP_block(
                index = index,
                station_name = station_name,
                block_name = 'ВВЭР-1200',
                nominal_el_value = 1170,
                min_power_fraction = 0.75,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
            )
##################################################################################
 # ВВЭР-ТОИ
 ##################################################################################
        def get_vver_toi(self, index, station_name, variable_costs, planning_outage = None):
            return self.g_block_creator.create_NPP_block(
                index = index,
                station_name = station_name,
                block_name = 'ВВЭР-ТОИ',
                nominal_el_value = 1255,
                min_power_fraction = 0.75,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
            )
 ##################################################################################
 # ВВЭР-600
 ##################################################################################
        def get_vver_600(self, index, station_name, variable_costs, planning_outage = None):
            return self.g_block_creator.create_NPP_block(
                index = index,
                station_name = station_name,
                block_name = 'ВВЭР-600',
                nominal_el_value = 600,
                min_power_fraction = 0.65,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
            )
 ##################################################################################
 # РИТМ-200
 ##################################################################################
        def get_ritm_200(self, index, station_name, variable_costs, planning_outage = None):
            return self.g_block_creator.create_NPP_block(
                index = index,
                station_name = station_name,
                block_name = 'РИТМ-200',
                nominal_el_value = 50,
                min_power_fraction = 0.65,
                output_flow = self.global_el_flow,
                variable_costs = variable_costs,
            )



        def get_p_50(self, index, station_name, output_flow_P):
            return self.g_block_creator.create_back_pressure_turbine(
                index = index,
                station_name = station_name,
                block_name = 'Р-50',
                nominal_el_value = 50,
                min_power_fraction = 0.35,
                input_flow = self.global_natural_gas_flow,
                output_flow_el = self.global_el_flow,
                output_flow_P = output_flow_P,
                efficiency_P = 0.91,
                heat_to_el_P = 3.8,
                variable_costs = 0,
                boiler_efficiency = 1
            )

        def get_dummy_source(self, index, station_name, label ,output_flow, variable_costs = 9999):
            return self.g_source_creator.create_source(
                    label=set_label(station_name ,'Dummy', label, str(index)),
                    output_flow=output_flow,
                    variable_costs = variable_costs
            )
            
        
        

   
   
   
   
   
        
 
 