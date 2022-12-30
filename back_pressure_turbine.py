
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.wrapper_generic_blocks import *

 


number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)


data_folder = os.getcwd()+'/data'
el_global_abs_profile = pd.read_excel(os.path.join(data_folder,'data_by_day.xlsx'), sheet_name='electric_demand_2021_odu')['el_winter_workDay_odu'][:number_of_time_steps]
steam_demand_data = [70] * 24;


[create_back_Trasformer, get_bus_list_by_name] = get_blocks_method_by_energy_system(energysystem)
[natural_gas_global_bus, electricity_bus,steam_bus] = get_bus_list_by_name('natural_gas_global_bus', 'electricity_bus', 'steam_bus')




 
back_electricity_tr = create_back_Trasformer('back_electricity_tr', natural_gas_global_bus, electricity_bus, 9999)
back_steam_tr = create_back_Trasformer('back_steam_tr', natural_gas_global_bus, electricity_bus, 9999)

