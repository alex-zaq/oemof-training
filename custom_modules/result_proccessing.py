from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from functools import cmp_to_key



def get_dataframe_by_output_bus_all(results, node_collection, output_bus):
    res = pd.DataFrame()
    results_by_commodity = solph.views.node(results, output_bus.label)["sequences"].dropna()
    # print(results_by_commodity)
    for node in node_collection:
        outputs_node = [str(output) for output in node.outputs]  
        if output_bus.label in outputs_node:
            res[node.label] = results_by_commodity[((node.label, output_bus.label),'flow')]
    return res


def get_dataframe_by_input_bus_all(results, node_collection, input_bus):
    res = pd.DataFrame()
    results_by_commodity = solph.views.node(results, input_bus.label)["sequences"].dropna()
    print(results_by_commodity)
    for node in node_collection:
        inputs_nodes = [str(input) for input in node.inputs]  
        if input_bus.label in inputs_nodes:
            res[node.label] = results_by_commodity[((input_bus.label, node.label),'flow')]
    return res


def get_dataframe_by_output_bus_single(results, block, output_bus):
    res = pd.DataFrame()
    results_by_commodity = solph.views.node(results, output_bus.label)["sequences"].dropna()
    # print(results_by_commodity)
    outputs_node = [str(output) for output in block.outputs]  
    if output_bus.label in outputs_node:
        res[block.label] = results_by_commodity[((block.label, output_bus.label),'flow')]
    return res


def get_dataframe_by_input_bus_single(results, block, input_bus):
    res = pd.DataFrame()
    results_by_commodity = solph.views.node(results, input_bus.label)["sequences"].dropna()
    # print(results_by_commodity)
    inputs_nodes = [str(input) for input in block.inputs]  
    if input_bus.label in inputs_nodes:
        res[block.label] = results_by_commodity[((input_bus.label, block.label),'flow')]
    return res

class Custom_result_extractor:
    def __init__(self, custom_es, processed_results):
        self.custom_es = custom_es
        self.processed_results = processed_results
        pass

            
    def get_natural_gas_price(self):
        return self.custom_es.natural_gas_price

    def get_install_energy_system_power(self):
        return self.custom_es.get_install_energy_system_power()   

    def get_total_gas_consumtion_by_block_type(self, block_type):
        pass

    def get_total_gas_consumption_value(self):
        pass
    
    def get_total_gas_consumption_by_station_type(self):
        pass
    
    def get_total_gas_consumption_by_station_value(self, station_name, commodity_type):
        pass
    
    
    def get_max_el_boilers_consumption_by_station_value(self, station_name, commodite_type):
        pass
    
    
    def get_dataframe_el_boilers_consumption(self, commodite_type):
        pass
    
    def get_total_el_boilers_consumption_value(self, commodite_type):
        pass
  

    def get_dataframe_online_power(self):
        pass
    
    def get_dataframe_online_power_by_station(self):
        pass


    def get_dataframe_load_fraction(self):
        pass
    
    
    def get_el_energy_by_block_type(self, block_type):
        pass
    
    
    def get_el_energy_by_station(self, station_name):
        pass
    
        
    def get_el_energy_by_station_type(self, station_type):
        pass
    
    
    def get_dataframe_spinning_reserve(self):
        # включенная мощность - полная мощность в часу
        pass
    
    
    def load_factor_by_station(self, station_name):
        pass
        
    
    def get_chp_electricity_by_station(self):
        pass
    
    
    def get_usd_MWth_by_station(self, station):
        pass
    
    
    def get_usd_MWth_total(self):
        pass
    
    
    def get_object_value(self):
        pass


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
        elif self.select_plot_type == 0:
            raise Exception('Не выбран тип графика')
        return res
        
        
    def get_dataframe_from_dict(self,data):
        res = pd.DataFrame()
        stations_names = data.keys()
        
        
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
                        return 1
                    elif b1_power < b2_power:
                        return -1
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
  
  
  
  
    # class Custom_color_setter:
    #     def __init__(self, custom_es) -> None:
    #         self.custom_es = custom_es
            
            
    #     def set_color_by_block_type(self, block_type, color):
    #         pass
                
    #     def set_color_by_station(self, station_name, color):
    #         pass
        
    #     def set_color_by_station_type(self, station_type, color):
    #         pass
        
    #     def set_color_by_id(self, color):
    #         pass

    #     def set_color_by_station_block_type(self, station, block_type, color):
    #         pass
        
    #     def set_color_by_station_type_block_type(self, station_type, block_type, color):
    #         pass
        
        
              
    

    # class Custom_plotter_el_hw_steam:
    #     def __init__(self, df_el, df_hw, df_steam):
    #         pass
                                               
    #     def set_max_value(self, max_value):
    #         pass
         
    #     def set_X_label(self, plot_type):
    #        pass
                    
    #     def set_Y_label(self, plot_type):
    #        pass
            
    #     def set_label(self, plot_type):
    #         pass    