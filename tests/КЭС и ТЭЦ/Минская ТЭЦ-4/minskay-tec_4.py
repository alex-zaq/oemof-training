from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import datetime as dt
sys.path.insert(0, './')
from modules.plot import get_dataframe_by_output_bus,get_dataframe_by_input_bus 
from modules.excel_operations import import_dataframe_to_excel
from modules.excel_operations import create_res_scheme
from drafts.functions_stations import get_factory_method_by_energysystem 
from drafts.wrapper_generic_blocks import (get_buses_method_by_energy_system, get_sinks_method_by_energy_system, get_buses_method_by_energy_system,get_sources_methods_by_energy_system)
from modules.helpers import set_XY_label
from modules.stations import Stations_getter, Generic_sinks
from modules.generic_blocks import Generic_buses



# from modules.wrapper_generic_blocks import get_buses_method_by_energy_system

# ПГУ - 427 
# проверка зависимости КПД от мощности

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)

[bgas, bel, bhw] = Generic_buses(es).create_buses('газ','электричество','горячая вода')
stations_getter = Stations_creator(es, bgas, bel)
electricity_data = [900 for _ in range(number_of_time_steps)]
sink_creator = Generic_sinks(es).create_sink_absolute_demand('эл', bel, electricity_data)


heat_water_demand = [900 for _ in range(number_of_time_steps)]
minskay_tec_4  = stations_getter.create_Minskay_tec_4(heat_water_demand, None, None)


# model = solph.Model(es)
# model.solve(solver="cplex")
# results = solph.processing.results(model)




# create_buses = get_buses_method_by_energy_system(es)
# create_source = get_sources_methods_by_energy_system(es, block_list)

# [bgas_bus, bel_bus, bth_bus] = create_buses('bgas','bel','bth')
# gas_source = create_source("gas_source", bgas_bus, 0 )


# [get_ccgt_427, get_dummy_flow] = get_factory_method_by_energysystem(es,block_list,bgas_bus,bel_bus, ['пгу-427', 'источник'])
# ccgt_427 = get_ccgt_427('тестовая станция', None)
# # el_dummy_flow = get_dummy_flow(bel_bus, variable_costs = 9999)


# create_sink_abs_demand = get_sinks_method_by_energy_system(es, block_list, 'abs')
# step = (427-427*0.4)/24
# el_sink = create_sink_abs_demand("el_sink", bel_bus, [427*0.4 + i*step for i in range(24)])




# df_el = get_dataframe_by_output_bus(results, block_list, bel_bus)
# df_gas = get_dataframe_by_input_bus(results, block_list, bgas_bus)
# df_eff = df_el/df_gas

# print(df_eff)

# fig, axes = plt.subplots(nrows=1, ncols=3)
# # (first_pos,second_pos) = (axes[0], axes[1])
# (first_pos,second_pos, third_pos) = (axes[0], axes[1], axes[2])


# ax1 = df_el.plot(kind="area", ylim=(0, 7000), ax=first_pos , legend = 'reverse', title = 'Производство электричества' )
# ax2 = df_gas.plot(kind="area", ylim=(0, 7000), ax=second_pos ,legend = 'reverse', title = 'Потребление газа' )
# ax3 = df_eff.plot(kind="line", ylim=(0, 1), ax=third_pos ,legend = 'reverse', title = 'КПД' )

# set_XY_label(ax1, 'Время, часы','Мощность, МВт')
# set_XY_label(ax2, 'Время, часы','Мощность, МВт')
# set_XY_label(ax3, 'Время, часы','КПД')


# plt.show()