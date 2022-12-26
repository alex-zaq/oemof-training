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
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)

data_folder = os.getcwd()+'/data'
el_global_abs_profile = pd.read_excel(os.path.join(data_folder,'data_by_day.xlsx'), sheet_name='electric_demand_2021_odu')['el_winter_workDay_odu'][:number_of_time_steps]

natural_gas_global_bus = solph.Bus(label = "natural_gas_global_bus" )
electricity_bus = solph.Bus(label = "electricity_bus" )
energysystem.add(natural_gas_global_bus, electricity_bus)



natural_gas_generator_source = solph.components.Source ( 
			label = 'natural_gas_generator_source',
			outputs = {natural_gas_global_bus: solph.Flow(variable_costs = 0)} 
   )
energysystem.add(natural_gas_generator_source) 
 
 
back_electricity_tr = solph.components.Transformer (
    label = 'back_electricity_tr',
		inputs = {natural_gas_global_bus: solph.Flow()},
		outputs = {electricity_bus: solph.Flow(nominal_value = 9000, variable_costs = -1000)},
		conversion_factors = {natural_gas_global_bus:2, electricity_bus:1}
		
 ) 
energysystem.add(back_electricity_tr) 


# ccgt_tr = solph.components.Transformer (
#     label = 'ccgt_tr',
# 		inputs = {natural_gas_global_bus: solph.Flow()},
# 		outputs = {electricity_bus: solph.Flow(nominal_value = 450)},
# 		conversion_factors = {natural_gas_global_bus: 1/0.57, electricity_bus:1}
		
#  ) 

eta_min = 0.45     # efficiency at minimal operation point
eta_max = 0.57       # efficiency at nominal operation point
P_out_min = 427*0.4      # absolute minimal output power
P_out_max = 427     # absolute nominal output power

# calculate limits of input power flow
P_in_min = P_out_min / eta_min
P_in_max = P_out_max / eta_max

# calculate coefficients of input-output line equation
c1 = (P_out_max-P_out_min)/(P_in_max-P_in_min)
c0 = P_out_max - c1*P_in_max

lst = [0.4,0.5,0.6,0.7,0.8,0.9]+[1]*18

ccgt_tr = solph.components.OffsetTransformer (
    label = 'ccgt_tr',
		inputs = {natural_gas_global_bus: solph.Flow(
      nominal_value = P_in_max,
      max = 1,
      min = P_in_min/P_in_max,
      nonconvex = solph.NonConvex() )},
		outputs = {electricity_bus: solph.Flow(fix = lst , nominal_value = 427)},
		conversion_factors = {natural_gas_global_bus: 1/0.57, electricity_bus:1},
    coefficients = [c0,c1]
		
 ) 





energysystem.add(ccgt_tr)

electricity_sink = solph.components.Sink(
		label = 'electricity_sink',
		inputs = {electricity_bus: solph.Flow( 
		fix = el_global_abs_profile,
   	nominal_value = 1)}
   )

energysystem.add(electricity_sink)

model = solph.Model(energysystem)
model.solve(solver="cplex")
results = solph.processing.results(model)

electricity_data = solph.views.node(results, "electricity_bus")["sequences"].dropna()
gas_data = solph.views.node(results, "natural_gas_global_bus")["sequences"].dropna()





electr_df = pd.DataFrame()
electr_df['Второй генератор'] = electricity_data[((back_electricity_tr.label, electricity_bus.label),'flow')]
electr_df['ПГУ'] = electricity_data[((ccgt_tr.label, electricity_bus.label),'flow')]

gas_df = pd.DataFrame()
gas_df['Расход газа ТЭЦ'] = gas_data[((natural_gas_global_bus.label, ccgt_tr.label),'flow')]


maxY = 8000 
fig, axes = plt.subplots(nrows=1, ncols=2)
ax1 = electr_df.plot(kind="area", ylim=(0, maxY), ax = axes[1]  ,legend = 'reverse', title = 'Генерация электроэнергии')
ax3 = gas_df.plot(kind="area", ylim=(0, maxY) , ax = axes[ 0] ,  legend = 'reverse', title = 'Расход газа ПГУ')



plt.show()


current_folder = os.getcwd()
result_folder = 'results'
path_results = os.path.join(current_folder, result_folder)

if not os.path.isdir(path_results):
  os.makedirs(path_results)

script_name = os.path.basename(__file__)[:-3]
path_local_result = os.path.join(path_results, script_name)

if not os.path.isdir(path_local_result):
  os.makedirs(path_local_result)

def getExcelResult(dataframe, path, tag_comment = ''):
  dataframe.to_excel(path + '/' + script_name + '_' + tag_comment + '.xlsx')

# gr = ESGraphRenderer(energy_system=energysystem, filepath=path_local_result+'/res' , img_format="png", txt_fontsize=10, txt_width=10)
# gr.view()

getExcelResult(electr_df, path_local_result, 'ccgt_elecr')
getExcelResult(gas_df, path_local_result, 'ccgt_gas')

