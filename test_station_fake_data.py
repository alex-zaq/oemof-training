
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
from custom_modules.result_proccessing import Custom_result_grouper, Custom_result_extractor
from custom_modules.scenario_builder import Scenario_builder


# ++++1. Сделать эксель котельные ЖКХ
# ++++2. Сделать эксель малые ТЭЦ
# ++++3. Добавить очередь загрузки для одинаковых блоков
# 4. Добавить 2 КЭС
# 5. Добавить 2 ТЭЦ
# 6. Добавить 2 ТЭЦ
# 7. Добавить 2 ТЭЦ
# 8. Добавить 2 ТЭЦ
# +++++9. Добавить малые ТЭЦ
# 10. Сделать словарь для входных данных эксель
# ++++11. Увеличить стоимость вкл и выкл
# ++++12. Фрейм включенной мощности
# 13. Словарь электрических и тепловых нагрузок из эксель
# 14. перенести профили диспечеров в эксель
# 15. Добавить номера блоков и очередей



winter_work_day_2023 = dict(
            start_date = find_first_monday(2023, months['февраль'], None),
            end_date = find_first_monday(2023, months['февраль'], None) + dt.timedelta(hours=23)
            )

data_time_options = dict (number_of_time_steps = 24, selected_interval = winter_work_day_2023)


number_of_time_steps = data_time_options['number_of_time_steps']
current_start_date = data_time_options['selected_interval']['start_date']
date_time_index = pd.date_range(current_start_date, periods = number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex = date_time_index, infer_last_interval= True)
excel_reader = get_excel_reader(folder ='./data_excel', file = 'test_data.xlsx' )
input_data = excel_reader(sheet_name='test_data')



main_power_profile_rel = input_data['Power-rel-2']

fixed_load_rel = {
    'ВЭС':  input_data['Ветер'],
    'СЭС':  input_data['Солнце'],
    'ГЭС':  input_data['Вода'],
    'Малые ТЭЦ': input_data['Малые ТЭЦ'],
    'Блок-станции': input_data['Блок-станции']
}

heat_water_demand_abs = {
    'Минская ТЭЦ-4': input_data['Минская ТЭЦ-4-гвс'],
    'Новополоцкая ТЭЦ': input_data['Новополоцкая ТЭЦ-гвс']
}

heat_steam_demand_abs = {
    'Новополоцкая ТЭЦ': input_data['Новополоцкая ТЭЦ-пар']
}


[el_bus, gas_bus] = Generic_buses(es).create_buses('электричество_поток','природный_газ_поток')
custom_es = Specific_stations(es, gas_bus, el_bus)
shout_down_lst = 10 * [0] + 14 * [999999]
custom_es.set_start_up_options(initial_status = 1, shout_down_cost = shout_down_lst ,
                start_up_cost= 9999999, maximum_shutdowns=1, maximum_startups = 100 )
##################################################################################################
# Настройка сценария
##################################################################################################
scen_builder = Scenario_builder(custom_es)
scen_builder.set_electricity_profile(elictricity_profile = main_power_profile_rel)
scen_builder.set_electricity_level(energy_level_in_billion_kWth = 39)
scen_builder.set_turbine_T_modelling_type('simple')
scen_builder.set_natural_gas_price(usd_per_1000_m3 = 10)
# scen_builder.remove_siemens()
# добавить фиксированный вариант работы аэс
# scen_builder.reduce_block_station_power_to_minimum()
# scen_builder.remove_renewables()
##################################################################################################
##################################################################################################
# Белорусская энергосистема - 2022
##################################################################################################
renewables = custom_es.add_renewables_fixed(fixed_load_rel['ВЭС'], fixed_load_rel['СЭС'], fixed_load_rel['ГЭС'])
lukomolskay_gres = custom_es.add_Lukomolskay_gres()
berezovskay_gres = custom_es.add_Berezovskay_gres()
minskay_tec_5 = custom_es.add_Minskay_tec_5()


minskay_tec_4 = custom_es.add_Minskay_tec_4(heat_water_demand_data = heat_water_demand_abs['Минская ТЭЦ-4'])
novopockay_tec = custom_es.add_Novopockay_tec(heat_water_demand_data = heat_water_demand_abs['Новополоцкая ТЭЦ'], 
                                              steam_demand_data = heat_steam_demand_abs['Новополоцкая ТЭЦ'])

