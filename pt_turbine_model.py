
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


data_folder = os.getcwd()+'/data'
el_global_abs_profile = pd.read_excel(os.path.join(data_folder,'data_by_day.xlsx'), sheet_name='electric_demand_2021_odu')['el_winter_workDay_odu'][:number_of_time_steps]
heat_demand_data = [3000] * 24;
steam_demand_data = [3000] * 24;


##########################################################################################################################
natural_gas_global_bus = solph.Bus(label = "natural_gas_global_bus" )
electricity_bus = solph.Bus(label = "electricity_bus" )
heat_water_bus = solph.Bus(label = "heat_water_bus" )
steam_bus = solph.Bus(label = "steam_bus" )
energysystem.add(natural_gas_global_bus, electricity_bus, heat_water_bus, steam_bus)
##########################################################################################################################

natural_gas_generator_source = solph.components.Source ( 
			label = 'natural_gas_generator_source',
			outputs = {natural_gas_global_bus: solph.Flow(variable_costs = 10)} 
   )
energysystem.add(natural_gas_generator_source) 

  
##########################################################################################################################
back_electricity_tr = solph.components.Source (
    label = 'back_electricity_tr',
		outputs = {electricity_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		
 ) 
energysystem.add(back_electricity_tr)
 
back_heat_water_tr = solph.components.Source (
    label = 'back_heat_water_tr',
		outputs = {heat_water_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		
 ) 
energysystem.add(back_heat_water_tr)
 

back_steam_tr = solph.components.Source (
    label = 'back_steam_tr',
		outputs = {steam_bus: solph.Flow(nominal_value = 10000, variable_costs = 999999)},
		
 ) 
energysystem.add(back_steam_tr)
##########################################################################################################################

 
##########################################################################################################################


chp_pt_60_gas_inner_general_bus = solph.Bus('chp_pt_60_gas_inner_general_bus')
chp_pt_60_gas_inner_P_bus = solph.Bus('chp_pt_60_gas_inner_P_bus')
chp_pt_60_on_of_bus = solph.Bus('chp_pt_60_on_of_bus')
chp_pt_60_heat_water_inner_chp_bus = solph.Bus('chp_pt_60_heat_water_inner_chp_bus')
chp_pt_60_steam_inner_bus = solph.Bus('chp_pt_60_steam_inner_bus')
chp_pt_60_electricity_inner_bus = solph.Bus('chp_pt_60_electricity_bus')
chp_pt_60_electricity_main_output_bus = solph.Bus('chp_pt_60_electricity_main_output_bus')

energysystem.add(chp_pt_60_gas_inner_general_bus, chp_pt_60_gas_inner_P_bus)
energysystem.add(chp_pt_60_on_of_bus, chp_pt_60_heat_water_inner_chp_bus )
energysystem.add(chp_pt_60_steam_inner_bus, chp_pt_60_electricity_inner_bus)
energysystem.add(chp_pt_60_electricity_main_output_bus)

# chp_pt_60_heat_water_main_output_bus = solph.Bus('chp_pt_60_heat_water_main_output_bus')
# chp_pt_60_steam_main_output_bus = solph.Bus('chp_pt_60_steam_main_output_bus')


chp_pt_60_gas_inner_general_tr = solph.components.Transformer (
    label = 'chp_pt_60_gas_inner_general_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {chp_pt_60_gas_inner_general_bus: solph.Flow(nominal_value = 198.36)},
		conversion_factors = {natural_gas_global_bus:1,chp_pt_60_gas_inner_general_bus:1}

 ) 

chp_pt_60_gas_inner_P_tr = solph.components.Transformer (
    label = 'chp_pt_60_gas_inner_P_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {chp_pt_60_gas_inner_P_bus: solph.Flow(nominal_value = 107.02)},
		conversion_factors = {natural_gas_global_bus:1,chp_pt_60_gas_inner_P_bus:1}
 ) 

chp_pt_60_P_mode_first_tr = solph.components.Transformer (
    label = 'chp_pt_60_P_mode_first_tr',
		inputs = {chp_pt_60_gas_inner_general_bus: solph.Flow()},
		outputs = {electricity_bus: solph.Flow(),
								chp_pt_60_on_of_bus: solph.Flow(),
								steam_bus: solph.Flow()
               },
		conversion_factors = {chp_pt_60_gas_inner_general_bus: (1 + 3.8) / 0.91, electricity_bus: 1, steam_bus: 3.8, chp_pt_60_on_of_bus: 100}
 ) 

chp_pt_60_T_mode_tr = solph.components.Transformer (
    label = 'chp_pt_60_T_mode_tr',
		inputs = {chp_pt_60_gas_inner_general_bus: solph.Flow()},
		outputs = {heat_water_bus: solph.Flow(),
								electricity_bus: solph.Flow()
             },
  	conversion_factors = {chp_pt_60_gas_inner_general_bus: (1 + 2.02) / 0.91, electricity_bus: 1, heat_water_bus: 2.02}
		
 ) 

chp_pt_60_P_mode_second_tr = solph.components.Transformer (
    label = 'chp_pt_60_P_mode_second_tr',
		inputs = {chp_pt_60_gas_inner_P_bus: solph.Flow(),
							chp_pt_60_on_of_bus: solph.Flow()
            },
		outputs = {electricity_bus: solph.Flow(),
								steam_bus: solph.Flow()
               },
		conversion_factors = {chp_pt_60_on_of_bus: 0.0001, chp_pt_60_gas_inner_P_bus: (1 + 3.8) / 0.91, electricity_bus: 1, steam_bus: 3.8}
 ) 

# chp_pt_60_electricity_main_output_tr = solph.components.Transformer (
#     label = 'chp_pt_60_electricity_main_output_tr',
# 		inputs = {chp_pt_60_electricity_inner_bus: solph.Flow(),
# 							chp_pt_60_heat_water_inner_chp_bus:solph.Flow(),
# 							chp_pt_60_steam_inner_bus: solph.Flow(),
#             },
# 		outputs = {electricity_bus: solph.Flow(nominal_value = 60),
# 							# heat_water_bus: solph.Flow(),
# 							# steam_bus:solph.Flow()
#              },
#  ) 


energysystem.add(chp_pt_60_gas_inner_general_tr, chp_pt_60_gas_inner_P_tr)
energysystem.add(chp_pt_60_P_mode_first_tr, chp_pt_60_T_mode_tr)
energysystem.add(chp_pt_60_P_mode_second_tr)



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
electr_df['ПТ-60_электроэнергия-теплофикац.часть'] = electricity_data[((chp_pt_60_T_mode_tr.label, electricity_bus.label),'flow')]
electr_df['ПТ-60_электроэнергия-промышленнвя 1'] = electricity_data[((chp_pt_60_P_mode_first_tr.label, electricity_bus.label),'flow')]
electr_df['ПТ-60_электроэнергия-промышленная 2'] = electricity_data[((chp_pt_60_P_mode_second_tr.label, electricity_bus.label),'flow')]
# electr_df['Дорогой генератор'] = electricity_data[((back_electricity_tr.label, electricity_bus.label),'flow')]

print(electr_df['ПТ-60_электроэнергия-промышленнвя 1']) 


gas_df = pd.DataFrame()
gas_df['Расход газа ПТ-60 - П - 1 часть  '] = gas_data[((natural_gas_global_bus.label, chp_pt_60_gas_inner_general_tr.label),'flow')]
gas_df['Расход газа ПТ-60 - П - 2 часть '] = gas_data[((natural_gas_global_bus.label, chp_pt_60_gas_inner_P_tr.label),'flow')]




heat_water_df = pd.DataFrame()
heat_water_df['ТЭЦ-горячая вода'] = heat_water_data[((chp_pt_60_T_mode_tr.label, heat_water_bus.label),'flow')]


steam_data_df = pd.DataFrame()
steam_data_df['ТЭЦ-пар-1'] = steam_data[((chp_pt_60_P_mode_first_tr.label, steam_bus.label),'flow')]
steam_data_df['ТЭЦ-пар-2'] = steam_data[((chp_pt_60_P_mode_second_tr.label, steam_bus.label),'flow')]




fig, axes = plt.subplots(nrows=2, ncols=2)


maxY = 1000;


ax1 = electr_df.plot(kind="area", ylim=(0, maxY), ax = axes[0,1]  ,legend = 'reverse', title = '"Электроэнергия ПТ-60"')
ax2 = heat_water_df.plot(kind="area", ylim=(0, maxY) , ax = axes[1,1] ,  legend = 'reverse', title = 'Горячая вода ПТ-60')
ax2 = steam_data_df.plot(kind="area", ylim=(0, maxY) , ax = axes[1,0] ,  legend = 'reverse', title = 'Пар ПТ-60')
ax3 = gas_df.plot(kind="area", ylim=(0, maxY) , ax = axes[0, 0] ,  legend = 'reverse', title = 'Расход газа ПТ-60')


plt.show()