
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.custom_blocks import *
from modules.custom_plot import *
from modules.custom_excel_operations import *

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)
nodes_collection = []

src_name = 'data_by_day'
get_sheet_name_by_work_book = get_reader_by_folder(os.getcwd()+'/data',src_name)
el_global_data = get_sheet_name_by_work_book('electric_demands_abs')[:number_of_time_steps]




[create_source] = get_sources_methods_by_energy_system(energysystem, nodes_collection)
[create_sink_absolute_demand, _] = get_sinks_method_by_energy_system(energysystem, nodes_collection)
[get_bus_list_by_name] = get_buses_method_by_energy_system(energysystem)
 


[bgas_bus, bel_bus, bth_bus] = get_bus_list_by_name('bgas','bel','bth')
gas_source = create_source("gas_source",bgas_bus, 0 )
el_back_source = create_source("el_back_tr", bel_bus, 999)
heat_back_source = create_source("heat_back_tr", bth_bus, 999)



el_sink = create_sink_absolute_demand("el_sink", bel_bus, 900 )
th_sink = create_sink_absolute_demand("th_sink", bth_bus, 500)


model = solph.Model(energysystem)
model.solve(solver="cplex")
results = solph.processing.results(model)

df_el = get_dataframe_by_commodity(results, nodes_collection, bel_bus)
df_h = get_dataframe_by_commodity(results, nodes_collection, bth_bus)

# ax1 = df_el.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство электроэнергии' )
# ax2 = df_h.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство тепла' )
# plt.show()




folders_options = (os.getcwd(), 'results', os.path.basename(__file__)[:-3],)
import_dataframe_to_excel(df_el, folders_options = folders_options, excel_name ='Выработка электроэнергии')
# import_dataframe_to_excel(df_h, folders_options = folders_options, excel_name ='Выработка тепла')
# create_res_scheme(energysystem, folders_options)