small_tec = custom_es.add_small_chp(fixed_el_load_data_rel= fixed_load_rel['Малые ТЭЦ'])
block_station = custom_es.add_block_staion_natural_gas(fixed_el_load_data_rel = fixed_load_rel['Блок-станции'])
bel_npp = custom_es.add_Bel_npp()
# fake_el_source = custom_es.add_electricity_source(nominal_value = 10000, usd_per_Mwth = -9999)
##################################################################################################
# Выполнение расчета 
##################################################################################################
model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)
result_plotter = Custom_result_grouper(custom_es, results)
result_extractor = Custom_result_extractor(custom_es, results)
##################################################################################################
# Настройка группировки результатов
##################################################################################################

el_boilers_power = result_extractor.get_install_el_boilers_power('гвс')
print('Мощность электрокотлов-гвс: ', el_boilers_power)


# result_plotter.set_block_station_plot_1({
#     bel_npp: ['ввэр'],
#     block_station: ['блок-станции-газ'],
#     small_tec: ['малые тэц', 'эк', 'кот'],
#     minskay_tec_4: ['пт','т','эк','кот'],
#     novopockay_tec: ['р','пт', 'кот'],
#     minskay_tec_5: ['пгу-кэс', 'к'],
#     lukomolskay_gres: ['пгу-кэс','к'],
#     berezovskay_gres: ['пгу-кэс','к', 'гту'],
#     renewables: ['виэ-вода','виэ-ветер','виэ-солнце'],
# })

##################################################################################################
result_plotter.set_station_plot_3(
  [ bel_npp,
    block_station,
    small_tec,
    minskay_tec_4,
    novopockay_tec,
    minskay_tec_5,
    lukomolskay_gres,
    berezovskay_gres,
    renewables,
    # fake_el_source
])
##################################################################################################

# result_plotter.set_block_type_station_plot_5(
#  {
#     bel_npp: ['ввэр'],
#     block_station: ['блок-станции-газ'],
#     small_tec: ['малые тэц', 'эк', 'кот'],
#     minskay_tec_4: ['пт','т','эк','кот'],
#     novopockay_tec: ['р','пт', 'кот'],
#     minskay_tec_5: ['пгу-кэс', 'к'],
#     lukomolskay_gres: ['пгу-кэс','к'],
#     berezovskay_gres: ['пгу-кэс','к', 'гту'],
#     renewables: ['виэ-вода','виэ-ветер','виэ-солнце'],
# } )


##################################################################################################


# result_plotter.set_station_type_plot_4(
# {
#     'аэс':[bel_npp],
#     'блок-станции': [block_station],
#     'малые тэц': [small_tec],
#     'тэц':[minskay_tec_4, novopockay_tec],
#     'кэс':[minskay_tec_5, lukomolskay_gres, berezovskay_gres],
#     'виэ': [renewables]
#     # 'фейки': [fake_el_source]
# })


##################################################################################################

# input_data = custom_es.get_all_blocks()

# gas_consumption = result_extractor.get_total_gas_consumption_value_m3(scale = 'млн')
# print('потребление газа: ', gas_consumption , 'млн. м3')

# # online_power_tec_4 = result_extractor.get_dataframe_online_power_by_station('Минская ТЭЦ-4')

# print('')

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

online_power_df = result_extractor.get_dataframe_online_power()

el_df = result_plotter.get_dataframe_by_commodity_type('электроэнергия')
# print(el_df['Минская ТЭЦ-4'])
hw_df = result_plotter.get_dataframe_by_commodity_type('гвс')
# steam_df = result_plotter.get_dataframe_by_commodity_type('пар')
el_demand_orig = result_plotter.get_dataframe_orig_electricity_demand(el_bus, custom_es.gobal_elictricity_sink)




maxY = 9000
ax_el = el_df.plot(kind="area", ylim=(0, maxY), legend = 'reverse', title = 'Производство электричества')
ax_el_demand = el_demand_orig.plot(kind="line", ax = ax_el ,color = 'black', ylim=(0, maxY), style='.-' , legend = 'reverse')
ax_online_power = online_power_df.plot(kind="line", ax = ax_el ,color = 'red', ylim=(0, maxY), style='.-' , legend = 'reverse')
# # .legend(fontsize=7, loc="upper right")
ax_hw = hw_df.plot(kind="area", ylim=(0, maxY),  legend = 'reverse', title = 'Производство гвс' )
# ax_steam = steam_df.plot(kind="area", ylim=(0, maxY), legend = 'reverse', title = 'Производство пара' )


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





