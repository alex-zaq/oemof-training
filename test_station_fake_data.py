
import logging
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from custom_modules.excel_operations import import_dataframe_to_excel, create_res_scheme, get_excel_reader, transform_dataframe_to_sql_style
from custom_modules.specific_stations import Specific_stations
from custom_modules.generic_blocks import Generic_buses, Generic_sinks, Generic_sources
from custom_modules.helpers import set_natural_gas_price, get_time_slice, find_first_monday, months, get_peak_load_by_energy_2020, rename_station
from custom_modules.result_proccessing import Custom_result_grouper, Custom_result_extractor
from custom_modules.scenario_builder import Scenario_builder

 
 
month = 'февраль'
day_of_week = 'рабочий'
year = 2022 




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


odu_power_febrary = input_data['Февраль']

main_power_profile_rel = input_data['Power-rel-2']

fixed_load_rel = {
    'ВЭС':  input_data['Ветер'].tolist(),
    'СЭС':  input_data['Солнце'].tolist(),
    'ГЭС':  input_data['Вода'].tolist(),
    'Малые ТЭЦ': input_data['Малые ТЭЦ-гвс'].tolist(),
    'Блок-станции': input_data['Блок-станции-1'].tolist()
}

heat_water_demand_abs = {
    'Минская ТЭЦ-4': input_data['Минская ТЭЦ-4-гвс'].tolist(),
    'Минская ТЭЦ-3': input_data['Минская ТЭЦ-3-гвс'].tolist(),
    'Новополоцкая ТЭЦ': input_data['Новополоцкая ТЭЦ-гвс'].tolist(),
    'Светлогорская ТЭЦ': input_data['Светлогорская ТЭЦ-гвс'].tolist(),
    'Могилевская ТЭЦ-2': input_data['Могилевская ТЭЦ-2-гвс'].tolist(),
    'Бобруйская ТЭЦ-2': input_data['Бобруйская ТЭЦ-2-гвс'].tolist(),
    'Гродненская ТЭЦ-2': input_data['Гродненская ТЭЦ-2-гвс'].tolist(),
    'Мозырская ТЭЦ-2': input_data['Мозырская ТЭЦ-2-гвс'].tolist(),
    'Гомельская ТЭЦ-2': input_data['Гомельская ТЭЦ-2-гвс'].tolist(),
    'Котельные Белэнерго': input_data['РК-Белэнерго-гвс'].tolist(),
    'Котельные ЖКХ': input_data['РК-ЖКХ-гвс'].tolist(),
}

heat_steam_demand_abs = {
    'Новополоцкая ТЭЦ': input_data['Новополоцкая ТЭЦ-пар'].tolist(),
    'Минская ТЭЦ-3': input_data['Минская ТЭЦ-3-пар'].tolist(),
    'Светлогорская ТЭЦ': input_data['Светлогорская ТЭЦ-пар'].tolist(),
    'Могилевская ТЭЦ-2': input_data['Могилевская ТЭЦ-2-пар'].tolist(),
    'Бобруйская ТЭЦ-2': input_data['Бобруйская ТЭЦ-2-пар'].tolist(),
    'Гродненская ТЭЦ-2': input_data['Гродненская ТЭЦ-2-пар'].tolist(),
    'Мозырская ТЭЦ-2': input_data['Мозырская ТЭЦ-2-пар'].tolist(),
    # 'Гомельская ТЭЦ-2': input_data['Гомельская ТЭЦ-2-пар'].tolist(),
    'Котельные Белэнерго': input_data['РК-Белэнерго-пар'].tolist(),
}


el_boilers_hw_groups = {
    'электрокотлы Белэнерго' : 'электрокотлы Белэнерго'
}


[el_bus, gas_bus] = Generic_buses(es).create_buses('электричество_поток','природный_газ_поток')
custom_es = Specific_stations(es, gas_bus, el_bus)

shout_down_lst = 10 * [0] + 14 * [999999]
custom_es.set_start_up_options(initial_status = 1, shout_down_cost = shout_down_lst ,
                start_up_cost= 10e8, maximum_shutdowns = 1, maximum_startups = 100 )

