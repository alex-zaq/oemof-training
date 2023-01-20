
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from custom_modules.excel_operations import import_dataframe_to_excel, create_res_scheme, get_excel_reader
from custom_modules.specific_stations import Specific_stations
from custom_modules.generic_blocks import Generic_buses, Generic_sinks, Generic_sources
from custom_modules.helpers import set_natural_gas_price, get_time_slice, find_first_monday, months, get_peak_load_by_energy_2020
from custom_modules.result_proccessing import Custom_result_grouper
from custom_modules.scenario_builder import Scenario_builder

winter_work_day_2020 = dict(
            start_date = find_first_monday(2020, months['февраль'], None),
            end_date = find_first_monday(2020, months['февраль'], None) + dt.timedelta(hours=23)
            )

# summer_work_day_2020 = dict(
#             start_date = find_first_monday(2020, months['июль'], None),
#             end_date = find_first_monday(2020, months['июль'], None) + dt.timedelta(hours=23)
#             )


data_time_options = dict (number_of_time_steps = 24, selected_interval = winter_work_day_2020)



number_of_time_steps = data_time_options['number_of_time_steps']
current_start_date = data_time_options['selected_interval']['start_date']
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= True)

# сделать словарь

excel_reader = get_excel_reader(folder ='./data_excel', file = 'test_data.xlsx' )

data = excel_reader(sheet_name='test_data')

power_rel = data['Power-rel']

minskay_tec_4_hw_abs = data['Минская ТЭЦ-4-гвс']
novopockay_tec_hw_abs = data['Новополоцкая ТЭЦ-гвс']

minskay_tec_4_steam_abs = 0
novopockay_tec_steam_abs = data['Новополоцкая ТЭЦ-пар']

block_station_load_data = data['Блок-станции']

wind_load_data = data['Ветер']
solar_load_data = data['Солнце']
hydro_load_data = data['Вода']


[el_bus, gas_bus] = Generic_buses(es).create_buses('электричество_поток','природный_газ_поток')
custom_es = Specific_stations(es, gas_bus, el_bus)

##################################################################################################
# Настройка сценария
##################################################################################################
scen_builder = Scenario_builder(custom_es)
scen_builder.set_electricity_level(energy_level_in_billion_kWth = 37.3)
scen_builder.set_electricity_profile(elictricity_profile = power_rel)
scen_builder.set_natural_gas_price(usd_per_1000_m3 = 10)
# scen_builder.remove_siemens()
# scen_builder.reduce_block_station_power_to_minimum()
# scen_builder.remove_renewables()
##################################################################################################
##################################################################################################
# Белорусская энергосистема - 2022
##################################################################################################
renewables = custom_es.add_renewables_fixed(wind_load_data, solar_load_data, hydro_load_data)
lukomolskay_gres = custom_es.add_Lukomolskay_gres()
# berezovskay_gres = custom_es.add_Berezovskay_gres()
# minskay_tec_5 = custom_es.add_Minskay_tec_5()

minskay_tec_4 = custom_es.add_Minskay_tec_4(heat_water_demand_data = minskay_tec_4_hw_abs)
novopockay_tec = custom_es.add_Novopockay_tec(heat_water_demand_data = novopockay_tec_hw_abs, steam_demand_data = novopockay_tec_steam_abs)


block_station = custom_es.add_block_staion_natural_gas(fixed_el_load_data_rel = block_station_load_data)
bel_npp = custom_es.add_Bel_npp()
fake_el_source = custom_es.add_electricity_source(10000, usd_per_Mwth = 9999)
##################################################################################################
# Выполнение расчета 
##################################################################################################
model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)
result_processor = Custom_result_grouper(custom_es, results)
##################################################################################################
# Настройка группировки результатов
##################################################################################################
result_processor.set_block_station_plot_1({
    bel_npp: ['ввэр'],
    block_station: ['блок-станции-газ'],
    minskay_tec_4: ['пт','т','эк','кот'],
    novopockay_tec: ['р','пт', 'кот'],
    lukomolskay_gres: ['пгу-кэс','к'],
    renewables: ['виэ-вода','виэ-ветер','виэ-солнце'],
    fake_el_source: ['фейк']
})
##################################################################################################
# result_processor.set_station_plot_3(
#   [ bel_npp,
#     block_station,
#     minskay_tec_4,
#     novopockay_tec,
#     lukomolskay_gres,
#     renewables,
#     fake_el_source
# ])




# result_processor.set_block_station_type_plot_2(
#     {
#     'аэс':[bel_npp],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[lukomolskay_gres],
#     'фейки': [fake_el_source]
# },
#     {
#     'аэс': ['ввэр'],
#     'тэц': ['р','пт','т', 'эк', 'кот'],
#     'кэс': ['пгу-кэс','к'],
#     'фейки': ['фейк'],
# }    
#     )



