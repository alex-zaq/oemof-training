
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
#  изменить на конкретные функции
from drafts.wrapper_generic_blocks import *
from modules.wrapper_plot import get_dataframe_by_bus
from modules.wrapper_excel_operations import import_dataframe_to_excel
from modules.wrapper_excel_operations import create_res_scheme
from drafts.functions_stations import get_factory_method_by_energysystem  

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)
block_list = []



# (tec_hw, tec_steam) = (file['sheetname-hw']['tec'], file['sheetname-hw']['tec'])


# src_name = 'data_by_day'
# get_sheet_name_by_work_book = get_reader_by_folder(os.getcwd()+'/data',src_name)
# el_global_data = get_sheet_name_by_work_book('electric_demands_abs')[:number_of_time_steps]

create_source = get_sources_methods_by_energy_system(es, block_list)
get_bus_list_by_name = get_buses_method_by_energy_system(es)
create_sink_abs_demand= get_sinks_method_by_energy_system(es, block_list, 'abs')
create_T_turb = get_chp_method_by_energy_system(es, block_list, 'Т')

[bgas_bus, bel_bus, bth_bus] = get_bus_list_by_name('bgas','bel','bth')
gas_source = create_source("gas_source", bgas_bus, 0 )
el_back_source = create_source("el_back_tr", bel_bus, 999)
heat_back_source = create_source("heat_back_tr", bth_bus, 999)
el_sink = create_sink_abs_demand("el_sink", bel_bus, 900)


create_Novopolockay_tec = get_factory_method_by_energysystem(es, block_list, bgas_bus, bel_bus, 'Новополоцкая ТЭЦ')
create_Minskay_tec_4= get_factory_method_by_energysystem(es, block_list, bgas_bus, bel_bus, 'Минская ТЭЦ-4')


hw_demand = [900 for _ in range(number_of_time_steps)]
steam_demand = [900 for _ in range(number_of_time_steps)]
(heat_tr_dict, heat_bus_dict) = create_Novopolockay_tec('Новополоцкая ТЭЦ', hw_demand, steam_demand, planning_outage = None)
(heat_tr_dict_2, heat_bus_dict_2) = create_Minskay_tec_4('Минская ТЭЦ-4', hw_demand, steam_demand = None, planning_outage = None)
 




model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)

df_el = get_dataframe_by_bus(results, block_list, bel_bus)
df_h = get_dataframe_by_bus(results, heat_tr_dict['ГВС'], heat_bus_dict['ГВС'])
df_h_2 = get_dataframe_by_bus(results, heat_tr_dict_2['ГВС'], heat_bus_dict_2['ГВС'])


df_h_union = pd.concat([df_h, df_h_2], axis=1)

df = df_h_union.sum(axis = 1)

df1 = pd.DataFrame(df, columns=['dfg'])
# df.rename_axis('сумма')
# df.

# print(df_h)
# print(df_h_2)

# print(df_h_union)
# print(df)
# print(df1)


fig, axes = plt.subplots(nrows=1, ncols=3)
(first_pos,second_pos,third_pos) = (axes[0], axes[1], axes[2])

# ax1 = df_el.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство электроэнергии' )
# ax2 = df_h_union.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство тепла' )
# ax3 = df_h_2.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство тепла' )
ax4 = df1.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство тепла' )
plt.show()


# folders_options = (os.getcwd(), 'results', os.path.basename(__file__)[:-3],)
# import_dataframe_to_excel(df_el, folders_options = folders_options, excel_name ='Выработка электроэнергии')
# import_dataframe_to_excel(df_h, folders_options = folders_options, excel_name ='Выработка тепла')
# create_res_scheme(energysystem, folders_options)