##################################################################################################
# Настройка сценария
##################################################################################################
scen_builder = Scenario_builder(custom_es)
# scen_builder.disable_all_exist_turb_by_station_name('Лукомольская ГРЭС', 'Березовская ГРЭС', 'Минская ТЭЦ-5')
scen_builder.add_constraint_for_el_boiler_group(el_boilers_hw_groups['электрокотлы Белэнерго'], 916)
# scen_builder.set_electricity_profile(elictricity_profile = main_power_profile_rel)
# scen_builder.set_electricity_level(energy_level_in_billion_kWth = 39)
scen_builder.set_electricity_demand_abs(odu_power_febrary)
scen_builder.set_turbine_T_modelling_type('detail')
scen_builder.set_natural_gas_price(usd_per_1000_m3 = 10)
scen_builder.set_bel_npp_vver_1200_first_options(active_status = 1, min_power_fraction=0.75, fix_load=False)
scen_builder.set_bel_npp_vver_1200_second_options(active_status = 1, min_power_fraction=0.75, fix_load=False)
scen_builder.add_inifinity_el_boilers_hw_for_all_large_chp()
# scen_builder.disable_all_exist_turb_by_station_name('Березовская ГРЭС', 'Минская ТЭЦ-5')
# scen_builder.enable_gas_boiler_hw().add_inifinity_gas_boilers_hw_for_all_large_chp().set_gas_boilers_hw_variable_cost(99999)


scen_builder.enable_gas_boiler_hw_by_station_name('Котельные Белэнерго')
scen_builder.enable_gas_boiler_steam_by_station_name('Котельные Белэнерго')
scen_builder.enable_gas_boiler_hw_by_station_name('Котельные ЖКХ')
# scen_builder.add_inifinity_el_boilers_hw_by_station('Минская ТЭЦ-4')
scen_builder.disable_el_boiler_steam()
# scen_builder.remove_renewables()
# scen_builder.add_ocgt_100(1)
# scen_builder.add_vver_toi_1255(1, -999)
# scen_builder.add_vver_600(0.6, -999)
# scen_builder.reduce_small_chp_demand_by_part(0)
# scen_builder.add_inifinity_el_boilers_hw_by_station('Малые ТЭЦ').set_el_boilers_hw_var_cost_by_station('Малые ТЭЦ', 2)
# scen_builder.set_bel_npp_vver_1200_first_options(active_status=0, min_power_fraction=0.75, usd_per_Mwth= -999)


# scen_builder.add_inifinity_el_boilers_hw_small_chp()
# scen_builder.add_inifinity_gas_boilers_hw_small_chp()
# scen_builder.reduce_block_station_power_to_minimum()
# scen_builder.remove_siemens()
# добавить фиксированный вариант работы аэс
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


svetlogorskay_tec = custom_es.add_Svetlogorskay_tec(heat_water_demand_data = heat_water_demand_abs['Светлогорская ТЭЦ'], 
                                              steam_demand_data = heat_steam_demand_abs['Светлогорская ТЭЦ'])

mogilevskya_tec_2 = custom_es.add_Mogilevskay_tec_2(heat_water_demand_data = heat_water_demand_abs['Могилевская ТЭЦ-2'], 
                                              steam_demand_data = heat_steam_demand_abs['Могилевская ТЭЦ-2']) 


bobryskay_tec_2 = custom_es.add_Bobryskay_tec_2(heat_water_demand_data = heat_water_demand_abs['Бобруйская ТЭЦ-2'], 
                                               steam_demand_data = heat_steam_demand_abs['Бобруйская ТЭЦ-2'])

grodnenskay_tec_2 = custom_es.add_Grodnenskay_tec_2(heat_water_demand_data = heat_water_demand_abs['Гродненская ТЭЦ-2'], 
                                               steam_demand_data = heat_steam_demand_abs['Гродненская ТЭЦ-2'])


minskay_tec_3 = custom_es.add_Minskay_tec_3(heat_water_demand_data = heat_water_demand_abs['Минская ТЭЦ-3'],
                                            steam_demand_data = heat_steam_demand_abs['Минская ТЭЦ-3'])


