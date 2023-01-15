from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt



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



class Custom_result_processor:
    
    
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
            res = self.custom_es.get_all_el_blocks()
        elif commodity_type == 'гвс':
            res = self.custom_es.get_all_heat_water_blocks()
        elif commodity_type == 'пар':
            res = self.custom_es.get_all_steam_blocks()
        return res
            
        
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
            elif b2_station_order > b2_station_order:
                return 1
            else:
                return -1
        
        blocks = self.__get_block_by_commodity_type(commodity_type)
        blocks.sort(key = __comparator_block_station_plot_1)
        el_bus = self.custom_es.get_global_output_flow
        results = solph.views.node(self.processed_results, el_bus.label)["sequences"].dropna()      
        res = pd.DataFrame()
        for block in blocks:
            pd[block.label] = results[((block.label, el_bus.label),'flow')]
        return res      
    
    
    def __get_dataframe_block_station_type_plot_2(self, commodity_type):
        def __comparator_block_station_type_plot_2(b1, b2):
            b1_station_type = b1.group_options['station_type']
            b2_station_type = b2.group_options['station_type']
            if b1_station_type == b2_station_type:
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
            elif b2_station_type > b2_station_type:
                return 1
            else:
                return -1        
        def get_dataframe_plot_1_by_commodity(sorted_blocks, commodite_type):
            if commodity_type == 'электроэнергия':
                output_bus = self.custom_es.global_el_flow
                results = solph.views.node(self.processed_results, output_bus.label)["sequences"].dropna()      
                res = pd.DataFrame()
                for el_block in sorted_blocks:
                     pd[el_block.label] = results[((el_block.label, output_bus.label), 'flow')]
                return res    
            elif commodity_type == 'гвс':
                for hw_block in sorted_blocks:
                    
                    current_station_name = hw_block.group_options['station_name']
                    current_hw_bus = self.custom_es.get_heat_water_bus_by_station(current_station_name)
                    hw_proccessed_results = solph.views.node(self.processed_results, current_hw_bus.label)["sequences"].dropna()
                    
                
                            
    
        
        
        blocks = self.__get_block_by_commodity_type(commodity_type)
        blocks.sort(key = __comparator_block_station_type_plot_2)
        res = get_dataframe_plot_1_by_commodity(sorted_blocks, commodity_type)
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
        blocks = self.__get_block_by_commodity_type(commodity_type)
        blocks.sort(key = __comparator_station_plot_3)
        el_bus = self.custom_es.get_global_output_flow
        results = solph.views.node(self.processed_results, el_bus.label)["sequences"].dropna()      
        i = 0 
        data = {}
        while i < len(blocks):
            current_station_outer = blocks[i].group_options['station_name']
            current_station_inner = current_station_inner
            data[current_station_inner] = []
            while (current_station_inner == current_station_outer) and (i < len(blocks)):
                current_station_inner = blocks[i].group_options['station_name']
                block_data = results[((blocks[i].label, el_bus.label),'flow')]
                data[current_station_inner].append(blocks[i]) # collect data
                i = i + 1
        res = get_dataframe_from_dict(data)
        return res
           
        
    def __get_dataframe_station_type_plot_4(self, commodity_type):
        def __comparator_station_type_plot_4(b1, b2):
            b1_station_type = b1.group_options['station_type']
            b2_station_type = b2.group_options['station_type']
            if b1_station_type == b2_station_type:
                return 0
            elif b1_station_type > b2_station_type:
                return 1
            elif b1_station_type < b2_station_type:
                return -1

        blocks = self.__get_block_by_commodity_type(commodity_type)
        blocks.sort(key = __comparator_station_type_plot_4)
        el_bus = self.custom_es.get_global_output_flow
        results = solph.views.node(self.processed_results, el_bus.label)["sequences"].dropna()      
        res = pd.DataFrame()
        i = 0 
        data_inner = []
        data_outer = []
        while i < len(blocks):
            current_station_type_outer = blocks[i].group_options['station_type']
            current_station_type_inner = current_station_type_inner
            while (current_station_type_inner == current_station_type_outer) and (i < len(blocks)):
                current_station_type_inner = blocks[i].group_options['station_type']
                data_inner.append(current_station_type_inner)
                # collect data
                i = i + 1
            # process data
    
    
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
            elif b2_station_order > b2_station_order:
                return 1
            elif b2_station_order < b2_station_order:
                return -1        
                # нужно объединенеие
        blocks = self.__get_block_by_commodity_type(commodity_type)
        blocks.sort(key = __comparator_block_type_station_plot_5)
        el_bus = self.custom_es.get_global_output_flow
        results = solph.views.node(self.processed_results, el_bus.label)["sequences"].dropna()      
        res = pd.DataFrame()
        i = 0 
        data_inner = {}
        data_outer = []
        while i < len(blocks):
            current_block_type_outer = blocks[i].group_options['block_type']
            current_station = blocks[i].group_options['station_name']
            data_inner[current_station] = []  
            current_block_type_inner = current_block_type_inner
            while (current_block_type_inner == current_block_type_outer) and (i < len(blocks)):
                current_block_type_inner = blocks[i].group_options['block_type']
                data_inner[current_station].append(current_block_type_inner)
                # collect data
                i = i + 1
            # process data
    
    
    def __get_dataframe_block_type_station_type_plot_6(self, commodity_type):
        def __comparator_block_type_station_type_plot_6(b1, b2):
            b1_station_type = b1.group_options['station_type']
            b2_station_type = b2.group_options['station_type']
            if b1_station_type == b2_station_type:
                b1_block_type_order = b1.group_options['block_type_order']
                b2_block_type_order = b2.group_options['block_type_order']
                if b1_block_type_order == b2_block_type_order:
                    return 0
                elif b1_block_type_order > b2_block_type_order:
                    return 1
                elif b1_block_type_order < b2_block_type_order:
                    return -1
            elif b2_station_type > b2_station_type:
                return 1
            elif  b2_station_type < b2_station_type:
                return -1        
        blocks = self.__get_block_by_commodity_type(commodity_type)
        blocks.sort(key = __comparator_block_type_station_type_plot_6)
        el_bus = self.custom_es.get_global_output_flow
        results = solph.views.node(self.processed_results, el_bus.label)["sequences"].dropna()      
        res = pd.DataFrame()
        i = 0 
        data_inner = {}
        data_outer = []
        while i < len(blocks):
            current_block_type_outer = blocks[i].group_options['block_type']
            current_station = blocks[i].group_options['station_type']
            data_inner[current_station] = []  
            current_block_type_inner = current_block_type_inner
            while (current_block_type_inner == current_block_type_outer) and (i < len(blocks)):
                current_block_type_inner = blocks[i].group_options['block_type']
                data_inner[current_station].append(current_block_type_inner)
                # collect data
                i = i + 1
            # process data
    
    
        
    def set_block_station_plot_1(self, data):
        self.custom_es.set_block_type_in_station_order(data)
        self.select_plot_type = 1
       
    
    def set_block_station_type_plot_2(self, data_station_type, data_bloc_type_station_order):
        self.custom_es.set_station_type(data_station_type)
        self.custom_es.set_block_type_in_station_type_order(data_bloc_type_station_order)
        self.select_plot_type = 2
    
        
    def set_station_plot_3(self, data):
        self.custom_es.set_station_order(data)
        self.select_plot_type = 3
        
    def set_station_type_plot_4(self, data):
        self.custom_es.set_station_type(data)
        self.select_plot_type = 4
        
            
    def set_block_type_station_plot_5(self, data_station_order, data_block_type_in_station):
        self.custom_es.set_station_order(data_station_order)
        self.custom_es.set_block_type_in_station_order(data_block_type_in_station)
        self.select_plot_type = 5
        
    def set_block_type_station_type_plot_6(self, data_station_type, data_block_type_in_station_type):
        self.custom_es.set_station_type_with_order(data_station_type)
        self.custom_es.set_block_type_in_station_type(data_block_type_in_station_type)
        self.select_plot_type = 6
  
  
  
  
    class Custom_color_setter:
        def __init__(self, custom_es) -> None:
            self.custom_es = custom_es
            
            
        def set_color_by_block_type(self, block_type, color):
            pass
                
        def set_color_by_station(self, station_name, color):
            pass
        
        def set_color_by_station_type(self, station_type, color):
            pass
        
        def set_color_by_id(self, color):
            pass

        def set_color_by_station_block_type(self, station, block_type, color):
            pass
        
        def set_color_by_station_type_block_type(self, station_type, block_type, color):
            pass
        
        
              
    

    class Custom_plotter_el_hw_steam:
        def __init__(self, df_el, df_hw, df_steam):
            pass
                                               
        def set_max_value(self, max_value):
            pass
         
        def set_X_label(self, plot_type):
           pass
                    
        def set_Y_label(self, plot_type):
           pass
            
        def set_label(self, plot_type):
            pass    