# result_processor.set_station_type_plot_4(
# {
#     'аэс':[bel_npp],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[lukomolskay_gres],
#     'фейки': [fake_el_source]
# })

# result_processor.set_block_type_station_plot_5(
#  {
#     bel_npp: ['ввэр'],
#     minskay_tec_4: ['пт','т','эк','кот'],
#     novopockay_tec: ['р','пт', 'кот'],
#     lukomolskay_gres: ['пгу-кэс','к'],
#     fake_el_source: ['фейк']
# } )

# result_processor.set_block_type_station_type_plot_6(
# {
#     'аэс':[bel_npp],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[lukomolskay_gres],
#     'фейки': [fake_el_source]
# },

# {
#     'аэс':['ввэр'],
#     'тэц':['р','пт','т','эк','кот'],
#     'кэс':['пгу-кэс','к'],
#     'фейки': ['фейк']
# })


el_df = result_processor.get_dataframe_by_commodity_type('электроэнергия')
hw_df = result_processor.get_dataframe_by_commodity_type('гвс')
steam_df = result_processor.get_dataframe_by_commodity_type('пар')
el_demand_orig = result_processor.get_dataframe_orig_electricity_demand(el_bus, custom_es.gobal_elictricity_sink)



maxY = 7000
ax_el = el_df.plot(kind="area", ylim=(0, maxY), legend = 'reverse', title = 'Производство электричества')
ax_el_demand = el_demand_orig.plot(kind="line", ax = ax_el ,color = 'black', ylim=(0, maxY), style='.-' , legend = 'reverse')
# # .legend(fontsize=7, loc="upper right")
ax_hw = hw_df.plot(kind="area", ylim=(0, maxY),  legend = 'reverse', title = 'Производство гвс' )
ax_steam = steam_df.plot(kind="area", ylim=(0, maxY), legend = 'reverse', title = 'Производство пара' )


plt.show()

# import_dataframe_to_excel(el_df, './results', 'el_test.xlsx')
# import_dataframe_to_excel(hw_df, './results', 'hw_test.xlsx')

#########################################################
# Отображение 1 - по отдельным блокам в пределах станции - ок
#########################################################

 

 

#########################################################
# Отображение 2 - показ по блокам в пределах типа станции - ок
#########################################################
# custom_es.set_station_type_with_order({
#     'аэс':[bel_npp],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[lukomolskay_gres],
#     'фейки': [fake_el_source]
# })

# custom_es.set_block_type_in_station_type({
#     'аэс': ['ввэр'],
#     'тэц': ['р','пт','т', 'эк', 'кот'],
#     'кэс': ['пгу-кэс','к'],
#     'фейки': ['фейк'],
# })


# block_list = custom_es.get_all_blocks()
# print('')
#########################################################
# Отображение 3 - показ по станциям - ок
#########################################################
# нужно объединить в фрейме
# custom_es.set_station_order([
#     bel_npp,
#     minskay_tec_4,
#     novopockay_tec,
#     lukomolskay_gres,
#     fake_el_source
# ])
# block_list = custom_es.get_all_blocks()
#########################################################
# Отображение 4 - показ по типам станций - ок
#########################################################
# добавить приоритет, нужно объединить в фрейме
# custom_es.set_station_type_with_order({
#     'аэс':[bel_npp],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[lukomolskay_gres],
#     'фейки': [fake_el_source]
# })
# block_list = custom_es.get_all_blocks()
#########################################################
# Отображение 5 - по типам блоков в пределах станций - ок
#########################################################
# custom_es.set_station_order([
#     bel_npp,
#     minskay_tec_4,
#     novopockay_tec,
#     lukomolskay_gres,
#     fake_el_source
# ])

# # объединить в фрейме
# custom_es.set_block_type_in_station_order({
#     bel_npp: ['ввэр'],
#     minskay_tec_4: ['пт','т','эк','кот'],
#     novopockay_tec: ['р','пт', 'кот'],
#     lukomolskay_gres: ['пгу-кэс','к'],
#     fake_el_source: ['фейк']
# })
# block_list = custom_es.get_all_blocks()
#########################################################
# Отображение 6 - по типам блоков в пределах типов станций - ок
#########################################################
# custom_es.set_station_type_with_order({
#     'аэс':[bel_npp],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[lukomolskay_gres],
#     'фейки': [fake_el_source]
# })
# # объединить в фрейме
# custom_es.set_block_type_in_station_type({
#     'аэс':['ввэр'],
#     'тэц':['р','пт','т','эк','кот'],
#     'кэс':['пгу-кэс','к'],
#     'фейки': ['фейк']
# })
# block_list = custom_es.get_all_blocks()
#########################################################
 
 
# custom_es.set_station_order(
#     bel_npp,
#     novopockay_tec,
#     minskay_tec_4,
    
    
# )




# турбины для проверки
# к-315
# к-310
# к-300
# ccgt_427
# пт-60
# ПТ-50
# р-50
# т-250
# т-110
# т-255




# 





