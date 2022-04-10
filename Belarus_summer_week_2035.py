

from oemof import solph
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
import oemof_visio as oev


##################################################
number_of_time_steps = 24 * 7
current_folder = os.getcwd()
demands_power = pd.read_excel(os.path.join(current_folder,'demands_power.xlsx'))
tech_fix = pd.read_excel(os.path.join(current_folder,"Tech_Fix.xlsx"))
tech_max = pd.read_excel(os.path.join(current_folder,"Tech_max.xlsx"))

##################################################


# Period options
###################################################
summer_case = slice(3768,3936),dt.datetime(2035,6,11)
winter_case = slice(408,576),dt.datetime(2035,1,15)

energy_peak_load_dict = {51.6:7890,45.51:6950}
peak_load = energy_peak_load_dict[45.51]

current_slice,current_start_date = summer_case
# current_slice,current_start_date = winter_case
 
date_time_index = pd.date_range(current_start_date,periods=number_of_time_steps,freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index)
demands_power = demands_power[current_slice].reset_index(drop=True)
tech_fix = tech_fix[current_slice].reset_index(drop=True)
tech_max = tech_max[current_slice].reset_index(drop=True)
###################################################



# NPP options
##################################################
Bel_NPP_fix_lst = ["Bel_NPP_July_December","Bel_NPP_April_December","Full_Power"]
NEW_NPP_TOI_fix_lst = ["New_NPP_June","New_NPP_February","Full_Power"]
Bel_NPP_fix = tech_fix[Bel_NPP_fix_lst[2]]
NEW_NPP_Toi = tech_fix[NEW_NPP_TOI_fix_lst[2]]
###################################################


# Fuels
################################################## 
b_gas= solph.Bus(label="natural_gas")
b_heat = solph.Bus(label="heat_water")
b_el = solph.Bus(label="electricity")
energysystem.add(b_gas,b_el,b_heat)
##################################################

# Tech
##################################################
Import_Gas = solph.Source(
    label = "Natural_Gas",outputs = {b_gas:solph.Flow(variable_costs=0)})
energysystem.add(Import_Gas)

A_Bel_NPP = solph.Source(
    label="A_BelNPP",
    outputs={b_el:solph.Flow(fix=NEW_NPP_Toi , 
    nominal_value=2400,variable_costs=15000)}
    )
energysystem.add(A_Bel_NPP)


B_New_NPP_TOI = solph.Source(
    label="B_New_NPP_TOI",
    outputs={b_el:solph.Flow(fix=NEW_NPP_Toi ,
    nominal_value=1255,variable_costs=0)}
    )
energysystem.add(B_New_NPP_TOI)



C_Block_Station = solph.Transformer(
        label = "C_Block_Station",
        inputs = {b_gas:solph.Flow()},
        outputs = {b_el:solph.Flow(nominal_value=684.6,fix = tech_fix["Block_Stations"] ,variable_costs=1)},
        conversion_factors = {b_el:0.45},
    )
energysystem.add(C_Block_Station)


D_CHP_Steam = solph.Source(
    label="D_CHP_Steam",
    outputs={b_el:solph.Flow(fix=tech_fix["CHP_Steam"]  ,
    nominal_value=250,variable_costs=0)}
    )
energysystem.add(D_CHP_Steam)

max=tech_max["CHP_HeatWater"]
E_CHP_Heat_Water = solph.Transformer(
        label = "E_CHP_Heat_Water",
        inputs = {b_gas:solph.Flow()},
        outputs = {b_el:solph.Flow(nominal_value=250,variable_costs = 1), b_heat:solph.Flow()},
        conversion_factors = {b_el:0.25, b_heat:0.5},
    )
energysystem.add(E_CHP_Heat_Water)


F_CCGT = solph.Transformer(
        label = "F_CCGT",
        inputs = {b_gas:solph.Flow()},
        outputs = {b_el:solph.Flow(nominal_value=1256, min = 0.286,variable_costs=1)},
        conversion_factors = {b_el:0.60},
    )
energysystem.add(F_CCGT)


min_tech = np.full(168, 0.072)
min_tech[120:] = 0


G_Turb_K = solph.Transformer(
        label = "G_Turb_K",
        inputs = {b_gas:solph.Flow()},
        outputs = {b_el:solph.Flow(nominal_value=8*300, min=min_tech, max=1, variable_costs=500)},
        conversion_factors = {b_el:0.45},
    )
energysystem.add(G_Turb_K)

# H_OCGT = solph.Transformer(
#         label = "H_OCGT",
#         inputs = {b_gas:solph.Flow()},
#         outputs = {b_el:solph.Flow(nominal_value=500, min=0, variable_costs=3)},
#         conversion_factors = {b_el:0.4},
#     )
# energysystem.add(H_OCGT)


F_El_Boiler = solph.Transformer(
        label = "F_El_Boiler",
        inputs = {b_el:solph.Flow()},
        outputs = {b_heat:solph.Flow(nominal_value=10000,variable_costs = 10000)},
        conversion_factors = {b_heat:0.99},
    )
energysystem.add(F_El_Boiler)


# Z_storage =  solph.components.GenericStorage(
#                 label= "Z_storage",
#                 nominal_storage_capacity=1500,
#                 inputs={b_el: solph.Flow(nominal_value=400,variable_costs=5)},
#                 outputs={b_el: solph.Flow(nominal_value=400)},
#                 initial_storage_level=0.2,
#                 infow_conversion_factor = 1,
#                 outfow_conversion_factor = 1
#             )
# energysystem.add(Z_storage)

