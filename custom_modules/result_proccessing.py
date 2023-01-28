from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from functools import cmp_to_key
from custom_modules.helpers import convert_Mwth_to_1000_m3



class Custom_result_extractor:
    def __init__(self, custom_es, processed_results):
        self.custom_es = custom_es
        self.processed_results = processed_results
        self.custom_es.set_heat_water_groupname_all_stations('гвс')
        self.custom_es.set_steam_groupname_all_stations('пар')  

###########################################################################################
#                                использование природного газ
###########################################################################################
    def get_natural_gas_price(self):
        'получить установленную цену на природный газ (долл. США за 1000 м3)'
        return self.custom_es.natural_gas_price

    def get_total_gas_consumption_value_m3(self, scale):
        'получить суммарное потребление природного газа в энергосистеме'
        global_gas_source = self.custom_es.global_gas_source
        global_gas_bus = self.custom_es.global_input_bus
        results = solph.views.node(self.processed_results, global_gas_bus.label)["sequences"].dropna() 
        res = pd.DataFrame()
        res['потребление газа'] = results[((global_gas_source.label, global_gas_bus.label), 'flow')]
        total_gas_consumption_Mwth =  res['потребление газа'].sum()
        total_gas_consumption_1000_m3 = convert_Mwth_to_1000_m3(total_gas_consumption_Mwth)
        if scale == 'млн':
            divider = 1_000
        elif scale == 'млрд':
            divider = 1_000_000
        else:
            raise Exception('Не выбраны единицы')
        total_gas_consumption = round(total_gas_consumption_1000_m3 / divider, 3) 
        return total_gas_consumption

    def get_total_gas_consumtion_by_block_type(self, block_type):
        'получить затраченный объем газа для указанного типа блока (млн. 1000 м3)'
        pass
    
    def get_total_gas_energy_generation_part(self):
        'получить долю генерации энергии природного газа в энергосистеме'
        pass
    
    def get_total_gas_consumption_by_station_type(self, station_type):
        'получить объем использованного природного газа указанной типа станции'
        pass
    
    def get_total_gas_consumption_by_station_value(self, station_name):
        'получить объем использованного природного газа указанной  станции'
        pass
###########################################################################################
#                               генерация электроэнергии
###########################################################################################
    def get_dataframe_orig_electricity_demand(self):
        'возвращает исходный профиль электрической нагрузки'        
        pass
    
    def get_total_electricity_generation_value(self):
        pass
    
    def get_chp_el_energy_by_station(self, station_name):
        'получить электроэнергию выработанную на тепловом потреблении для указанной станции'
        pass
    
    def get_chp_el_energy(self):
        'получить электроэнергию выработанную на тепловом потреблении в энергосистеме'
        pass
    
    
    def get_total_npp_energy_generation_part(self):
        'получить долю генерации энергии от АЭС'
        pass
    
    
    def get_el_energy_by_block_type(self, block_type):
        'получить объем электрической энергии для указанного типа блока'
        pass
    
    
    def get_el_energy_by_station(self, station_name):
        'получить объем электрической энергии для указанной станции'
        pass
    
        
    def get_el_energy_by_station_type(self, station_type):
        'получить объем электрической энергии для указанного типа станции'
        pass
###########################################################################################
#                               генерация тепла
###########################################################################################   
    def get_total_heat_generation_value_by_station(self, station_name, commodite_type):
        pass
    
    def get_total_heat_generation_by_type(self, commodite_type):
        pass
    
    def get_total_heat_generation(self):
        pass
