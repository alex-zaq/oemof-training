
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
#  изменить на конкретные функции
from modules.wrapper_generic_blocks import *
from modules.wrapper_plot import *
from modules.wrapper_excel_operations import * 
from modules.stations import get_station_method_by_energysystem  

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)
block_list = []

# src_name = 'data_by_day'
# get_sheet_name_by_work_book = get_reader_by_folder(os.getcwd()+'/data',src_name)
# el_global_data = get_sheet_name_by_work_book('electric_demands_abs')[:number_of_time_steps]

create_source = get_sources_methods_by_energy_system(es, block_list)
get_bus_list_by_name = get_buses_method_by_energy_system(es)
create_sink_abs_demand= get_sinks_method_by_energy_system(es, block_list, 'абс')
create_T_turb = get_chp_method_by_energy_system(es, block_list, 'Т')

[bgas_bus, bel_bus, bth_bus] = get_bus_list_by_name('bgas','bel','bth')
gas_source = create_source("gas_source",bgas_bus, 0 )
el_back_source = create_source("el_back_tr", bel_bus, 999)
heat_back_source = create_source("heat_back_tr", bth_bus, 999)


el_sink = create_sink_abs_demand("el_sink", bel_bus, 900)
th_sink = create_sink_abs_demand("th_sink", bth_bus, 500)
# [tr_dict, heat_dict]
create_test_station = get_station_method_by_energysystem(es, block_list, bgas_bus, bel_bus, 'Тестовая станция')

[tr_dict, heat_dict] = create_test_station([900 for _ in range(number_of_time_steps)], None, None) 





model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)

df_el = get_dataframe_by_commodity(results, block_list, bel_bus)
df_h = get_dataframe_by_commodity(results, block_list, bth_bus)




ax1 = df_el.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство электроэнергии' )
ax2 = df_h.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство тепла' )
plt.show()


# folders_options = (os.getcwd(), 'results', os.path.basename(__file__)[:-3],)
# import_dataframe_to_excel(df_el, folders_options = folders_options, excel_name ='Выработка электроэнергии')
# import_dataframe_to_excel(df_h, folders_options = folders_options, excel_name ='Выработка тепла')
# create_res_scheme(energysystem, folders_options)
