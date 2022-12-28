
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.custom_blocks import *

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)

[create_back_Trasformer, get_bus_list_by_name, create_sink_absolute_demand, create_back_Trasformer ] = get_blocks_method_by_energy_system(energysystem)
[bgas_bus,bel_bus,bth_bus] = get_bus_list_by_name('bgas','bel','bth')

el_back_tr = create_back_Trasformer("el_back_tr",bgas_bus,bel_bus, 99999)
heat_back_tr = create_back_Trasformer("heat_back_tr",bgas_bus, bth_bus, 99999)


el_sink = create_sink_absolute_demand("el_sink", bel_bus, [900 for _ in range(24)] )
th_sink = create_sink_absolute_demand("th_sink", bth_bus, [1500 for _ in range(24)])


model = solph.Model(energysystem)
model.solve(solver="cplex")
results = solph.processing.results(model)

