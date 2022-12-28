
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from oemof_visio import ESGraphRenderer


number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_5range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)


current_folder = os.getcwd()
el_global_abs_profile = pd.read_excel(os.path.join(current_folder,'data_by_day.xlsx'), sheet_name='electric_demand_2021_odu')['el_winter_workDay_odu'][:number_of_time_steps]
heat_demand_data = [1000] * 24;



natural_gas_global_bus = solph.Bus(label = "natural_gas_global_bus" )
electricity_bus = solph.Bus(label = "electricity_bus" )
heat_water_bus = solph.Bus(label = "heat_water_bus" )
# steam_bus = solph.Bus(label = "steam_bus" )
energysystem.add(natural_gas_global_bus, electricity_bus, heat_water_bus)


natural_gas_generator_source = solph.components.Source ( 
			label = 'natural_gas_generator_source',
			outputs = {natural_gas_global_bus: solph.Flow(variable_costs = 0)} 
   )
energysystem.add(natural_gas_generator_source) 
 
 
  
back_electricity_tr = solph.components.Transformer (
    label = 'back_electricity_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {electricity_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		conversion_factors = {natural_gas_global_bus:2, electricity_bus:1}
		
 ) 
energysystem.add(back_electricity_tr)
 
   
back_heat_water_tr = solph.components.Transformer (
    label = 'back_heat_water_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {heat_water_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
 ) 
energysystem.add(back_heat_water_tr)
 
 

chp_natural_gas_bus = solph.Bus('chp_natural_gas_bus')
energysystem.add(chp_natural_gas_bus)
 
chp_natural_gas_tr = solph.components.Transformer (
    label = 'chp_natural_gas_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {chp_natural_gas_bus: solph.Flow(nominal_value = 2000)},
 ) 
energysystem.add(chp_natural_gas_tr)
 
    
 
back_chp_electricity_tr = solph.components.Transformer (
    label = 'back_chp_electricity_tr',
		inputs = {chp_natural_gas_bus: solph.Flow()},
		outputs = {electricity_bus: solph.Flow(nominal_value = 500, variable_costs = 400, min = 0.2, nonconvex = solph.NonConvex()), heat_water_bus: solph.Flow()},
		conversion_factors = {chp_natural_gas_bus:4,  electricity_bus:1, heat_water_bus:2}
		
 ) 
energysystem.add(back_chp_electricity_tr)
 
 
   
   
electricity_sink = solph.components.Sink(
		label = 'electricity_sink',
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


energysystem.add(electricity_sink, heat_water_sink)

model = solph.Model(energysystem)
model.solve(solver="cplex")
results = solph.processing.results(model)


# print(results)

electricity_data = solph.views.node(results, "electricity_bus")["sequences"].dropna()
chp_gas_data = solph.views.node(results, "chp_natural_gas_bus")["sequences"].dropna()
heat_water_data = solph.views.node(results, "heat_water_bus")["sequences"].dropna()


electr_df = pd.DataFrame()
electr_df['ТЭЦ-электроэнергия'] = electricity_data[((back_chp_electricity_tr.label, electricity_bus.label),'flow')]
# electr_df['Дорогой генератор'] = electricity_data[((back_electricity_tr.label, electricity_bus.label),'flow')]

gas_df = pd.DataFrame()
gas_df['Расход газа ТЭЦ'] = chp_gas_data[((chp_natural_gas_bus.label, back_chp_electricity_tr.label),'flow')]

heat_water_df = pd.DataFrame()
heat_water_df['ТЭЦ-горячая вода'] = heat_water_data[((back_chp_electricity_tr.label, heat_water_bus.label),'flow')]


fig, axes = plt.subplots(nrows=2, ncols=2)





ax1 = electr_df.plot(kind="area", ylim=(0, 3000), ax = axes[0,1]  ,legend = 'reverse', title = 'Генерация электроэнергии')
ax2 = heat_water_df.plot(kind="area", ylim=(0, 3000) , ax = axes[1,0] ,  legend = 'reverse', title = 'Генерация тепла')
ax3 = gas_df.plot(kind="area", ylim=(0, 3000) , ax = axes[0, 0] ,  legend = 'reverse', title = 'Расход газа ТЭЦ')


gr = ESGraphRenderer(energy_system=energysystem, filepath="energy_system", img_format="png", txt_fontsize=10, txt_width=10)
gr.view()

plt.show()