mozyrskay_tec_2 = custom_es.add_Mozyrskay_tec_2(heat_water_demand_data = heat_water_demand_abs['Мозырская ТЭЦ-2'],
                                               steam_demand_data = heat_steam_demand_abs['Мозырская ТЭЦ-2'])

gomelskay_tec_2 = custom_es.add_Gomelskay_tec_2(heat_water_demand_data = heat_water_demand_abs['Гомельская ТЭЦ-2'])


small_tec = custom_es.add_small_chp(fixed_el_load_data_rel= fixed_load_rel['Малые ТЭЦ'])
block_station = custom_es.add_block_station_natural_gas(fixed_el_load_data_rel = fixed_load_rel['Блок-станции'])
bel_npp = custom_es.add_Bel_npp()

district_boilers_Belenergo = custom_es.add_district_boilers_Belenergo(heat_water_demand_data = heat_water_demand_abs['Котельные Белэнерго'],
                                                                    steam_demand_data = heat_steam_demand_abs['Котельные Белэнерго'])

# district_boilers = custom_es.add_district_boilers(heat_water_demand_data = heat_water_demand_abs['Котельные ЖКХ'])

# new_npp = custom_es.add_new_npp()
# new_ocgt = custom_es.add_new_ocgt()
# fake_el_source = custom_es.add_electricity_source(nominal_value = 10000, usd_per_Mwth = -9999)

el_boilers_hw = custom_es.get_install_el_boilers_hw_power()
custom_es.print_el_boilers_hw_by_station()

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
#     # new_npp: ['ввэр'],
#     block_station: ['блок-станции-газ'],
#     small_tec: ['малые тэц', 'эк', 'кот'],

#     novopockay_tec: ['р','пт', 'эк' ,'кот'],
#     minskay_tec_3: ['пт','т', 'пгу-тэц' ,'эк', 'кот'],
#     svetlogorskay_tec: ['р','пт', 'т', 'эк', 'кот'],
#     mogilevskya_tec_2: ['р', 'пт', 'гту', 'эк', 'кот'],
#     bobryskay_tec_2: ['пт','гту','эк','кот'],
#     mozyrskay_tec_2: ['пт','эк','кот'],
#     grodnenskay_tec_2: ['р','пт','гту-тэц','эк', 'кот'],
#     gomelskay_tec_2: ['т','эк','кот'],
#     minskay_tec_4: ['пт','т','эк', 'кот'],

#     lukomolskay_gres: ['пгу-кэс','к','эк', 'кот'],
#     berezovskay_gres: ['пгу-кэс','к', 'гту','эк', 'кот'],
#     minskay_tec_5: ['пгу-кэс', 'к'],
#     # new_ocgt: ['гту'],
#     renewables: ['виэ-вода','виэ-ветер','виэ-солнце'],
#     district_boilers_Belenergo: ['эк', 'кот'],
#     # district_boilers: ['эк','кот']
# })

##################################################################################################
# result_plotter.set_station_plot_3(
#   [ bel_npp,
#     block_station,
#     small_tec,

#     novopockay_tec,
#     minskay_tec_3,
#     svetlogorskay_tec,
#     mogilevskya_tec_2,
#     bobryskay_tec_2,
#     mozyrskay_tec_2,
#     grodnenskay_tec_2,
#     gomelskay_tec_2,
#     minskay_tec_4,

#     lukomolskay_gres,
#     berezovskay_gres,
#     minskay_tec_5,

#     renewables,
#     district_boilers_Belenergo,
#     # district_boilers,
#     # fake_el_source
# ])
##################################################################################################


result_plotter.set_station_type_plot_4(
{
    'аэс':[bel_npp],
    'блок-станции': [block_station],
    'тэц': [small_tec, 
            novopockay_tec,
            minskay_tec_3,
            svetlogorskay_tec,
            mogilevskya_tec_2,
            bobryskay_tec_2,
            mozyrskay_tec_2,
            grodnenskay_tec_2,
            gomelskay_tec_2,
            minskay_tec_4],
    
    'кэс':[minskay_tec_5, lukomolskay_gres, berezovskay_gres],
    'виэ': [renewables],
    'котельные Белэнерго': [district_boilers_Belenergo]
    # 'фейки': [fake_el_source]
})
##################################################################################################

