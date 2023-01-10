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








class io_result_extractor:
    def __init__(self, processed_results):
        self.processed_results = processed_results

    def get_result_by_output_bus(self, output_bus_data):  
        if isinstance(output_bus_data, list):
            for output_bus in output_bus_data:
                pass # последовательное извлечение
        else:
            return solph.views.node(self.processed_results, output_bus_data.label)["sequences"].dropna()

    def get_result_by_input_bus(self, input_bus_data):
        if isinstance(input_bus_data, list):
            for output_bus in input_bus_data:
                pass # последовательное извлечение
        else:
            return solph.views.node(self.processed_results, input_bus_data.label)["sequences"].dropna()       

    


class Result_processor_el:
    def __init__(self, all_block_el, processed_results, el_output_bus):
        self.all_block_el = all_block_el
        self.el_output_bus = el_output_bus
        self.all_block_el_dict = { block.label:block for block in all_block_el}
        self.processed_results = processed_results
        self.df_station_block_sorted = self.__get_df_station_block()
    

    def get_df_station(self):
        pass
        # создать фрейм с учетом последоватльного объединения в станции (есть порядок - быстро)
        # block_dict = self.all_block_el_dict
        # for block_name in self.df_station_block_sorted:
        #     current_station_name = block_dict[block_name].group_options['станция']
            
        
    # def get_df_station_block_type(self):
    #     # создать фрейм с учетом последоватльного объединения в станции типы блоков (есть порядок - быстро)
    #     pass  
                      
    def get_df_block_type(self):
        # создать фрейм с учетом последоватльного объединения в типы блоков (нет порядка - медленно)
        pass
                                  
    def get_df_station_type(self):
        # создать фрейм с учетом последоватльного объединения в типы станции (есть порядок - быстро)
        pass
                                              
    def get_station_type_block_type(self):
        # создать фрейм с учетом последоватльного объединения в типы станции и типы блоков (нет порядка - медленно)
        pass
            
    def __get_df_station_block(self):
        self.block_list.sort(key = self.__comparator_station_block)   
        all_block_list = self.all_block_list        
        el_output_bus = self.el_output_bus
        results_electricity_output = io_result_extractor(self.processed_results, el_output_bus)
        res = pd.DataFrame()
        for block in all_block_list:
            outputs = [str(output) for output in block.outputs]  
            if el_output_bus in outputs:
                res[block.label] = results_electricity_output[((block.label, el_output_bus.label), 'flow')]
        self.df_station_block_sorted = res

    def __comparator_station_block(b1, b2):
        b1_station_order = b1.group_options['порядок станции']
        b2_station_order = b2.group_options['порядок станции']
        if b1_station_order == b2_station_order:
            b1_block_type_order = b1.group_options['порядок типа блока']
            b2_block_type_order = b2.group_options['порядок типа блока']
            if b1_block_type_order == b2_block_type_order:
                b1_power = b1.group_options['мощность']
                b2_power = b2.group_options['мощность']
                if b1_power == b2_power:
                    return 0
                elif b1_power > b2_power:
                    return 1
                else:
                    return -1
            elif b1_block_type_order > b2_block_type_order:
                return 1
            else:
                return -1
        elif b2_station_order > b2_station_order:
            return 1
        else:
            return -1
            
    
    