###########################################################################################   
#                                    электрокотлы
###########################################################################################   
    
    def get_install_el_boilers_power(self, commodite_type):
        'получить установленную мощность электрокотлов в энергосистеме'
        el_boilers = self.custom_es.get_all_blocks_by_block_type('эк')
        el_boilers = self.custom_es.filter_block_list_by_group_options_attr(el_boilers, 'heat_demand_type', commodite_type)
        el_boilers_power = self.custom_es.get_install_power_blocklist(el_boilers)
        return el_boilers_power
    
    def get_install_el_boilers_power_by_station(self, station_name, commodite_type):
        'получить мощность электротлов для указанной станции (ГВС или ПАР)'
        pass
    
    def get_max_el_boilers_power_by_station_value(self, station_name, commodite_type):
        'получить суммарное максимальной использование электрокотлов для указанной станции (ГВС или ПАР)'
        pass
    
    def get_max_el_boilers_load_value(self):
        pass
    
    def get_dataframe_el_boilers_consumption(self, commodite_type):
        'получить датафрейм потребления всех электрокотлов (ГВС или ПАР)'
        pass
    
    def get_dataframe_el_boilers_consumption_by_station(self, station_name, commodite_type):
        'получить датафрейм потребления электрокотлов указ. типа (гвс или пар) для указанной станции'
        pass
    
    def get_total_el_boilers_consumption_value(self, commodite_type):
        'получить  потребление всех электрокотлов указ. типа (гвс или пар)'
        pass

    
    def get_total_el_boilers_consumption_value(self, station_name, commodite_type):
        'получить  потребление всех электрокотлов указ. типа (гвс или пар) для указанной станции ' 
        pass
###########################################################################################   
#                          электрическая мощность 
###########################################################################################               
    def get_install_energy_system_power(self):
        'получить установленную мощность энергосистемы (МВТ(э))'
        return self.custom_es.get_install_energy_system_power()   

    def get_dataframe_online_power(self):
        'получить датафрейм включенной мощности'
        output_bus = self.custom_es.global_output_bus
        results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
        el_blocks = self.custom_es.get_all_el_blocks()
        blocks_df = pd.DataFrame()
        for el_block in el_blocks:
                blocks_df[el_block.label] = results[((el_block.label, output_bus.label), 'flow')]
        blocks_df[blocks_df < 0] = 0     
        time_length = len(blocks_df.index)
        for el_block in el_blocks:
            nominal_el_value = el_block.group_options['nominal_value']
            blocks_df.loc[blocks_df[el_block.label] > 0, el_block.label] = nominal_el_value
        blocks_df = blocks_df.loc[:, (blocks_df > 0.1).any(axis=0)]
        blocks_df = blocks_df.sum(axis=1)
        blocks_df = pd.DataFrame(blocks_df)
        blocks_df.columns = ['Включенная мощность']
        return blocks_df  
    
    def get_dataframe_online_power_by_station(self, station_name):
        'получить датафрейм включенной мощности для указанной станции'
        output_bus = self.custom_es.global_output_bus
        results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
        el_blocks = self.custom_es.get_el_blocks_by_station(station_name)
        blocks_df = pd.DataFrame()
        for el_block in el_blocks:
                blocks_df[el_block.label] = results[((el_block.label, output_bus.label), 'flow')]
        blocks_df[blocks_df < 0] = 0     
        time_length = len(blocks_df.index)
        for el_block in el_blocks:
            nominal_el_value = el_block.group_options['nominal_value']
            blocks_df.loc[blocks_df[el_block.label] > 0, el_block.label] = nominal_el_value
        blocks_df = blocks_df.loc[:, (blocks_df > 0.1).any(axis=0)]
        blocks_df = blocks_df.sum(axis=1)
        blocks_df = pd.DataFrame(blocks_df)
        blocks_df.columns = ['Включенная мощность ' + station_name]
        return blocks_df  

    def get_dataframe_load_fraction(self):
        'получить датафрейм отношение установленной мощности к текущей нагрузке'
        pass
    def load_factor_by_station(self, station_name):
        'получить коэффициент установленной электрической мощности для станции'
        pass
###########################################################################################   
#                          себестоимость электроэнергии
###########################################################################################        
    def get_usd_MWth_by_station(self, station):
        'получить себестоимость производства для указанной станции'
        pass
    
    def get_usd_MWth_total(self):
        'получить полную себестоимость производства для энергосистемы'
        pass
###########################################################################################        



