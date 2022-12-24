
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt


number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)


current_folder = os.getcwd()
el_global_abs_profile = pd.read_excel(os.path.join(current_folder,'data_by_day.xlsx'), sheet_name='electric_demand_2021_odu')['el_winter_workDay_odu'][:number_of_time_steps]
heat_demand_data = [400] * 24;
steam_demand_data = [600] * 24;


##########################################################################################################################
natural_gas_global_bus = solph.Bus(label = "natural_gas_global_bus" )
electricity_bus = solph.Bus(label = "electricity_bus" )
heat_water_bus = solph.Bus(label = "heat_water_bus" )
steam_bus = solph.Bus(label = "steam_bus" )
energysystem.add(natural_gas_global_bus, electricity_bus, steam_bus)
##########################################################################################################################

natural_gas_generator_source = solph.components.Source ( 
			label = 'natural_gas_generator_source',
			outputs = {natural_gas_global_bus: solph.Flow(variable_costs = 0)} 
   )
energysystem.add(natural_gas_generator_source) 

  
##########################################################################################################################
back_electricity_tr = solph.components.Transformer (
    label = 'back_electricity_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {electricity_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		
 ) 
energysystem.add(back_electricity_tr)
 
back_heat_water_tr = solph.components.Transformer (
    label = 'back_electricity_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {heat_water_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		
 ) 
energysystem.add(back_heat_water_tr)
 

back_steam_tr = solph.components.Transformer (
    label = 'back_steam_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {steam_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		
 ) 
energysystem.add(back_steam_tr)
##########################################################################################################################


#  1 т/ч = 0,627 МВт
# пт-60: el.power = 60, heat_water = 151 при расходе 220*0,627 = 137.94   steam = 210*1.163 = 244.23 при расходе  360*0,627 = 225.72


##########################################################################################################################

natural_gas_pt_60_bus = solph.Bus('natural_gas_pt_60_bus')
electricity_pt_60_bus = solph.Bus('electricity_pt_60_bus')
heat_water_chp_bus = solph.Bus('heat_water_chp_bus')
steam_chp_bus = solph.Bus('steam_chp_bus')

# chp_pt_60_natural_gas_tr = solph.components.Transformer (
#     label = 'chp_pt_60_natural_gas_tr',
# 		inputs = {natural_gas_global_bus: solph.Flow()},
# 		outputs = {natural_gas_pt_60_bus: solph.Flow(nominal_value = ?)},
		
#  ) 

chp_pt_60_P_mode_tr = solph.components.Transformer (
    label = 'chp_pt_60_P_mode_tr',
		inputs = {natural_gas_pt_60_bus: solph.Flow()},
		outputs = {electricity_pt_60_bus: solph.Flow(nominal_value = 60),
								steam_chp_bus: solph.Flow(nominal_value = 244.23)
               },
		conversion_factors = {natural_gas_pt_60_bus: 6.76, electricity_pt_60_bus: 1, steam_chp_bus: 4.07}
 ) 

chp_pt_60_T_mode_tr = solph.components.Transformer (
    label = 'chp_pt_60_T_mode_tr',
		inputs = {natural_gas_pt_60_bus: solph.Flow()},
		outputs = {electricity_pt_60_bus: solph.Flow(nominal_value = 6),
								heat_water_chp_bus: solph.Flow(nominal_value = 12)
             },
  	conversion_factors = {natural_gas_pt_60_bus: 4, electricity_pt_60_bus: 1, steam_chp_bus: 2}
		
 ) 


chp_electric_output_tr = solph.components.Transformer (
    label = 'chp_electric_output_tr',
		inputs = {electricity_pt_60_bus: solph.Flow()},
		outputs = {electricity_bus: solph.Flow(nominal_value = 60, min = 0.5, nonconvex = solph.NonConvex()),
             },
 ) 


energysystem.add(chp_pt_60_natural_gas_tr, chp_pt_60_P_mode_tr, chp_pt_60_P_mode_tr, chp_electric_output_tr)





##########################################################################################################################










 
   
##########################################################################################################################
electricity_sink = solph.components.Sink(
		label = 'electricity_demand',
		inputs = {electricity_bus: solph.Flow( 
		fix = el_global_abs_profile,
   	nominal_value = 1)}

   )
heat_water_sink = solph.components.Sink(
		label = 'heat_water_sink',
		inputs = {heat_water_bus: solph.Flow( 
		fix = heat_demand_data,
   	nominal_value = 1)}

   )
steam_sink = solph.components.Sink(
		label = 'steam_sink',
		inputs = {steam_bus: solph.Flow( 
		fix = steam_demand_data,
		nominal_value = 1)}
)
energysystem.add(electricity_sink, heat_water_sink, steam_sink)
##########################################################################################################################

model = solph.Model(energysystem)
model.solve(solver="cplex")
results = solph.processing.results(model)




electricity_data = solph.views.node(results, "electricity_bus")["sequences"].dropna()
heat_water_data = solph.views.node(results, "heat_water_bus")["sequences"].dropna()
steam_data = solph.views.node(results, "steam_bus")["sequences"].dropna()
gas_data = solph.views.node(results, "natural_gas_global_bus")["sequences"].dropna()


electr_df = pd.DataFrame()
electr_df['ТЭЦ-электроэнергия'] = electricity_data[((back_chp_electricity_tr.label, electricity_bus.label),'flow')]
# electr_df['Дорогой генератор'] = electricity_data[((back_electricity_tr.label, electricity_bus.label),'flow')]

gas_df = pd.DataFrame()
gas_df['Расход газа ТЭЦ'] = gas_data[((natural_gas_global_bus.label, back_chp_electricity_tr.label),'flow')]

heat_water_df = pd.DataFrame()
heat_water_df['ТЭЦ-горячая вода'] = heat_water_data[((back_chp_electricity_tr.label, heat_water_bus.label),'flow')]


fig, axes = plt.subplots(nrows=2, ncols=2)





ax1 = electr_df.plot(kind="area", ylim=(0, 3000), ax = axes[0,1]  ,legend = 'reverse', title = 'Генерация электроэнергии')
ax2 = heat_water_df.plot(kind="area", ylim=(0, 3000) , ax = axes[1,0] ,  legend = 'reverse', title = 'Генерация тепла')
ax3 = gas_df.plot(kind="area", ylim=(0, 3000) , ax = axes[0, 0] ,  legend = 'reverse', title = 'Расход газа ТЭЦ')


plt.show()