class Result_processor_heat:
  def __init__(self, all_block_list_heat, processed_results, heat_bus_list):
    self.processed_results = processed_results
    self.heat_bus_list = heat_bus_list # bus список для всех станций
    self.all_block_list_heat = all_block_list_heat
    self.station_block = self.__get_df_station_block()
    # отсортировать компоратором однократно
    
    def get_df_station(self):
        # создать фрейм с учетом последоватльного объединения в станции (есть порядок - быстро)
        pass    
        
    def get_df_station_block(self):
        # oemof.solph.views.filter_nodes(results, option=<NodeOption.All: 'all'>, exclude_busses=False)
        res = pd.DataFrame()
        for heat_bus in self.heat_bus_list:
            result_by_heat_bus = solph.views.node(self.processing, heat_bus.label)["sequences"].dropna()
            loc_res = pd.DataFrame()
            for heat_block in self.all_block_list_heat:
                outputs = [str(output) for output in heat_block.outputs]
                if heat_bus in outputs:
                   res[heat_block.label] = result_by_heat_bus[((heat_block.label, heat_bus.label), 'flow')]
            res.union(loc_res)
        return res
                
            
        # self.block_list.sort(key = self.comparator)
        # block_list = self.block_list
        # res = pd.DataFrame()
        # results_by_hw = io_result_extractor(self.processed_results, heat_bus_list)
        # # print(results_by_hw)
        # for heat_block in all_block_list_heat:
        #     outputs_node = [str(output) for output in heat_block.outputs]  
        #     if output_bus.label in outputs_node:
        #     res[node.label] = results_by_commodity[((node.label, output_bus.label),'flow')]
        # return res
        
        # содать фрейм согласно сортировке - конец (быстро)
        
        
    def get_df_station_block_type(self):
        # создать фрейм с учетом последоватльного объединения в станции типы блоков (есть порядок - быстро)
        pass  
                      
    def get_df_block_type(self):
        # создать фрейм с учетом последоватльного объединения в типы блоков (нет порядка - медленно)
        pass
                                  
    def get_df_station_type(self):
        # создать фрейм с учетом последоватльного объединения в типы станции (есть порядок - быстро)
        pass
                                              
    def get_station_type_block_type(self):
        # создать фрейм с учетом последоватльного объединения в типы станции и типы блоков (нет порядка - медленно)
        pass
            

    def comparator_station_block(b1, b2):
        b1_station_order = b1.group_options['порядок станции']
        b2_station_order = b2.group_options['порядок станции']
        if b1_station_order == b2_station_order:
            b1_block_type_order = b1.group_options['порядок типа блока']
            b2_block_type_order = b2.group_options['порядок типа блока']
            if b1_block_type_order == b2_block_type_order:
                b1_power = b1.group_options['мощность']
                b2_power = b2.group_options['мощность']
                if b1_power == b2_power:
                    return 0
                elif b1_power > b2_power:
                    return 1
                else:
                    return -1
            elif b1_block_type_order > b2_block_type_order:
                return 1
            else:
                return -1
        elif b2_station_order > b2_station_order:
            return 1
        else:
            return -1
            
     
    
    	# 	графики электричество: 
        #         показ по блокам в пределах станции, (БелАЭС(ВВЭР-1200 ...), Лукомольская ГРЭС (ПГУ-427 ...))
        #         показ по станциям, (БелАЭС, Минская ТЭЦ-4, Лукомольская ГРЭС и т.д.)
        #         показ по типам станций, (АЭС, блок-станции, малые ТЭЦ, крупные ТЭЦ, КЭС, ВИЭ)
        #         показ по типам турбин а пределах станций (БелАЭС(ВВЭР), Минская ТЭЦ-4(ПТ,Т,Р), Лукомольская ГРЭС(ПГУ,К,ГТУ))
        #         показ по типам турбин а пределах типов станций (АЭС(ВВЭР), ТЭЦ(ПТ,Т,Р), КЭС(ПГУ,К,ГТУ))
                
		# графики гвс: 
        #         показ по блокам в пределах станций, (Минская ТЭЦ-4 (ПТ-60, Т-250, ЭК, КОТ) Минская ТЭЦ-3(...))
        #         показ по станциям, (Минская ТЭЦ-4, Минская ТЭЦ-3, районные котельные, Лукомольская ГРЭС)
        #         по типам станции (ТЭЦ, котельные, КЭС,)
        #         показ по типам источников тепла в пределах станций (Минская ТЭЦ-4(ТЭЦ,ЭК,КОТ))
        #         показ по типам источников тепла ()
                
            
            
        # информация для сортировки для блока
                # мощность блока
                # порядок отображения станции
                # порядок отображения типа станции
                # порядок отображения типа блока в пределах станции и в ее пределов
                # порядок типа источника тепла

                # признак источника электричества
                
                # тип источника тепла
                # тип блока
                # тип станции
                # название станции
                # название блока




	
    
  


  
  

  
    
  
  
  
 