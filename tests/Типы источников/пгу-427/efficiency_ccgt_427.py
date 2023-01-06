from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import datetime as dt
sys.path.insert(0, './')
from modules.wrapper_plot import get_dataframe_by_output_bus,get_dataframe_by_input_bus 
from modules.wrapper_excel_operations import import_dataframe_to_excel
from modules.wrapper_excel_operations import create_res_scheme
from drafts.functions_stations import get_factory_method_by_energysystem 
from drafts.wrapper_generic_blocks import (get_buses_method_by_energy_system, get_sinks_method_by_energy_system, get_buses_method_by_energy_system,get_sources_methods_by_energy_system)
from modules.helpers import set_XY_label
from modules.classes_generic_blocks import * 
from modules.classes_specific_blocks import * 


# from modules.wrapper_generic_blocks import get_buses_method_by_energy_system

# ПГУ - 427 
# проверка зависимости КПД от мощности

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)
block_list = []

[bgas_bus, bel_bus] = Generic_buses(es).create_buses('газ','электричество')
gas_source = Generic_sources(es, block_list).create_source('источник газа', bgas_bus, 0)
step = (427-427*0.4)/24
el_sink = Generic_sinks(es).create_sink_absolute_demand('электричество_спрос', bel_bus, [427*0.4 + i*step for i in range(24)])


specific_block_creator = Specific_blocks(es, block_list, bgas_bus, bel_bus)
ccgt_427 = specific_block_creator.get_ccgt_427(1,'тестовая станция', planning_outage = None)
  

model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)


df_el = get_dataframe_by_output_bus(results, block_list, bel_bus)
df_gas = get_dataframe_by_input_bus(results, block_list, bgas_bus)
df_eff = df_el/df_gas

print(df_eff)

fig, axes = plt.subplots(nrows=1, ncols=3)
# (first_pos,second_pos) = (axes[0], axes[1])
(first_pos,second_pos, third_pos) = (axes[0], axes[1], axes[2])


ax1 = df_el.plot(kind="area", ylim=(0, 7000), ax=first_pos , legend = 'reverse', title = 'Производство электричества' )
ax2 = df_gas.plot(kind="area", ylim=(0, 7000), ax=second_pos ,legend = 'reverse', title = 'Потребление газа' )
ax3 = df_eff.plot(kind="line", ylim=(0, 1), ax=third_pos ,legend = 'reverse', title = 'КПД' )

set_XY_label(ax1, 'Время, часы','Мощность, МВт')
set_XY_label(ax2, 'Время, часы','Мощность, МВт')
set_XY_label(ax3, 'Время, часы','КПД')


plt.show()