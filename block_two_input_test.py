from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from oemof_visio import ESGraphRenderer

def createBackForBus(bus):
  return solph.components.Transformer(
		label = "back for"+ str(bus),
		inputs = {b_gas_bus: solph.Flow()},
    outputs = {bus:solph.Flow(variable_costs=99999)})
	
def addToEnergySystem(e, component):
  e.add(component)
   
 

number_of_time_steps = 24
current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)

current_folder = os.getcwd()
el_global_data_file = pd.read_excel(os.path.join(current_folder,'data_by_day.xlsx'), sheet_name='electric_demand_2021_odu')['el_winter_workDay_odu'][:number_of_time_steps];

el_global_profile = el_global_data_file/ max(el_global_data_file)
el_peak_load = 2000
heat_global_data = [1000]*24


b_gas_bus= solph.Bus(label="b_gas_bus")
fake_flow_on_off_bus= solph.Bus(label="fake_flow_on_off_bus")
b_el_global_bus = solph.Bus(label="b_el_global_bus")
b_heat_global_bus = solph.Bus(label="b_heat_global_bus")


energysystem.add(b_gas_bus, fake_flow_on_off_bus, b_el_global_bus, b_heat_global_bus)


natural_gas_generator_sr = solph.components.Source(
    label = "natural_gas_generator",
    outputs = {b_gas_bus:solph.Flow()})
energysystem.add(natural_gas_generator_sr)



el_back_generator_tr = createBackForBus(b_el_global_bus)
heat_back_generator_tr = createBackForBus(b_heat_global_bus)
energysystem.add(el_back_generator_tr,heat_back_generator_tr)


fake_flow_on_off_sr = solph.components.Source(
    label = "fake_flow_on_off_sr",
    outputs = {fake_flow_on_off_bus:solph.Flow(nominal_value = 1)})
energysystem.add(fake_flow_on_off_sr)

chp_tr = solph.components.Transformer(
    label="chp_tr",
		inputs = {b_gas_bus: solph.Flow(),
				  		fake_flow_on_off_bus: solph.Flow()
             },
    outputs={b_el_global_bus:solph.Flow(nominal_value = 500), b_heat_global_bus: solph.Flow()},
    conversion_factors = { fake_flow_on_off_bus: 0.0001,b_gas_bus: 4 , b_el_global_bus: 1, b_heat_global_bus: 2}
    )

addToEnergySystem(energysystem, chp_tr)

# energysystem.add(chp_tr)


########################################################################################################################################################################
########################################################################################################################################################################
electricity_sink =  solph.components.Sink(
        label="electricity_sink",
        inputs = {b_el_global_bus: solph.Flow(fix = el_global_profile, nominal_value = el_peak_load )} 
    ) 
heat_sink =  solph.components.Sink(
        label="heat_sink",
        inputs = {b_heat_global_bus: solph.Flow(fix = heat_global_data, nominal_value = 1 )} 
    ) 
energysystem.add(electricity_sink, heat_sink)
########################################################################################################################################################################
########################################################################################################################################################################
 


model = solph.Model(energysystem)
model.solve(solver="cplex")
results = solph.processing.results(model)

data_el_global = solph.views.node(results, "b_el_global_bus")["sequences"].dropna()
data_heat_global = solph.views.node(results, "b_heat_global_bus")["sequences"].dropna()
data_gas_global = solph.views.node(results, "b_gas_bus")["sequences"].dropna()


el_res = pd.DataFrame();
el_res['ТЭЦ'] = data_el_global[((chp_tr.label, b_el_global_bus.label),'flow')]
# el_res['Дорогой источник'] = data_el_global[((el_back_generator_tr.label, b_el_global_bus.label),'flow')]

heat_res = pd.DataFrame();
heat_res['ТЭЦ'] = data_heat_global[((chp_tr.label, b_heat_global_bus.label),'flow')]
# heat_res['Дорогой источник'] = data_heat_global[((heat_back_generator_tr.label, b_heat_global_bus.label),'flow')]

gas_res = pd.DataFrame();
gas_res['ТЭЦ'] = data_gas_global[((b_gas_bus.label,chp_tr.label),'flow')]

fig, axes = plt.subplots(nrows=2, ncols=2)

ax1 =el_res.plot(kind="area", ylim=(0, 5000), ax = axes[0,1] ,legend = 'reverse', title = 'Производство электроэнергии ')
ax2 =heat_res.plot(kind="area", ylim=(0, 5000), ax = axes[1,0] , legend = 'reverse', title = 'Производство тепла ')
ax3 =gas_res.plot(kind="area", ylim=(0, 5000), ax = axes[1,1] , legend = 'reverse', title = 'Потребление газа')


plt.show()