# E_Boiler_Gas = solph.Transformer(
#         label = "E_Boiler_Gas",
#         inputs = {b_gas:solph.Flow()},
#         outputs = {b_heat:solph.Flow(nominal_value=500,variable_costs=10000)},
#         conversion_factors = {b_heat:0.9},
#     )
# energysystem.add(E_Boiler_Gas)

El_demand =  solph.Sink(
        label="El_demand",
        inputs = {b_el: solph.Flow(fix =demands_power["Electricity"], nominal_value = peak_load )} 
                
    ) 
energysystem.add(El_demand)



Heat_demand = solph.Sink(
        label = "Heat_water_demand",
        inputs = {b_heat:solph.Flow(fix = demands_power["Heat_Water"], nominal_value = 7969.86  )}
    
    )
energysystem.add(Heat_demand)

##################################################
model = solph.Model(energysystem)
model.solve(solver="cplex")
##################################################
results = solph.processing.results(model)
data_el = solph.views.node(results, "electricity")["sequences"]
data_h = solph.views.node(results, "heat_water")["sequences"]


out_cols_el = oev.plot.divide_bus_columns(
    "electricity", data_el.columns
)["in_cols"]

in_cols_el = oev.plot.divide_bus_columns(
    "electricity", data_el.columns
)["out_cols"]


out_cols_h = oev.plot.divide_bus_columns(
    "heat_water", data_h.columns
)["in_cols"]

in_cols_h = oev.plot.divide_bus_columns(
    "heat_water", data_h.columns
)["out_cols"]


color_dict = {
   (('electricity', 'El_demand'), 'flow') : "#000000", 
   (('A_BelNPP', 'electricity'), 'flow') :  "#008000",
   (('B_New_NPP_TOI', 'electricity'), 'flow') : "#00ff00", 
   (('C_Block_Station', 'electricity'), 'flow') : "#00ffff", 
   (('D_CHP_Steam', 'electricity'), 'flow') : "#8000ff", 
   (('F_CCGT', 'electricity'), 'flow') : "#ffff00", 
   (('G_Turb_K', 'electricity'), 'flow') : "#0080ff",
   (('E_Boiler_Gas', 'heat_water'), 'flow') : "#ff0000", 
   (('F_El_Boiler', 'heat_water'), 'flow') : "#0080ff", 
   

}


# current_color = color_dict
# current_color = None



elboiler_in_key = (('electricity', 'F_El_Boiler'), 'flow') 
in_cols_el.remove(elboiler_in_key)

fig = plt.figure()

ax1 = data_el[out_cols_el].plot(kind="area", ylim=(0,7000),ax = fig.add_subplot(1,2,1), legend = 'reverse' , title ="Электрический график (Лето - 2035)" )
ax2 = data_el[in_cols_el].plot(kind="line" ,ax = ax1, color = color_dict )
ax3 = data_h[out_cols_h].plot(kind="area", ylim=(0,7000),ax = fig.add_subplot(1,2,2), title = "Тепловой график (Лето - 2035)")
ax1.set_xlabel("Дата")
ax1.set_ylabel("Мощность, МВт (э)")
ax3.set_xlabel("Дата")
ax3.set_ylabel("Мощность, МВт (т)")
plt.show()  


# data_heat = solph.views.node_output_by_type(results, "heat_water")["sequences"]

# myplot = oev.plot.io_plot(
    
#     bus_label= "electricity",
#     df = data_el,
#     smooth= True,
        
# )





# out_cols = oev.plot.divide_bus_columns(
#     "electricity", data_el.columns
# )["out_cols"]

# storage_in = data_el[(('electricity', 'Z_storage'), 'flow')]
# storage_in *=-1

# ax = data_el[in_cols].plot(
#     kind="area"
# )

# myplot_heat = oev.plot.io_plot(
    
#     bus_label= "heat_water",
#     df = data_heat,
#     smooth= True,
        
# )


 


# exclude = ["El_demand","F_El_Boiler"]
# columns = [
#     c
#     for c in data.columns
#     if not any(s in c[0] or s in c[1] for s in exclude)
# ]


# dF_Electr = data[columns]


# # res = data[(("Z_storage","Electricity"),"flow")]

# fig, axes = plt.subplots(nrows=1, ncols=2)


# ax = dF_Electr.plot(ax = axes[0] ,kind="area",  stacked = True , grid=True, rot=0, ylim=(0,10000),legend = 'reverse')




 
###################################################### 


# data = solph.views.node(results, "heat_water")["sequences"]


# exclude = ["Heat_water_demand"]
# columns = [
#     c
#     for c in data.columns
#     if not any(s in c[0] or s in c[1] for s in exclude)
# ]


# dF_Heat = data[columns]




# ax = dF_Heat.plot(ax = axes[1],kind="area",  stacked = True , grid=True, rot=0,ylim=(0,10000),legend='reverse')



# plt.show()

# pylab.subplot(1,2,2)
# pylab.plot(ax) 

# pylab.show()

# results = solph.processing.results(model)


# solph.views.convert_keys_to_strings(results)

# # print(results[("CPP","b_el")]["sequences"])

# # print(results)

# cppInfo = solph.views.node(results, 'CPP')

# print(cppInfo)