result_plotter.set_block_type_station_type_plot_6(
{
    'аэс':[bel_npp],
    'блок-станции': [block_station],
    'тэц': [small_tec, 
            novopockay_tec,
            minskay_tec_3,
            svetlogorskay_tec,
            mogilevskya_tec_2,
            bobryskay_tec_2,
            mozyrskay_tec_2,
            grodnenskay_tec_2,
            gomelskay_tec_2,
            minskay_tec_4],
    
    'кэс':[minskay_tec_5, lukomolskay_gres, berezovskay_gres],
    'виэ': [renewables],
    'котельные Белэнерго': [district_boilers_Belenergo]
},

{
    'аэс':['ввэр'],
    'блок-станции': ['блок-станции-газ'],
    'тэц':['малые тэц','пгу-тэц','гту-тэц','р','пт','т','гту','эк','кот'],
    'кэс':['пгу-кэс','к', 'гту', 'эк'],
    'виэ': ['виэ-вода','виэ-ветер','виэ-солнце'],
    'котельные Белэнерго': ['эк','кот']
})


##################################################################################################



##################################################################################################


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






online_power_df = result_extractor.get_dataframe_online_power()

el_df = result_plotter.get_dataframe_by_commodity_type('электроэнергия')
# print(el_df['Минская ТЭЦ-4'])
hw_df = result_plotter.get_dataframe_by_commodity_type('гвс')
# steam_df = result_plotter.get_dataframe_by_commodity_type('пар')
el_demand_orig = result_plotter.get_dataframe_orig_electricity_demand(el_bus, custom_es.gobal_elictricity_sink)

scale = 'млн'
gas_volume = result_extractor.get_total_gas_consumption_value_m3(scale='млн')
gas_consumption ='газ: ' + str(gas_volume) + ' '+ scale +' м3' 
gas_consumption = ' ('+ gas_consumption +')'
print(gas_consumption)

maxY = 9000
ax_el = el_df.plot(kind="area", ylim=(0, maxY), legend = 'reverse', title = 'Производство электричества' + gas_consumption)
ax_el_demand = el_demand_orig.plot(kind="line", ax = ax_el ,color = 'black', ylim=(0, maxY), style='.-' , legend = 'reverse')
ax_online_power = online_power_df.plot(kind="line", ax = ax_el ,color = 'red', ylim=(0, maxY), style='.-' , legend = 'reverse')
# # .legend(fontsize=7, loc="upper right")
ax_hw = hw_df.plot(kind="area", ylim=(0, maxY),  legend = 'reverse', title = 'Производство гвс' )
# ax_steam = steam_df.plot(kind="area", ylim=(0, maxY), legend = 'reverse', title = 'Производство пара' )
 
#  столбец месяца и года станции типов турбин названий станций типов станций, тип энергии
#  переименовать станции
#  добавить столбец - ячейку потребления газа
#  добавить столбец исходного электрического спроса
#  электрокотлы малых тэц
#  расход газ для блок-станций
#  подкорректировать включенную мощность
#  добавить областные ограничения эк
#  разрешить одновременную работу газ кот и эк
# + столбец пар и гвс
# (сделано)  добавить обязательную работу для аэс
#  сделать excel файл 2023 в двумя блоками
# сделать расчеты для каждой комбинации и перенести в общий excel файл



 
# logging.info(f"{year}-{month}-{day_of_week}-газ: {gas_consumption}") 

# create_res_scheme(custom_es.es, './results/1.png')

# logging.info("")

# logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")
# logging.info("An INFO")
# logging.debug("A DEBUG Message")
# logging.warning("A WARNING")
# logging.error("An ERROR")
# logging.critical("A message of CRITICAL severity")


plt.show()


# df_el = rename_station({
    
# }, df_el)

# df_el_sql_like = transform_dataframe_to_sql_style(el_df)


# import_dataframe_to_excel(el_df, './results/', 'res.xlsx')


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




# 





