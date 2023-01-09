import sys
sys.path.insert(0, './')
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from custom_modules.excel_operations import import_dataframe_to_excel, create_res_scheme, get_excel_reader
from custom_modules.specific_stations import Specific_stations
from custom_modules.specific_blocks import Specific_blocks
from custom_modules.generic_blocks import Generic_buses, Generic_sinks, Generic_sources
from custom_modules.helpers import set_natural_gas_price, get_time_slice, find_first_monday, months, Custom_counter
from custom_modules.plot import get_dataframe_by_output_bus

# template
##########################################################################################################
# характерные сутки и временное разрешение
##########################################################################################################
winter_work_day_2020 = dict(
            start_date = find_first_monday(2020, months['февраль'], None),
            end_date = find_first_monday(2020, months['февраль'], None) + dt.timedelta(hours=23)
            )
 
data_time_options = dict (number_of_time_steps = 24, selected_interval = winter_work_day_2020)
##########################################################################################################
# Создание исходного объекта энергосистемы
##########################################################################################################
number_of_time_steps = data_time_options['number_of_time_steps']
current_start_date = data_time_options['selected_interval']['start_date']
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)
##########################################################################################################
# Извлечение данных из excel
##########################################################################################################
excel_reader_power = get_excel_reader(folder ='./data_excel', file = 'power_by_year_2020.xlsx' )
# excel_reader_heat = get_excel_reader(folder ='./data_excel', file = 'heat_data_by_year_2020.xlsx' )
power_loads_by_hour_sheet = excel_reader_power('электроэнергия 2020')
# heat_water_loads_by_hour_sheet = excel_reader_heat('гвс 2020')
# steam_loads_by_hour_sheet = excel_reader_heat('пар 2020')
power_selected_info = get_time_slice(power_loads_by_hour_sheet, data_time_options['selected_interval'])[['date','day-type-name','power-rel']]
# hw_selected_info = get_time_slice(heat_water_loads_by_hour_sheet, data_time_options['selected_interval'])[['date','day-type-name', 'Минская ТЭЦ-4', 'Новополоцкая ТЭЦ']]
# steam_selected_info = get_time_slice(steam_loads_by_hour_sheet, data_time_options['selected_interval'])[['date','day-type-name', 'Минская ТЭЦ-4', 'Новополоцкая ТЭЦ']]
power_loads = power_selected_info['power-rel'].tolist()
# hw_minskay_tec_4 = hw_selected_info['Минская ТЭЦ-4']
# hw_novopolockay_tec, steam_novopolockay_tec = hw_selected_info['Новополоцкая ТЭЦ'], steam_selected_info['Новополоцкая ТЭЦ']
##########################################################################################################
[el_bus, gas_bus] = Generic_buses(es).create_buses('электричество_поток','природный_газ_поток')
gas_source = Generic_sources(es).create_source('природный_газ_источник', gas_bus, 100)
# print(power_loads)
el_sink = Generic_sinks(es).create_sink_fraction_demand('электричество_потребитель', el_bus, demand_profile=power_loads, peak_load=800)

# block_collection = []
counter = Custom_counter()
station_name = 'Тестовая станция'
block_creator = Specific_blocks(es, gas_bus, el_bus, [])

block_creator.get_k_300(counter.next(), station_name)
block_creator.get_k_310(counter.next(), station_name)
block_creator.get_k_315(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)
# block_creator.get_k_300(counter.next(), station_name)


block_collection = block_creator.get_block_collection()


model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)


df_el = get_dataframe_by_output_bus(results, block_collection, el_bus)


ax_el = df_el.plot(kind="area", ylim=(0, 1000) , legend = 'reverse', title = 'Производство электричества' )


plt.show()

# турбины для проверки

# пт-60
# ПТ-50
# р-50
# т-250
# т-110
# т-255