class Custom_result_grouper:
    
    
    def __init__(self, custom_es, processed_results):
        self.processed_results = processed_results
        self.custom_es = custom_es
        self.custom_es.set_heat_water_groupname_all_stations('гвс')
        self.custom_es.set_steam_groupname_all_stations('пар')
        self.select_plot_type = 0
        
        
    def get_dataframe_by_commodity_type(self, commodity_type):
        'общий метод расчета результирующего датарфрейма' 
        '(commodite_type = электроэнергия, гвс, пар)'
        if self.select_plot_type == 1:
            res = self.__get_dataframe_block_station_plot_1(commodity_type)
        elif self.select_plot_type == 2:
            res = self.__get_dataframe_block_station_type_plot_2(commodity_type)
        elif self.select_plot_type == 3:
            res = self.__get_dataframe_station_plot_3(commodity_type)
        elif self.select_plot_type == 4:
            res = self.__get_dataframe_station_type_plot_4(commodity_type)
        elif self.select_plot_type == 5:
            res = self.__get_dataframe_block_type_station_plot_5(commodity_type)
        elif self.select_plot_type == 6:
            res = self.__get_dataframe_block_type_station_type_plot_6(commodity_type)
        else:
            raise Exception('Не выбран тип графика')
        return res
        
        
    def get_dataframe_from_dict(self,data):
        res = pd.DataFrame()
        stations_names = data.keys()
        
        # потом убрать
    def get_dataframe_orig_electricity_demand(self, el_bus, el_sink):
        'возвращает исходный профиль электрической нагрузки'        
        results = solph.views.node(self.processed_results, el_bus.label)["sequences"].dropna()      
        res = pd.DataFrame()
        res[el_sink.label] = results[((el_bus.label, el_sink.label),'flow')]
        return res      
        
    def __get_block_by_commodity_type(self, commodity_type):
        if commodity_type == 'электроэнергия':
            data = self.custom_es.get_all_el_blocks()
            return data
        elif commodity_type == 'гвс':
            return  self.custom_es.get_all_heat_water_blocks()
        elif commodity_type == 'пар':
            return self.custom_es.get_all_steam_blocks()
            
        
        
    def __get_dataframe_block_station_plot_1(self, commodity_type):
        def __comparator_block_station_plot_1(b1, b2):
            b1_station_order = b1.group_options['station_order']
            b2_station_order = b2.group_options['station_order']
            if b1_station_order == b2_station_order:
                b1_block_type_order = b1.group_options['block_type_order']
                b2_block_type_order = b2.group_options['block_type_order']
                if b1_block_type_order == b2_block_type_order:
                    b1_power = b1.group_options['nominal_value']
                    b2_power = b2.group_options['nominal_value']
                    if b1_power == b2_power:
                        return 0
                    elif b1_power > b2_power:
                        return -1
                    elif b1_power < b2_power:
                        return 1
                elif b1_block_type_order > b2_block_type_order:
                    return 1
                elif b1_block_type_order < b2_block_type_order:
                    return -1
            elif b1_station_order > b2_station_order:
                return 1
            elif b1_station_order < b2_station_order:
                return -1
        def get_dataframe_plot_1_by_commodity(sorted_blocks, commodite_type):
            if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.get_global_output_flow()
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                res = pd.DataFrame()
                for el_block in sorted_blocks:
                     res[el_block.label] = results[((el_block.label, output_bus.label), 'flow')]
                res[res < 0] = 0     
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res    
            elif commodity_type in ['гвс', 'пар']:
                i = 0
                length = len(sorted_blocks)
                res = pd.DataFrame()
                bus_getter = self.custom_es.get_heat_water_bus_by_station if commodite_type == 'гвс' else self.custom_es.get_steam_bus_by_station
                while i < length:
                    current_station_name_outer = sorted_blocks[i].group_options['station_name']
                    current_station_name_inner = current_station_name_outer
                    current_energy_bus = bus_getter(current_station_name_inner) 
                    hw_proccessed_results = solph.views.node(self.processed_results, current_energy_bus.label)["sequences"].dropna()
                    while current_station_name_inner == current_station_name_outer and i < length:
                        res[sorted_blocks[i].label] = hw_proccessed_results[((sorted_blocks[i].label, current_energy_bus.label), 'flow')]
                        i = i + 1
                        if i < length:
                           current_station_name_inner = sorted_blocks[i].group_options['station_name']
                        else:
                            break
                res[res < 0] = 0   
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res
        
        
        blocks = self.__get_block_by_commodity_type(commodity_type)
        # for block in blocks:
        #     print(block.group_options['station_name'],
        #           block.group_options['station_order'],
        #           block.group_options['block_type'],
        #           block.group_options['block_type_order'],
        #           block.group_options['nominal_value'])
        # print('----------------------------------------------')
        sorted_blocks = sorted(blocks, key = cmp_to_key(__comparator_block_station_plot_1))
        # sorted(blocks, key = __comparator_block_station_plot_1)
        # blocks.sort(key = __comparator_block_station_plot_1 )
        # for block in blocks:
        #     print(block.group_options['station_name'],
        #           block.group_options['station_order'],
        #           block.group_options['block_type'],
        #           block.group_options['block_type_order'],
        #           block.group_options['nominal_value'])
        # blocks.sort(key = __comparator_block_station_plot_1)
        res = get_dataframe_plot_1_by_commodity(sorted_blocks, commodity_type)
        return res      
    
    
    def __get_dataframe_block_station_type_plot_2(self, commodity_type):
        def __comparator_block_station_type_plot_2(b1, b2):
            b1_station_type_order = b1.group_options['station_type_order']
            b2_station_type_order = b2.group_options['station_type_order']
            if b1_station_type_order == b2_station_type_order:
                b1_block_type_order = b1.group_options['block_type_order']
                b2_block_type_order = b2.group_options['block_type_order']
                if b1_block_type_order == b2_block_type_order:
                    b1_power = b1.group_options['nominal_value']
                    b2_power = b2.group_options['nominal_value']
                    if b1_power == b2_power:
                        return 0
                    elif b1_power > b2_power:
                        return -1
                    elif b1_power < b2_power:
                        return 1
                elif b1_block_type_order > b2_block_type_order:
                    return 1
                elif b1_block_type_order < b2_block_type_order:
                    return -1
            elif b1_station_type_order > b2_station_type_order:
                return 1
            elif b1_station_type_order < b2_station_type_order: 
                return -1        
        def get_dataframe_plot_2_by_commodity(sorted_blocks, commodite_type):
            if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.get_global_output_flow()
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                res = pd.DataFrame()
                for el_block in sorted_blocks:
                     res[el_block.label] = results[((el_block.label, output_bus.label), 'flow')]
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res    
            elif commodity_type in ['гвс', 'пар']:
                i = 0
                length = len(sorted_blocks)
                res = pd.DataFrame()
                bus_getter = self.custom_es.get_heat_water_bus_by_station if commodite_type == 'гвс' else self.custom_es.get_steam_bus_by_station
                while i < length:
                    current_station_name_outer = sorted_blocks[i].group_options['station_name']
                    current_station_name_inner = current_station_name_outer
                    current_energy_bus = bus_getter(current_station_name_inner) 
                    hw_proccessed_results = solph.views.node(self.processed_results, current_energy_bus.label)["sequences"].dropna()
                    while current_station_name_inner == current_station_name_outer and i < length:
                        res[sorted_blocks[i].label] = hw_proccessed_results[((sorted_blocks[i].label, current_energy_bus.label), 'flow')]
                        i = i + 1
                        if i < length:
                           current_station_name_inner = sorted_blocks[i].group_options['station_name']
                        else:
                            break
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res
        
        blocks = self.__get_block_by_commodity_type(commodity_type)
        sorted_blocks = sorted(blocks, key = cmp_to_key(__comparator_block_station_type_plot_2))
        res = get_dataframe_plot_2_by_commodity(sorted_blocks, commodity_type)
        return res

     
    def __get_dataframe_station_plot_3(self, commodity_type):
        def __comparator_station_plot_3(b1, b2):
            b1_station_order = b1.group_options['station_order']
            b2_station_order = b2.group_options['station_order']
            if b1_station_order == b2_station_order:
                return 0
            elif b1_station_order > b2_station_order:
                return 1
            elif  b1_station_order < b2_station_order:
                return -1
        def get_dataframe_plot_3_by_commodity(sorted_blocks, commodite_type):
             if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.get_global_output_flow()
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                length = len(sorted_blocks)
                i = 0
                data_to_union = {}
                while i < length:
                    current_station_name_outer = sorted_blocks[i].group_options['station_name']
                    current_station_name_inner = current_station_name_outer
                    data_to_union[current_station_name_inner] = []
                    while current_station_name_inner == current_station_name_outer and i < length:
                        data = results[((sorted_blocks[i].label, output_bus.label), 'flow')]
                        data_to_union[current_station_name_inner].append(data) 
                        i = i + 1
                        if i < length:
                            current_station_name_inner = sorted_blocks[i].group_options['station_name']
                        else:
                            break
                res = []
                station_names = []
                for station_name, blocks in data_to_union.items():
                    df = pd.concat(blocks, axis=1)
                    df2  = df.sum(axis = 1)
                    res.append(df2) 
                    station_names.append(station_name)
                res = pd.concat(res, axis=1)
                res.columns = station_names
                res[res < 0] = 0    
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res    
             elif commodity_type in ['гвс', 'пар']:
                i = 0
                length = len(sorted_blocks)
                res = pd.DataFrame()
                bus_getter = self.custom_es.get_heat_water_bus_by_station if commodite_type == 'гвс' else self.custom_es.get_steam_bus_by_station
                data_to_union = {}
                while i < length:
                    current_station_name_outer = sorted_blocks[i].group_options['station_name']
                    current_station_name_inner = current_station_name_outer
                    current_energy_bus = bus_getter(current_station_name_inner) 
                    data_to_union[current_station_name_inner] = []
                    hw_proccessed_results = solph.views.node(self.processed_results, current_energy_bus.label)["sequences"].dropna()
                    while current_station_name_inner == current_station_name_outer and i < length:
                        data = hw_proccessed_results[((sorted_blocks[i].label, current_energy_bus.label), 'flow')]
                        data_to_union[current_station_name_inner].append(data)
                        i = i + 1
                        if i < length:
                           current_station_name_inner = sorted_blocks[i].group_options['station_name']
                        else:
                            break
                        
                res = []
                station_names = []
                for station_name, blocks in data_to_union.items():
                    df = pd.concat(blocks, axis=1)
                    df2  = df.sum(axis = 1)
                    res.append(df2) 
                    station_names.append(station_name)
                res = pd.concat(res, axis=1)
                res.columns = station_names        
                res[res < 0] = 0      
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res
            
            

        blocks = self.__get_block_by_commodity_type(commodity_type)
        sorted_blocks = sorted(blocks, key = cmp_to_key(__comparator_station_plot_3))          
        res = get_dataframe_plot_3_by_commodity(sorted_blocks, commodity_type)
        return res
           
        
        
    def __get_dataframe_station_type_plot_4(self, commodity_type):
        def __comparator_station_type_plot_4(b1, b2):
            b1_station_type = b1.group_options['station_type_order']
            b2_station_type = b2.group_options['station_type_order']
            if b1_station_type == b2_station_type:
                return 0
            elif b1_station_type > b2_station_type:
                return 1
            elif b1_station_type < b2_station_type:
                return -1

        def get_dataframe_plot_4_by_commodity(sorted_blocks, commodite_type):
            if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.get_global_output_flow()
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                length = len(sorted_blocks)
                i = 0
                data_to_union = {}
                while i < length:
                    current_station_type_outer = sorted_blocks[i].group_options['station_type']
                    current_station_type_inner = current_station_type_outer
                    data_to_union[current_station_type_inner] = []
                    while current_station_type_inner == current_station_type_outer and i < length:
                        data = results[((sorted_blocks[i].label, output_bus.label), 'flow')]
                        data_to_union[current_station_type_inner].append(data) 
                        i = i + 1
                        if i < length:
                            current_station_type_inner = sorted_blocks[i].group_options['station_type']
                        else:
                            break
                res = []
                station_types = []
                for station_name, blocks in data_to_union.items():
                    df = pd.concat(blocks, axis=1)
                    df2  = df.sum(axis = 1)
                    res.append(df2) 
                    station_types.append(station_name)
                res = pd.concat(res, axis=1)
                res.columns = station_types
                res[res < 0] = 0    
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res    
            elif  commodity_type in ['гвс', 'пар']:
                i = 0
                length = len(sorted_blocks)
                bus_getter = self.custom_es.get_heat_water_bus_by_station if commodite_type == 'гвс' else self.custom_es.get_steam_bus_by_station
                data_to_union = {}
                while i < length:
                    current_station_type_outer = sorted_blocks[i].group_options['station_type']
                    current_station_type_inner = current_station_type_outer
                    data_to_union[current_station_type_inner] = []
                    while current_station_type_inner == current_station_type_outer and i < length:
                        current_station = sorted_blocks[i].group_options['station_name']
                        current_energy_bus = bus_getter(current_station) 
                        hw_proccessed_results = solph.views.node(self.processed_results, current_energy_bus.label)["sequences"].dropna()
                        data = hw_proccessed_results[((sorted_blocks[i].label, current_energy_bus.label), 'flow')]
                        data_to_union[current_station_type_inner].append(data)
                        i = i + 1
                        if i < length:
                           current_station_type_inner = sorted_blocks[i].group_options['station_type']
                        else:
                            break
                        
                res = []
                station_names = []
                for station_name, blocks in data_to_union.items():
                    df = pd.concat(blocks, axis=1)
                    df2  = df.sum(axis = 1)
                    res.append(df2) 
                    station_names.append(station_name)
                res = pd.concat(res, axis=1)
                res.columns = station_names        
                res[res < 0] = 0            
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res

        blocks = self.__get_block_by_commodity_type(commodity_type)
        sorted_blocks = sorted(blocks, key = cmp_to_key(__comparator_station_type_plot_4))          
        res = get_dataframe_plot_4_by_commodity(sorted_blocks, commodity_type)
        return res
    
    
    
    
    def __get_dataframe_block_type_station_plot_5(self, commodity_type):
        def __comparator_block_type_station_plot_5(b1, b2):
            b1_station_order = b1.group_options['station_order']
            b2_station_order = b2.group_options['station_order']
            if b1_station_order == b2_station_order:
                b1_block_type_order = b1.group_options['block_type_order']
                b2_block_type_order = b2.group_options['block_type_order']
                if b1_block_type_order == b2_block_type_order:
                    return 0
                elif b1_block_type_order > b2_block_type_order:
                    return 1
                elif b1_block_type_order < b2_block_type_order:
                    return -1
            elif b1_station_order > b2_station_order:
                return 1
            elif b1_station_order < b2_station_order:
                return -1       
        def get_dataframe_plot_5_by_commodity(sorted_blocks, commodite_type):
            if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.get_global_output_flow()
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                length = len(sorted_blocks)
                i = 0
                data_to_union = {}
                while i < length:
                    current_station_name_outer = sorted_blocks[i].group_options['station_name']
                    current_station_name_inner = current_station_name_outer

                    while current_station_name_inner == current_station_name_outer and i < length:
                        current_block_type_outer = sorted_blocks[i].group_options['block_type']
                        current_block_type_inner = current_block_type_outer
                        data_to_union[(current_station_name_inner, current_block_type_inner)] = []

                        while current_block_type_inner == current_block_type_outer and i < length and current_station_name_inner == current_station_name_outer:
                           
                            data = results[((sorted_blocks[i].label, output_bus.label), 'flow')]
                            data_to_union[(current_station_name_inner, current_block_type_inner)].append(data) 
                            i = i + 1
                            if i < length:
                                current_block_type_inner = sorted_blocks[i].group_options['block_type']
                                current_station_name_inner = sorted_blocks[i].group_options['station_name']
                                # current_station_name_inner = current_station_name_outer
                            else:
                                break
                        # i = i + 1
                        if i < length:
                                current_station_name_inner = sorted_blocks[i].group_options['station_name']
                        else:
                            break
                items = {}
                for key in data_to_union.keys():
                    item = data_to_union[key]
                    df = pd.concat(item, axis=1)
                    df2 = df.sum(axis=1)
                    items[key[0] +'_'+ key[1]] = df2

                names = items.keys()
                values = list(items.values())
                res = pd.concat(values, axis=1)
                res.columns = names
                res[res < 0] = 0    
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res  
            elif  commodity_type in ['гвс', 'пар']:
                    output_bus = self.custom_es.get_global_output_flow()
                    bus_getter = self.custom_es.get_heat_water_bus_by_station if commodite_type == 'гвс' else self.custom_es.get_steam_bus_by_station
                    length = len(sorted_blocks)
                    i = 0
                    data_to_union = {}
                    while i < length:
                        current_station_name_outer = sorted_blocks[i].group_options['station_name']
                        current_station_name_inner = current_station_name_outer

                        while current_station_name_inner == current_station_name_outer and i < length:
                            current_block_type_outer = sorted_blocks[i].group_options['block_type']
                            current_block_type_inner = current_block_type_outer
                            current_hw_bus = bus_getter(current_station_name_inner)
                            data_to_union[(current_station_name_inner, current_block_type_inner)] = []
                            results = solph.views.node(self.processed_results, current_hw_bus.label)["sequences"].dropna()      


                            while current_block_type_inner == current_block_type_outer and i < length and current_station_name_inner == current_station_name_outer:
                            
                                data = results[((sorted_blocks[i].label, current_hw_bus.label), 'flow')]
                                data_to_union[(current_station_name_inner, current_block_type_inner)].append(data) 
                                i = i + 1
                                if i < length:
                                    current_block_type_inner = sorted_blocks[i].group_options['block_type']
                                    current_station_name_inner = sorted_blocks[i].group_options['station_name']
                                    # current_station_name_inner = current_station_name_outer
                                else:
                                    break
                            # i = i + 1
                            if i < length:
                                    current_station_name_inner = sorted_blocks[i].group_options['station_name']
                            else:
                                break  
                    items = {}
                    for key in data_to_union.keys():
                        item = data_to_union[key]
                        df = pd.concat(item, axis=1)
                        df2 = df.sum(axis=1)
                        items[key[0] +'_'+ key[1]] = df2

                    names = items.keys()
                    values = list(items.values())
                    res = pd.concat(values, axis=1)
                    res.columns = names
                    res[res < 0] = 0    
                    res = res.loc[:, (res > 0.1).any(axis=0)]
                    return res
    
             
        
        
        

        blocks = self.__get_block_by_commodity_type(commodity_type)
        sorted_blocks = sorted(blocks, key = cmp_to_key(__comparator_block_type_station_plot_5))          
        res = get_dataframe_plot_5_by_commodity(sorted_blocks, commodity_type)
        return res
     
    
    
    
    def __get_dataframe_block_type_station_type_plot_6(self, commodity_type):
        def __comparator_block_type_station_type_plot_6(b1, b2):
            b1_station_type_order = b1.group_options['station_type_order']
            b2_station_type_order = b2.group_options['station_type_order']
            if b1_station_type_order == b2_station_type_order:
                b1_block_type_order = b1.group_options['block_type_order']
                b2_block_type_order = b2.group_options['block_type_order']
                if b1_block_type_order == b2_block_type_order:
                    return 0
                elif b1_block_type_order > b2_block_type_order:
                    return 1
                elif b1_block_type_order < b2_block_type_order:
                    return -1
            elif b1_station_type_order > b2_station_type_order:
                return 1
            elif  b1_station_type_order < b2_station_type_order:
                return -1        
        def get_dataframe_plot_6_by_commodity(sorted_blocks, commodite_type):
            if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.get_global_output_flow()
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                length = len(sorted_blocks)
                i = 0
                data_to_union = {}
                while i < length:
                    current_station_type_outer = sorted_blocks[i].group_options['station_type']
                    current_station_type_inner = current_station_type_outer

                    while current_station_type_inner == current_station_type_outer and i < length:
                        current_block_type_outer = sorted_blocks[i].group_options['block_type']
                        current_block_type_inner = current_block_type_outer
                        data_to_union[(current_station_type_inner, current_block_type_inner)] = []

                        while current_block_type_inner == current_block_type_outer and i < length and current_station_type_inner == current_station_type_outer:
                           
                            data = results[((sorted_blocks[i].label, output_bus.label), 'flow')]
                            data_to_union[(current_station_type_inner, current_block_type_inner)].append(data) 
                            i = i + 1
                            if i < length:
                                current_block_type_inner = sorted_blocks[i].group_options['block_type']
                                current_station_type_inner = sorted_blocks[i].group_options['station_type']
                                # current_station_name_inner = current_station_name_outer
                            else:
                                break
                        # i = i + 1
                        if i < length:
                                current_station_type_inner = sorted_blocks[i].group_options['station_type']
                        else:
                            break
                items = {}
                for key in data_to_union.keys():
                    item = data_to_union[key]
                    df = pd.concat(item, axis=1)
                    df2 = df.sum(axis=1)
                    items[key[0] +'_'+ key[1]] = df2

                names = items.keys()
                values = list(items.values())
                res = pd.concat(values, axis=1)
                res.columns = names
                res = res.loc[:, (res > 0.1).any(axis=0)]
                return res  
            elif  commodity_type in ['гвс', 'пар']:
                    output_bus = self.custom_es.get_global_output_flow()
                    bus_getter = self.custom_es.get_heat_water_bus_by_station if commodite_type == 'гвс' else self.custom_es.get_steam_bus_by_station
                    length = len(sorted_blocks)
                    i = 0
                    data_to_union = {}
                    while i < length:
                        current_station_type_outer = sorted_blocks[i].group_options['station_type']
                        current_station_type_inner = current_station_type_outer

                        while current_station_type_inner == current_station_type_outer and i < length:
                            
                            
                            current_block_type_outer = sorted_blocks[i].group_options['block_type']
                            current_block_type_inner = current_block_type_outer
                            data_to_union[(current_station_type_inner, current_block_type_inner)] = []


                            while current_block_type_inner == current_block_type_outer and i < length and current_station_type_inner == current_station_type_outer:
                            
                                
                                current_station_outer = sorted_blocks[i].group_options['station_name']
                                current_station_inner = current_station_outer
                                current_hw_bus = bus_getter(current_station_inner)
                                results = solph.views.node(self.processed_results, current_hw_bus.label)["sequences"].dropna()      

                                while current_station_inner == current_station_outer and i < length and current_block_type_inner == current_block_type_outer and current_station_type_inner == current_station_type_outer:
                                  data = results[((sorted_blocks[i].label, current_hw_bus.label), 'flow')]
                                  data_to_union[(current_station_type_inner, current_block_type_inner)].append(data) 
                                  i = i + 1
                                  if i < length:
                                      current_block_type_inner = sorted_blocks[i].group_options['block_type']
                                      current_station_type_inner = sorted_blocks[i].group_options['station_type']
                                      current_station_inner = sorted_blocks[i].group_options['station_name']
                                  else:
                                        break
                            # i = i + 1
                            if i < length:
                                    current_station_type_inner = sorted_blocks[i].group_options['station_type']
                            else:
                                break  
                            
                            
                            
                            
                    items = {}
                    for key in data_to_union.keys():
                        item = data_to_union[key]
                        df = pd.concat(item, axis=1)
                        df2 = df.sum(axis=1)
                        items[key[0] +'_'+ key[1]] = df2

                    names = items.keys()
                    values = list(items.values())
                    res = pd.concat(values, axis=1)
                    res.columns = names
                    res = res.loc[:, (res > 0.1).any(axis=0)]
                    return res
            
        

        blocks = self.__get_block_by_commodity_type(commodity_type)
        sorted_blocks = sorted(blocks, key = cmp_to_key(__comparator_block_type_station_type_plot_6))          
        res = get_dataframe_plot_6_by_commodity(sorted_blocks, commodity_type)
        return res
    
        
    def set_block_station_plot_1(self, data):
        self.custom_es.set_block_type_in_station_order(data)
        self.select_plot_type = 1
       
    
    def set_block_station_type_plot_2(self, data_station_type, data_bloc_type_station_order):
        self.custom_es.set_station_type_with_order(data_station_type)
        self.custom_es.set_block_type_in_station_type(data_bloc_type_station_order)
        self.select_plot_type = 2
    
        
    def set_station_plot_3(self, data):
        self.custom_es.set_station_order(data)
        self.select_plot_type = 3
        
    def set_station_type_plot_4(self, data):
        self.custom_es.set_station_type_with_order(data)
        self.select_plot_type = 4
        
            
    def set_block_type_station_plot_5(self, data):
        # self.custom_es.set_station_order(data_station_order)
        # self.custom_es.set_block_type_in_station_order(data_block_type_in_station)
        self.custom_es.set_block_type_in_station_order(data)
        self.select_plot_type = 5
        
    def set_block_type_station_type_plot_6(self, data_station_type, data_block_type_in_station_type):
        self.custom_es.set_station_type_with_order(data_station_type)
        self.custom_es.set_block_type_in_station_type(data_block_type_in_station_type)
        self.select_plot_type = 6
  