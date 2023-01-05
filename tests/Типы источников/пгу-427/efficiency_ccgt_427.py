from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import datetime as dt
sys.path.insert(0, './')
from modules.wrapper_plot import get_dataframe_by_bus
from modules.wrapper_excel_operations import import_dataframe_to_excel
from modules.wrapper_excel_operations import create_res_scheme
from modules.stations import get_factory_method_by_energysystem 
from modules.wrapper_generic_blocks import (get_buses_method_by_energy_system, get_sinks_method_by_energy_system, get_buses_method_by_energy_system,get_sources_methods_by_energy_system)

# from modules.wrapper_generic_blocks import get_buses_method_by_energy_system

# ПГУ - 427 
# проверка зависимости КПД от мощности

number_of_time_steps = 10
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
es = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)
block_list = []

create_buses = get_buses_method_by_energy_system(es)
create_source = get_sources_methods_by_energy_system(es, block_list)

[bgas_bus, bel_bus, bth_bus] = create_buses('bgas','bel','bth')
gas_source = create_source("gas_source", bgas_bus, 0 )


[get_ccgt_427, get_dummy_flow] = get_factory_method_by_energysystem(es,block_list,bgas_bus,bel_bus, ['пгу-427', 'источник'])
ccgt_427 = get_ccgt_427('тестовая станция', None)
el_dummy_flow = get_dummy_flow(bel_bus, variable_costs = 9999)


create_sink_abs_demand = get_sinks_method_by_energy_system(es, block_list, 'abs')
el_sink = create_sink_abs_demand("el_sink", bel_bus, 900)


model = solph.Model(es)
model.solve(solver="cplex")
results = solph.processing.results(model)


df_el = get_dataframe_by_bus(results, block_list, bel_bus)

ax1 = df_el.plot(kind="area", ylim=(0, 7000), legend = 'reverse', title = 'Производство электричества' )
plt.show()