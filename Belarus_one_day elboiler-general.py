

# from errno import EHOSTDOWN
# from tkinter import E
from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
# import oemof_visio as oev
 
#  

# слабые метса модели - список
# умножить на два в датафрейме электрокотлы
# убрать потовры - имена файлов
# удобство исходных данных
# проверить электрокотлы 
# вариант с параллельными тепловыми спросами
# быстрая замена цены на газ с помощью словаря
# быстрая замена профиля нагрзузок
# быстрая расчет мощности по объему на основе профиля
# соотношение э/т для тэц - переменная
# уточнить мощность блок-станций
# перенос в эксель: по большим группам, по станциям, по блокам: заполнение электрического графика (полная выработка, спрос без эк), нагрузка электрокотлов

#################################################################################
number_of_time_steps = 24
current_folder = os.getcwd()
el_global_data = pd.read_excel(os.path.join(current_folder,'data.xlsx'), sheet_name='electric_demand_2021_odu')
el_chp_data = pd.read_excel(os.path.join(current_folder,'data.xlsx'), sheet_name='chp_el_winter_workday_abs')
#################################################################################



peak_load = max(el_global_data['el_winter_workDay_odu'][:number_of_time_steps]);
el_global_demand_profile = el_global_data['el_winter_workDay_odu'][:number_of_time_steps]/peak_load



small_chp_maxload = max( el_chp_data['Малые ТЭЦ'][:number_of_time_steps])
el_small_chp_profile = el_chp_data['Малые ТЭЦ'][:number_of_time_steps]/small_chp_maxload

# el_chp_demand_profile = el_chp_data['Минская ТЭЦ-4'][:number_of_time_steps]/ max(el_chp_data['Минская ТЭЦ-4'][:number_of_time_steps])
# el_chp_max_load = max( el_chp_data['Минская ТЭЦ-4'][:number_of_time_steps])


el_heat_ratio = 2.3;


current_start_date = dt.datetime(2020,6,8,1,0,0)
date_time_index = pd.date_range(current_start_date, periods=number_of_time_steps, freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index, infer_last_interval= False)



b_gas_bus= solph.Bus(label="gas")
b_el_global_bus = solph.Bus(label="electricity_global")
energysystem.add(b_gas_bus, b_el_global_bus)



#################################################################################
natural_gas_generator = solph.components.Source(
    label = "natural_gas_generator",
    outputs = {b_gas_bus:solph.Flow(variable_costs=0)})
energysystem.add(natural_gas_generator)
#################################################################################
# БелАЭС
#################################################################################
bel_npp_vver_1200_1 = solph.components.Source(
    label="bel_Npp_vver_1200_1_1",
	 
    outputs={b_el_global_bus:solph.Flow( min=0.75, nominal_value= 1170, variable_costs= -10)},
    
    # conversion_factors = {b_el_global_bus: 0.375}
    )
energysystem.add(bel_npp_vver_1200_1)
bel_npp_vver_1200_2 = solph.components.Source(
    label="bel_Npp_vver_1200_2",
	 	 
    outputs={b_el_global_bus:solph.Flow( fix = 1 , nominal_value= 1170, variable_costs= -10)},
    
    # conversion_factors = {b_el_global_bus: 0.375}
    )
energysystem.add(bel_npp_vver_1200_2)
#################################################################################
# Блок-станции
#################################################################################
night_start = 7 
night_end = 2
reduction = 0.8
block_station_profile = [reduction] * night_start + (number_of_time_steps - night_start-night_end) * [1] + night_end * [reduction]
block_station_ng = solph.components.Source(
    label="block_station_ng",
    outputs={b_el_global_bus:solph.Flow( fix = block_station_profile, nominal_value= 600, variable_costs=0),
             },
    )
energysystem.add(block_station_ng)
#################################################################################
# ТЭЦ
#################################################################################
# Могилевская ТЭЦ-2
#################################################################################
b_el_mogilev_tec_2_bus = solph.Bus(label="b_el_mogilev_tec_2_bus")
energysystem.add(b_el_mogilev_tec_2_bus)
mogilev_tec_2_maxload = max( el_chp_data['Могилевская_ТЭЦ-2'][:number_of_time_steps])
mogilev_tec_2_profile = el_chp_data['Могилевская_ТЭЦ-2'][:number_of_time_steps]/mogilev_tec_2_maxload
mogilev_tec_2 = solph.components.Transformer(
    label="mogilev_tec_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow( nominal_value= mogilev_tec_2_maxload, variable_costs= 32),  
             b_el_mogilev_tec_2_bus:solph.Flow(nominal_value = mogilev_tec_2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_mogilev_tec_2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(mogilev_tec_2)

mogilev_tec_2_el_demand =  solph.components.Sink(
        label="mogilev_tec_2_el_demand",
        inputs = {b_el_mogilev_tec_2_bus: solph.Flow(fix = mogilev_tec_2_profile, nominal_value = mogilev_tec_2_maxload )} 
    ) 
energysystem.add(mogilev_tec_2_el_demand)
elboilers_mogilev_tec_2 = solph.components.Transformer(
    label="elboilers_mogilev_tec_2",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_mogilev_tec_2_bus:solph.Flow(nominal_value= 40.37 / el_heat_ratio, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio / 0.99, b_el_mogilev_tec_2_bus: 1}
    )
energysystem.add(elboilers_mogilev_tec_2)
#################################################################################
# Бобруйская ТЭЦ-2 
#################################################################################
b_el_bobruisk_tec_2_bus = solph.Bus(label="b_el_bobruisk_tec_2_bus")
energysystem.add(b_el_bobruisk_tec_2_bus)
bobruisk_tec_2_maxload = max( el_chp_data['Бобруйская ТЭЦ-2'][:number_of_time_steps])
bobruisk_tec_2_profile = el_chp_data['Бобруйская ТЭЦ-2'][:number_of_time_steps]/bobruisk_tec_2_maxload
bobruisk_tec_2 = solph.components.Transformer(
    label="bobruisk_tec_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow( nominal_value= bobruisk_tec_2_maxload, variable_costs= 31.4),  
             b_el_bobruisk_tec_2_bus:solph.Flow(nominal_value = bobruisk_tec_2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_mogilev_tec_2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(bobruisk_tec_2)

elboilers_bobruisk_tec_2 = solph.components.Transformer(
    label="elboilers_bobruisk_tec_2",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_bobruisk_tec_2_bus:solph.Flow(nominal_value= 30.32 / el_heat_ratio , variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio / 0.99, b_el_bobruisk_tec_2_bus: 1}
    )
energysystem.add(elboilers_bobruisk_tec_2)

bobruisk_tec_2_el_demand =  solph.components.Sink(
        label="bobruisk_tec_2_el_demand",
        inputs = {b_el_bobruisk_tec_2_bus: solph.Flow(fix = bobruisk_tec_2_profile, nominal_value = bobruisk_tec_2_maxload )} 
    ) 
energysystem.add(bobruisk_tec_2_el_demand)

#################################################################################
# Гродненская ТЭЦ-2 
#################################################################################
b_el_grodno_tec_2_bus = solph.Bus(label="b_el_grodno_tec_2_bus")
energysystem.add(b_el_grodno_tec_2_bus)
grodno_tec_2_maxload = max( el_chp_data['Гродненская ТЭЦ-2'][:number_of_time_steps])
grodno_tec_2_profile = el_chp_data['Гродненская ТЭЦ-2'][:number_of_time_steps] / grodno_tec_2_maxload
grodno_tec_2 = solph.components.Transformer(
    label="grodno_tec_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= grodno_tec_2_maxload, variable_costs= 28),  
             b_el_grodno_tec_2_bus:solph.Flow(nominal_value = grodno_tec_2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_grodno_tec_2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(grodno_tec_2)

elboilers_grodno_tec_2 = solph.components.Transformer(
    label="elboilers_grodno_tec_2",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_grodno_tec_2_bus:solph.Flow(nominal_value = 60.53 / el_heat_ratio , variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio / 0.99, b_el_grodno_tec_2_bus: 1}
    )
energysystem.add(elboilers_grodno_tec_2)
grodno_tec_2_el_demand =  solph.components.Sink(
        label="grodno_tec_2_el_demand",
        inputs = {b_el_grodno_tec_2_bus: solph.Flow(fix = grodno_tec_2_profile, nominal_value = grodno_tec_2_maxload )} 
    ) 
energysystem.add(grodno_tec_2_el_demand)
#################################################################################
# Новополоцкая ТЭЦ 
#################################################################################
b_el_novopozkay_tec_2_bus = solph.Bus(label="b_el_novopozkay_tec_bus")
energysystem.add(b_el_novopozkay_tec_2_bus)
novopozkay_tec_2_maxload = max( el_chp_data['Новополоцкая ТЭЦ'][:number_of_time_steps])
novopozkay_tec_2_profile = el_chp_data['Новополоцкая ТЭЦ'][:number_of_time_steps] / novopozkay_tec_2_maxload
novopozkay_tec_2 = solph.components.Transformer(
    label="novopozkya_tec_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= novopozkay_tec_2_maxload, variable_costs= 28),  
             b_el_novopozkay_tec_2_bus:solph.Flow(nominal_value = novopozkay_tec_2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_novopozkay_tec_2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(novopozkay_tec_2)
# нет электрокотлов
# energysystem.add(elboilers_grodno_tec_2)
novopozkay_tec_2_el_demand =  solph.components.Sink(
        label="novopozkya_tec_2_el_demand",
        inputs = {b_el_novopozkay_tec_2_bus: solph.Flow(fix = novopozkay_tec_2_profile, nominal_value = novopozkay_tec_2_maxload )} 
    ) 
energysystem.add(novopozkay_tec_2_el_demand)
#################################################################################
# Минская ТЭЦ-4
#################################################################################
b_el_minskay_tec_4_bus = solph.Bus(label="b_el_minskay_tec_4_bus")
energysystem.add(b_el_minskay_tec_4_bus)
minskay_tec_4_maxload = max( el_chp_data['Минская ТЭЦ-4'][:number_of_time_steps])
minskay_tec_4_profile = el_chp_data['Минская ТЭЦ-4'][:number_of_time_steps] / minskay_tec_4_maxload
minskay_tec_4 = solph.components.Transformer(
    label="minskay_tec_4",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= minskay_tec_4_maxload, variable_costs= 31.9),  
             b_el_minskay_tec_4_bus:solph.Flow(nominal_value = minskay_tec_4_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_minskay_tec_4_bus:1}    # продумать эфф. тэц
    )
energysystem.add(minskay_tec_4)
elboilers_minskay_tec_4 = solph.components.Transformer(
    label="elboilers_minskay_tec_4",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_minskay_tec_4_bus:solph.Flow(nominal_value = (160.56) / el_heat_ratio, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio / 0.99, b_el_minskay_tec_4_bus: 1}
    )
energysystem.add(elboilers_minskay_tec_4)
minskay_tec_4_el_demand =  solph.components.Sink(
        label="minskay_tec_4_el_demand",
        inputs = {b_el_minskay_tec_4_bus: solph.Flow(fix = minskay_tec_4_profile, nominal_value = minskay_tec_4_maxload )} 
    ) 
energysystem.add(minskay_tec_4_el_demand)
#################################################################################
# Минская ТЭЦ-3
#################################################################################
b_el_minskay_tec_3_bus = solph.Bus(label="b_el_minskay_tec_3_bus")
energysystem.add(b_el_minskay_tec_3_bus)
minskay_tec_3_maxload = max( el_chp_data['Минская ТЭЦ-3'][:number_of_time_steps])
minskay_tec_3_profile = el_chp_data['Минская ТЭЦ-3'][:number_of_time_steps] / minskay_tec_3_maxload
minskay_tec_3 = solph.components.Transformer(
    label="minskay_tec_3",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= minskay_tec_3_maxload, variable_costs= 36.3),  
             b_el_minskay_tec_3_bus:solph.Flow(nominal_value = minskay_tec_3_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_minskay_tec_3_bus:1}    # продумать эфф. тэц
    )
energysystem.add(minskay_tec_3)
elboilers_minskay_tec_3 = solph.components.Transformer(
    label="elboilers_minskay_tec_3",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_minskay_tec_3_bus:solph.Flow(nominal_value = 100.28 / el_heat_ratio, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio / 0.99, b_el_minskay_tec_3_bus: 1}
    )
energysystem.add(elboilers_minskay_tec_3)
minskay_tec_3_el_demand =  solph.components.Sink(
        label="minskay_tec_3_el_demand",
        inputs = {b_el_minskay_tec_3_bus: solph.Flow(fix = minskay_tec_3_profile, nominal_value = minskay_tec_3_maxload)} 
    ) 
energysystem.add(minskay_tec_3_el_demand)
#################################################################################
# Гомельская ТЭЦ-2
#################################################################################
b_el_gomelskya_tec2_bus = solph.Bus(label="b_el_gomelskya_tec2_bus")
energysystem.add(b_el_gomelskya_tec2_bus)
gomelskya_tec2_maxload = max( el_chp_data['Гомельская ТЭЦ-2'][:number_of_time_steps])
gomelskya_tec2_profile = el_chp_data['Гомельская ТЭЦ-2'][:number_of_time_steps] / gomelskya_tec2_maxload
gomelskya_tec2 = solph.components.Transformer(
    label="gomelskya_tec2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= gomelskya_tec2_maxload, variable_costs= 31.2),  
             b_el_gomelskya_tec2_bus:solph.Flow(nominal_value = gomelskya_tec2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_gomelskya_tec2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(gomelskya_tec2)
elboilers_gomelskya_tec2 = solph.components.Transformer(
    label="elboilers_gomelskya_tec2",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_gomelskya_tec2_bus:solph.Flow(nominal_value = 80.34 / el_heat_ratio, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio / 0.99, b_el_gomelskya_tec2_bus: 1}
    )
energysystem.add(elboilers_gomelskya_tec2)
gomelskya_tec2_el_demand =  solph.components.Sink(
        label="gomelskya_tec2_el_demand",
        inputs = {b_el_gomelskya_tec2_bus: solph.Flow(fix = gomelskya_tec2_profile, nominal_value = gomelskya_tec2_maxload)} 
    ) 
energysystem.add(gomelskya_tec2_el_demand)
#################################################################################
# Мозырская ТЭЦ-2
#################################################################################
b_el_mozyrskay_tec2_bus = solph.Bus(label="b_el_mozyrskay_tec2_bus")
energysystem.add(b_el_mozyrskay_tec2_bus)
mozyrskay_tec2_maxload = max( el_chp_data['Мозырская ТЭЦ-2'][:number_of_time_steps])
mozyrskay_tec2_profile = el_chp_data['Мозырская ТЭЦ-2'][:number_of_time_steps] / mozyrskay_tec2_maxload
mozyrskay_tec2 = solph.components.Transformer(
    label="mozyrskay_tec2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= mozyrskay_tec2_maxload, variable_costs= 26.3),  
             b_el_mozyrskay_tec2_bus:solph.Flow(nominal_value = mozyrskay_tec2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_mozyrskay_tec2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(mozyrskay_tec2)

# Нет электрокотлов 
# elboilers_mozyrskay_tec2 = solph.components.Transformer(
#     label="elboilers_mozyrskay_tec2",
# 		inputs = {b_el_global_bus:solph.Flow()},
#     outputs={b_el_mozyrskay_tec2_bus:solph.Flow(nominal_value = 80 / 2, variable_costs= 1.2)},
# 		conversion_factors = {b_el_global_bus: 2, b_el_mozyrskay_tec2_bus: 1}
#     )
# energysystem.add(elboilers_mozyrskay_tec2)
mozyrskay_tec2_el_demand =  solph.components.Sink(
        label="mozyrskay_tec2_el_demand",
        inputs = {b_el_mozyrskay_tec2_bus: solph.Flow(fix = mozyrskay_tec2_profile, nominal_value = mozyrskay_tec2_maxload)} 
    ) 
energysystem.add(mozyrskay_tec2_el_demand)
#################################################################################
# Светлогорская ТЭЦ
#################################################################################
b_el_svetlogorskay_tec_bus = solph.Bus(label="b_el_svetlogorskay_tec_bus")
energysystem.add(b_el_svetlogorskay_tec_bus)
svetlogorskay_tec_maxload = max( el_chp_data['Светлогорская ТЭЦ'][:number_of_time_steps])
svetlogorskay_tec_profile = el_chp_data['Светлогорская ТЭЦ'][:number_of_time_steps] / svetlogorskay_tec_maxload
svetlogorskay_tec = solph.components.Transformer(
    label="svetlogorskay_tec",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= svetlogorskay_tec_maxload, variable_costs= 49.7),  
             b_el_svetlogorskay_tec_bus:solph.Flow(nominal_value = svetlogorskay_tec_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_svetlogorskay_tec_bus:1}    # продумать эфф. тэц
    )
energysystem.add(svetlogorskay_tec)
# нет электрокотлов
# elboilers_svetlogorskay_tec = solph.components.Transformer(
#     label="elboilers_svetlogorskay_tec",
# 		inputs = {b_el_global_bus:solph.Flow()},
#     outputs={b_el_svetlogorskay_tec_bus:solph.Flow(nominal_value = 80 / 2, variable_costs= 1.2)},
# 		conversion_factors = {b_el_global_bus: 2, b_el_svetlogorskay_tec_bus: 1}
#     )
# energysystem.add(elboilers_svetlogorskay_tec)
svetlogorskay_tec_el_demand =  solph.components.Sink(
        label="svetlogorskay_tec_el_demand",
        inputs = {b_el_svetlogorskay_tec_bus: solph.Flow(fix = svetlogorskay_tec_profile, nominal_value = svetlogorskay_tec_maxload)} 
    ) 
energysystem.add(svetlogorskay_tec_el_demand)
#################################################################################
#################################################################################
# Миниская ТЭЦ-2
#################################################################################
b_el_minskaya_tec2_bus = solph.Bus(label="b_el_minskaya_tec2_bus")
energysystem.add(b_el_minskaya_tec2_bus)
minskaya_tec2_maxload = max( el_chp_data['Минская ТЭЦ-2'][:number_of_time_steps])
minskaya_tec2_profile = el_chp_data['Минская ТЭЦ-2'][:number_of_time_steps] / minskaya_tec2_maxload
minskaya_tec2 = solph.components.Transformer(
    label="minskaya_tec2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs= {b_el_global_bus:solph.Flow( nominal_value= minskaya_tec2_maxload, variable_costs= 31.2),  
             b_el_minskaya_tec2_bus:solph.Flow(nominal_value = minskaya_tec2_maxload,  variable_costs=0)
             },
    conversion_factors = {b_gas_bus:3.5, b_el_global_bus:1, b_el_minskaya_tec2_bus:1}    # продумать эфф. тэц
    )
energysystem.add(minskaya_tec2)
elboilers_minskaya_tec2 = solph.components.Transformer(
    label="elboilers_minskaya_tec2",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_el_minskaya_tec2_bus:solph.Flow(nominal_value = 40.05 / el_heat_ratio, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: el_heat_ratio  / 0.99, b_el_minskaya_tec2_bus: 1}
    )
energysystem.add(elboilers_minskaya_tec2)
minskaya_tec2_el_demand =  solph.components.Sink(
        label="minskaya_tec2_el_demand",
        inputs = {b_el_minskaya_tec2_bus: solph.Flow(fix = minskaya_tec2_profile, nominal_value = minskaya_tec2_maxload)} 
    ) 
energysystem.add(minskaya_tec2_el_demand)
#################################################################################
# РК и МТЭЦ
#################################################################################
b_th_district_boiler_bus = solph.Bus(label="b_th_district_boiler_bus")
energysystem.add(b_th_district_boiler_bus)
district_boiler_maxload = max( el_chp_data['РК и МТЭЦ Белэнерго'][:number_of_time_steps])
district_boiler_profile = el_chp_data['РК и МТЭЦ Белэнерго'][:number_of_time_steps] / district_boiler_maxload

boilers_district = solph.components.Transformer(
    label="boilers_district",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_th_district_boiler_bus:solph.Flow(variable_costs= 25/1)},
		conversion_factors = {b_el_global_bus: 1, b_th_district_boiler_bus: 0.9}
    )
energysystem.add(boilers_district)

elboilers_district = solph.components.Transformer(
    label="elboilers_district",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_th_district_boiler_bus:solph.Flow(nominal_value = 296.1 / 1, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: 1 / 0.99, b_th_district_boiler_bus: 1}
    )
energysystem.add(elboilers_district)

boilers_district_demand =  solph.components.Sink(
        label="boilers_district_demand",
        inputs = {b_th_district_boiler_bus: solph.Flow(fix = district_boiler_profile, nominal_value = district_boiler_maxload)} 
    ) 
energysystem.add(boilers_district_demand)

#################################################################################
# Тепло КЭС
#################################################################################
b_th_cpp_heat_bus = solph.Bus(label="b_th_cpp_heat_bus")
energysystem.add(b_th_cpp_heat_bus)
cpp_heat_maxload = max( el_chp_data['Тепло КЭС'][:number_of_time_steps])
cpp_heat_profile = el_chp_data['Тепло КЭС'][:number_of_time_steps] / cpp_heat_maxload

cpp_heat = solph.components.Transformer(
    label="cpp_heat",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_th_cpp_heat_bus:solph.Flow(variable_costs= 25/1)},
		conversion_factors = {b_el_global_bus: 1 / 0.99, b_th_cpp_heat_bus: 0.9}
    )
energysystem.add(cpp_heat)

elboilers_cpp = solph.components.Transformer(
    label="elboilers_cpp",
		inputs = {b_el_global_bus:solph.Flow()},
    outputs={b_th_cpp_heat_bus:solph.Flow(nominal_value = 80 / 1, variable_costs= 1.2)},
		conversion_factors = {b_el_global_bus: 1 / 0.99, b_th_cpp_heat_bus: 1}
    )
energysystem.add(elboilers_cpp)

cpp_heat_demand =  solph.components.Sink(
        label="cpp_heat_demand",
        inputs = {b_th_cpp_heat_bus: solph.Flow(fix = cpp_heat_profile, nominal_value = cpp_heat_maxload)} 
    ) 
energysystem.add(cpp_heat_demand)

#################################################################################
# Малые ТЭЦ
#################################################################################
small_chp = solph.components.Transformer(
    label="small_chp",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow( fix = el_small_chp_profile, nominal_value= small_chp_maxload, variable_costs=38)},
		conversion_factors = {b_gas_bus:2.5, b_el_global_bus: 0.57}
    )
energysystem.add(small_chp)
#################################################################################
startupOptions = [-100000] + 23* [2 * 100000]
shutdownOptions = 24 * [2 * 100000]
#################################################################################
# КЭС
#################################################################################
# Лукомольская ГРЭС
#################################################################################
lukomol_ccgt_427_block_9 = solph.components.Transformer(
    label="lukomol_ccgt_427_block_9",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(nonconvex = solph.NonConvex(maximum_startups = 1, startup_costs = startupOptions, shutdown_costs =shutdownOptions), min=0.4, max = 1, nominal_value= 427, variable_costs=41)},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.57}
    )
energysystem.add(lukomol_ccgt_427_block_9)
# #################################################################################
lukomol_K_300__block_1 = solph.components.Transformer(
    label="lukomol_K_300_block_1",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1, startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300__block_1)
# # #################################################################################
lukomol_K_300_block_2 = solph.components.Transformer(
    label="lukomol_K_300_block_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_2)
# #################################################################################
lukomol_K_300_block_3 = solph.components.Transformer(
    label="lukomol_K_300_block_3",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_3)
# #################################################################################
lukomol_K_300_block_4 = solph.components.Transformer(
    label="lukomol_K_300_block_4",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_4)
# #################################################################################
lukomol_K_300_block_5 = solph.components.Transformer(
    label="lukomol_K_300_block_5",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_5)
lukomol_K_300_block_6 = solph.components.Transformer(
    label="lukomol_K_300_block_6",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_6)
lukomol_K_300_block_7 = solph.components.Transformer(
    label="lukomol_K_300_block_7",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_7)
lukomol_K_300_block_8 = solph.components.Transformer(
    label="lukomol_K_300_block_8",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 300, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(lukomol_K_300_block_8)
##################################################################################
##################################################################################
# Березовская ГРЭС
##################################################################################
bereza_ccgt_427_block_7 = solph.components.Transformer(
    label="bereza_ccgt_427_block_7",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions), min=0.4, max = 1, nominal_value= 427, variable_costs=40)},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.57}
    )
energysystem.add(bereza_ccgt_427_block_7)
#################################################################################
bereza_K_160_block_4 = solph.components.Transformer(
    label="bereza_K_160_block_4",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(min=0.4, nominal_value = 160, variable_costs= 50, nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions))},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(bereza_K_160_block_4)
#################################################################################
bereza_SSG_25_block_4_1 = solph.components.Transformer(
    label="bereza_SSG_25_block_4_1",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow( nominal_value = 25, variable_costs= 60)},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.35}
    )
energysystem.add(bereza_SSG_25_block_4_1)
#################################################################################
bereza_SSG_25_block_4_2 = solph.components.Transformer(
    label="bereza_SSG_25_block_4_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow( nominal_value = 25, variable_costs= 60)},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 1}
    )
energysystem.add(bereza_SSG_25_block_4_2)
#################################################################################
#################################################################################
# Минская  ТЭЦ-5
#################################################################################
tec5_ccgt_399_block_2 = solph.components.Transformer(
    label="tec5_ccgt_399_block_2",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions), min=0.4, max = 1, nominal_value= 399.6, variable_costs=42)},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.57}
    )
energysystem.add(tec5_ccgt_399_block_2)
#################################################################################
tec5_TK_330_block_1 = solph.components.Transformer(
    label="tec5_TK_330_block_1",
		inputs = {b_gas_bus:solph.Flow()},
    outputs={b_el_global_bus:solph.Flow(nonconvex = solph.NonConvex(maximum_startups = 1,startup_costs = startupOptions,shutdown_costs =shutdownOptions), min=0.4, max = 1, nominal_value= 330, variable_costs=50)},
		conversion_factors = {b_gas_bus:1, b_el_global_bus: 0.40}
    )
energysystem.add(tec5_TK_330_block_1)
#################################################################################
# #################################################################################
# # Определение электрического графика
# #################################################################################
el_demand_global =  solph.components.Sink(
        label="el_demand_global",
        inputs = {b_el_global_bus: solph.Flow(fix = el_global_demand_profile, nominal_value = peak_load )} 
                
    ) 
energysystem.add(el_demand_global)
#################################################################################
model = solph.Model(energysystem)
model.solve(solver="cplex")


results = solph.processing.results(model)
data_el_global = solph.views.node(results, "electricity_global")["sequences"].dropna()
# data_el_mogilev = solph.views.node(results, "b_el_mogilev_tec_2_bus")["sequences"]
# data_el_global_chp = solph.views.node(results, "electricity_chp")["sequences"]
print(data_el_global)

# data

res = pd.DataFrame();
res['ВВЭР-1200_1'] = data_el_global[((bel_npp_vver_1200_1.label, b_el_global_bus.label),'flow')]
res['ВВЭР-1200_2'] = data_el_global[((bel_npp_vver_1200_2.label, b_el_global_bus.label),'flow')]
res['Блок-станции'] = data_el_global[((block_station_ng.label, b_el_global_bus.label),'flow')]

res['Малые ТЭЦ'] = data_el_global[((small_chp.label, b_el_global_bus.label),'flow')]

res['Могилевская ТЭЦ-2'] = data_el_global[((mogilev_tec_2.label, b_el_global_bus.label),'flow')]
res['Бобруйская ТЭЦ-2'] = data_el_global[((bobruisk_tec_2.label, b_el_global_bus.label),'flow')]
res['Гродненская ТЭЦ-2'] = data_el_global[((grodno_tec_2.label, b_el_global_bus.label),'flow')]
res['Новополоцкая ТЭЦ'] = data_el_global[((novopozkay_tec_2.label, b_el_global_bus.label),'flow')]
res['Минская ТЭЦ-4'] = data_el_global[((minskay_tec_4.label, b_el_global_bus.label),'flow')]
res['Минская ТЭЦ-3'] = data_el_global[((minskay_tec_3.label, b_el_global_bus.label),'flow')]
res['Гомельская ТЭЦ-2'] = data_el_global[((gomelskya_tec2.label, b_el_global_bus.label),'flow')]
res['Мозырская ТЭЦ-2'] = data_el_global[((mozyrskay_tec2.label, b_el_global_bus.label),'flow')]
res['Светлогорская ТЭЦ'] = data_el_global[((svetlogorskay_tec.label, b_el_global_bus.label),'flow')]
res['Минская ТЭЦ-2'] = data_el_global[((minskaya_tec2.label, b_el_global_bus.label),'flow')]



res['ПГУ-427_Лукомольская'] = data_el_global[((lukomol_ccgt_427_block_9.label, b_el_global_bus.label),'flow')]
res['ПГУ-427_Березовская'] = data_el_global[((bereza_ccgt_427_block_7.label, b_el_global_bus.label),'flow')]
res['ПГУ-399_ТЭЦ-5'] = data_el_global[((tec5_ccgt_399_block_2.label, b_el_global_bus.label),'flow')]


res['K-300_1_Лукомольская'] = data_el_global[((lukomol_K_300__block_1.label, b_el_global_bus.label),'flow')]
res['K-300_2_Лукомольская'] = data_el_global[((lukomol_K_300_block_2.label, b_el_global_bus.label),'flow')]
res['K-300_3_Лукомольская'] = data_el_global[((lukomol_K_300_block_3.label, b_el_global_bus.label),'flow')]
res['K-300_4_Лукомольская'] = data_el_global[((lukomol_K_300_block_4.label, b_el_global_bus.label),'flow')]
res['K-300_5_Лукомольская'] = data_el_global[((lukomol_K_300_block_5.label, b_el_global_bus.label),'flow')]
res['K-300_6_Лукомольская'] = data_el_global[((lukomol_K_300_block_6.label, b_el_global_bus.label),'flow')]
res['K-300_7_Лукомольская'] = data_el_global[((lukomol_K_300_block_7.label, b_el_global_bus.label),'flow')]
res['K-300_8_Лукомольская'] = data_el_global[((lukomol_K_300_block_8.label, b_el_global_bus.label),'flow')]


res['K-160_1_Березовская'] = data_el_global[((bereza_K_160_block_4.label, b_el_global_bus.label),'flow')]
res['ГТУ-25_1_Березовская'] = data_el_global[((bereza_SSG_25_block_4_1.label, b_el_global_bus.label),'flow')]
res['ГТУ-25_2_Березовская'] = data_el_global[((bereza_SSG_25_block_4_2.label, b_el_global_bus.label),'flow')]


res['ТК-330_ТЭЦ-5'] = data_el_global[((tec5_TK_330_block_1.label, b_el_global_bus.label),'flow')]

# order = res.keys();


demand = pd.DataFrame();
demand['Исходный спрос'] = data_el_global[(( b_el_global_bus.label, el_demand_global.label),'flow')]



el_boiler_df = pd.DataFrame();

el_boiler_df['ЭК_Могилевская ТЭЦ-2'] = data_el_global[((b_el_global_bus.label, elboilers_mogilev_tec_2.label),'flow')]
el_boiler_df['ЭК_Бобруйская ТЭЦ-2'] = data_el_global[((b_el_global_bus.label, elboilers_bobruisk_tec_2.label),'flow')]
el_boiler_df['ЭК_Гродненская ТЭЦ-2'] = data_el_global[((b_el_global_bus.label, elboilers_grodno_tec_2.label),'flow')]
el_boiler_df['ЭК_Минская ТЭЦ-4'] = data_el_global[((b_el_global_bus.label, elboilers_minskay_tec_4.label),'flow')]
el_boiler_df['ЭК_Минская ТЭЦ-3'] = data_el_global[((b_el_global_bus.label, elboilers_minskay_tec_3.label),'flow')]
el_boiler_df['ЭК_Гомельская ТЭЦ-2'] = data_el_global[((b_el_global_bus.label, elboilers_gomelskya_tec2.label),'flow')]
el_boiler_df['ЭК_Минская ТЭЦ-2'] =  data_el_global[((b_el_global_bus.label, elboilers_minskay_tec_3.label),'flow')]
# el_boiler_df['ЭК_Мозырская ТЭЦ-2'] = data_el_global[((b_el_global_bus.label, elboilers_mogilev_tec_2.label),'flow')]
# el_boiler_df['ЭК_Светлогорская ТЭЦ'] = data_el_global[((b_el_global_bus.label, elboilers_mogilev_tec_2.label),'flow')]
# el_boiler_df = el_boiler_df.multiply(el_heat_ratio);
el_boiler_df['ЭК_Тепло КЭС'] =  data_el_global[((b_el_global_bus.label, elboilers_cpp.label),'flow')]
el_boiler_df['ЭК_РК_и_МТЭЦ'] =  data_el_global[((b_el_global_bus.label, elboilers_district.label),'flow')]
el_boiler_df = el_boiler_df[el_boiler_df > 0]

print(el_boiler_df)

ax1 = el_boiler_df.plot(kind="area", ylim=(0, 7000), legend = 'reverse')



res = res.loc[:, (res != 0).any(axis=0)]
res = res[res > 0]
ax2 = res.plot(kind="area", ylim=(0, 7000), legend = 'reverse')
ax3 = demand.plot(kind="line", ylim=(0, 7000), ax=ax2 , color = 'black' , legend = 'reverse')

plt.show()



# res.to_excel('winter_day_result.xlsx')
# demand.to_excel('demand.xlsx')



# res['full_demand_el'] = data_el_global[((b_el_global_bus.label, el_demand_global.label),'flow')]
# res['chp_load_global'] = data_el_global[((chp.label, b_el_global_bus.label),'flow')]
# res['chp_load_fake'] = data_el_global_chp[((chp.label, b_el_chp.label),'flow')]

# res[res<0] = 0

# ax1 = res["dummy_el"].plot(kind="area", ylim=(0,9000), legend = 'reverse')


# order = ["dummy_el"]







# print(data_el_global)
# print(data_el_mogilev)



# out_cols_el = oev.plot.divide_bus_columns(
#     "b_el_mogilev_tec_2_bus", data_el_mogilev.columns
# )["in_cols"]

# in_cols_el = oev.plot.divide_bus_columns(
#     "b_el_mogilev_tec_2_bus", data_el_mogilev.columns
# )["out_cols"]

# ax1 = data_el_mogilev[out_cols_el].plot(kind="area", ylim=(0,1000), legend = 'reverse')





# out_cols_el = oev.plot.divide_bus_columns(
#     "electricity_global", data_el_global.columns
# )["in_cols"]
# in_cols_el = oev.plot.divide_bus_columns(
#     "electricity_global", data_el_global.columns
# )["out_cols"]
# res = pd.DataFrame();
# res['исходный спрос'] = data_el_global[(( b_el_global_bus.label, el_demand_global.label),'flow')]
# data_el_global[data_el_global<0] = 0
# ax1 = data_el_global[out_cols_el].plot(kind="area", ylim=(0,9000), legend = False)
# ax2 = res.plot(kind="line", ylim=(0,9000), ax=ax1, color ='black' ,legend = False)






# ax1 = data_el_mogilev[out_cols_el].plot(kind="area", ylim=(0,1000), legend = 'reverse')




# res['могилевская тэц'] = data_el_global[((mogilev_tec_2.label, b_el_global_bus.label),'flow')]
# ax1 = res.plot(kind="area", ylim=(0,1000), legend = False)


# res = pd.DataFrame();
# res['могилевская тэц_электрокотлы'] = data_el_global[((elboilers_mogilev_tec_2.label, b_el_mogilev_tec_2_bus.label),'flow')]
# ax1 = res.plot(kind="area", ylim=(0,1000), legend = False)






# res['хороший_без_минимума'] = data_el[((good_block.label, b_el.label),'flow')]
# res['промежуточный_минимум'] = data_el[((inter_block.label, b_el.label),'flow')]
# res['Спрос'] = data_el[((b_el.label, El_demand.label),'flow' )]

# print(data_el_global[((small_chp.label, b_el_global_bus.label),'flow')])




# cdict = {
#     (("variable_chp_gas", "electricity"), "flow"): "#42c77a",
#     (("fixed_chp_gas_2", "electricity_2"), "flow"): "#20b4b6",
#     (("fixed_chp_gas", "electricity"), "flow"): "#20b4b6",
#     (("fixed_chp_gas", "heat"), "flow"): "#20b4b6",
#     (("variable_chp_gas", "heat"), "flow"): "#42c77a",
#     (("heat", "demand_therm"), "flow"): "#5b5bae",
#     (("heat_2", "demand_th_2"), "flow"): "#5b5bae",
#     (("electricity", "demand_elec"), "flow"): "#5b5bae",
#     (("electricity_2", "demand_el_2"), "flow"): "#5b5bae",
#     (("heat", "excess_therm"), "flow"): "#f22222",
#     (("heat_2", "excess_bth_2"), "flow"): "#f22222",
#     (("electricity", "excess_elec"), "flow"): "#f22222",
#     (("electricity_2", "excess_bel_2"), "flow"): "#f22222",
#     (("electricity_global", "el_demand_global"), "flow"): "#20b4b6",
# }

# mp = oev.plot.io_plot(
#     bus_label="electricity_global",
#     df=data_el_global["sequences"],
#     cdict=cdict,
#     # smooth=smooth_plot,
#     # line_kwa={"linewidth": 4},
#     # ax=fig.add_subplot(3, 2, 2),
#     # inorder=[
#     #     (("fixed_chp_gas", "electricity"), "flow"),
#     #     (("variable_chp_gas", "electricity"), "flow"),
#     # ],
#     # outorder=[
#     #     (("electricity", "demand_elec"), "flow"),
#     #     (("electricity", "excess_elec"), "flow"),
#     # ]
# )







# res = pd.DataFrame();

# for elem in energysystem.nodes:
#   res[elem.label] = data_el_global[((elem.label, b_el_global_bus.label),'flow')]


# res[tec5_ccgt_399_block_2.label] = data_el_global[   ((tec5_ccgt_399_block_2.label, b_el_global_bus.label),'flow')   ]
# # res[back_stop_tech.label] = data_el_global[   ((back_stop_tech.label, b_el_global_bus.label),'flow')   ]


# ax1 = res.plot(kind="area", ylim=(0,9000), legend = 'reverse')
# # ax2 = res.plot(kind="area", ylim=(0,9000), legend = 'reverse')

# ax1.set_xlabel("Дата")
# ax1.set_ylabel("Мощность, МВт (э)")
 
# plt.show()  



# res['dummy_el'] = data_el_global[((dummy_el.label, b_el_global_bus.label),'flow')]



# res['dummy_el'] = data_el_global[((dummy_el.label, b_el_global_bus.label),'flow')]
# res['full_demand_el'] = data_el_global[((b_el_global_bus.label, el_demand_global.label),'flow')]
# res['chp_load_global'] = data_el_global[((chp.label, b_el_global_bus.label),'flow')]
# res['chp_load_fake'] = data_el_global_chp[((chp.label, b_el_chp.label),'flow')]




# order = ["dummy_el"]


# res[res<0] = 0


# ax1 = res["dummy_el"].plot(kind="area", ylim=(0,9000), legend = 'reverse')
# ax2 = res["full_demand_el"].plot(kind="line", style = 'o-'  , legend = 'reverse'  )


# ax1 = res["chp_load_global"].plot(kind="area",stacked=True , legend = 'reverse')
# ax2 = res["chp_load_fake"].plot(kind="area",stacked=True , legend = 'reverse')



# ax1.set_xlabel("Дата")
# ax1.set_ylabel("Мощность, МВт (э)")
 
# plt.show()  


# res = pd.DataFrame();
# res['плохой_источник_минимум_nonconvex'] = data_el[((bad_block.label, b_el.label),'flow')]
# res['хороший_без_минимума'] = data_el[((good_block.label, b_el.label),'flow')]
# res['промежуточный_минимум'] = data_el[((inter_block.label, b_el.label),'flow')]
# res['Спрос'] = data_el[((b_el.label, El_demand.label),'flow' )]


# color_dict = {
#    bad_block: "#00b050", 
#   #  "БелАЭС" :  "#00b050",
#   #  "Новая АЭС" : "#a9d18e", 
#   #  "Блок-станции" : "#7030a0",  
#   #  "ТЭЦ": "#f57a23", 
#   #  "ПГУ" : "#ffff00", 
#   #  "Турбина 'К'": "#0080ff", 
#   #  "ГЭС": "#00ffff" ,
#   #  "ВЭУ": "#0080ff" ,
#   #  "СЭС": "#ffff00", 
#   #  "Электрокотлы": "#8080ff", 
#   #  "ВИЭ": "#808080"
   
#    }

# res[res<0] = 0

 
# order = ["плохой_источник_минимум_nonconvex", 'промежуточный_минимум' ,'хороший_без_минимума'  ]

# print(res[order])

 
# ax1 = res[order].plot(kind="area", ylim=(0,7000), legend = 'reverse')
# ax1 = res["хороший_без_минимума"].plot(kind="area", ylim=(0,7000), legend = 'reverse')
# ax1 = res['Дорогой_минимум'].plot(kind="area", ylim=(0,7000), legend = 'reverse')
# ax2 = res['Дорогой_минимум'].plot(kind="area", ylim=(0,7000), legend = 'reverse')



# ax2 = res["Спрос"].plot(kind="line", ax = ax1  , legend = 'reverse'  )
# ax2 = data_el["Мощность без ЭК"].plot(kind="line", ax = ax1, color = color_dict , legend = 'reverse'  )
# ax3 = data_h[order_h].plot(kind="area", ylim=(0,7000),ax = fig.add_subplot(1,2,2), color = color_dict,)
# ax1.title = 'asdfasd'

# ax1.set_xlabel("Дата")
# ax1.set_ylabel("Мощность, МВт (э)")
 
# plt.show()  




##################################################
# model = solph.Model(energysystem)
# model.solve(solver="cplex")
##################################################
# results = solph.processing.results(model)
# data_el = solph.views.node(results, "electricity")["sequences"]
# data_h = solph.views.node(results, "heat_water")["sequences"]


# solph.views.convert_keys_to_strings(results)

# print(results[( Import_Gas, b_gas_bus)]['sequences'])

# print(results[(E_CHP_Heat_Water, b_el )]['sequences'])
# print(results[(E_CHP_Heat_Water, b_heat )]['sequences'])

# e = results[(E_CHP_Heat_Water, b_el )]['sequences']['flow'][-1]
# h = results[(E_CHP_Heat_Water, b_heat )]['sequences']['flow'][-1]
# g = results[(b_gas_bus, E_CHP_Heat_Water )]['sequences']['flow'][-1]


# print(e,h,g)


# print(sum(results[( Import_Gas, b_gas_bus)]['sequences']['flow']))

 


# node_gen = energysystem.groups['A_BelNPP']
# print(results[(E_CHP_Heat_Water, b_el)])

 





# flows = [x for x in results.keys() ]
# res= solph.processing.create_dataframe(model)
# res.to_excel("result_output.xlsx")
# views.convert_keys_to_strings(results)
# print(results[('Natural_Gas', 'natural_gas')]['sequences'])
# data_gas = solph.views.node(results, 'Natural_Gas')
# data_ng = solph.views.node(results, "natural_gas")["sequences"];
# data_el.rename({(('A_BelNPP', 'electricity'), 'flow'):'БелАЭС'})
# pprint.pprint(data_el)


# out_cols_el = oev.plot.divide_bus_columns(
#     "electricity", data_el.columns
# )["in_cols"]

# in_cols_el = oev.plot.divide_bus_columns(
#     "electricity", data_el.columns
# )["out_cols"]


# out_cols_h = oev.plot.divide_bus_columns(
#     "heat_water", data_h.columns
# )["in_cols"]

# in_cols_h = oev.plot.divide_bus_columns(
#     "heat_water", data_h.columns
# )["out_cols"]


# color_dict = {
#    "Мощность без ЭК" : "#000000", 
#    "БелАЭС" :  "#00b050",
#    "Новая АЭС" : "#a9d18e", 
#    "Блок-станции" : "#7030a0",  
#    "ТЭЦ": "#f57a23", 
#    "ПГУ" : "#ffff00", 
#    "Турбина 'К'": "#0080ff", 
#    "ГЭС": "#00ffff" ,
#    "ВЭУ": "#0080ff" ,
#    "СЭС": "#ffff00", 
#    "Электрокотлы": "#8080ff", 
#    "ВИЭ": "#808080"
   
#    }



# elboiler_in_key = (('electricity', 'F_El_Boiler'), 'flow') 
# in_cols_el.remove(elboiler_in_key)
# fig = plt.figure()

# data_el = data_el[out_cols_el+in_cols_el]




# data_el["БелАЭС"] = data_el.pop((('A_BelNPP', 'electricity'), 'flow'))
# data_el["Новая АЭС"] = data_el.pop((('B_New_NPP_TOI', 'electricity'), 'flow'))
# data_el["Блок-станции"] = data_el.pop((('C_Block_Station', 'electricity'), 'flow'))
# data_el["ТЭЦ"] = data_el.pop((('E_CHP_Heat_Water', 'electricity'), 'flow'))
# data_el["ПГУ"] = data_el.pop((('F_CCGT', 'electricity'), 'flow'))
# data_el["Турбина 'К'"] = data_el.pop((('G_Turb_K', 'electricity'), 'flow'))


# ren_df= pd.DataFrame({"wind":data_el.pop((('wind', 'electricity'), 'flow'))})
# ren_df["hydro"]=data_el.pop((('hydro', 'electricity'), 'flow'))
# ren_df["Solar"]=data_el.pop((('PV', 'electricity'), 'flow'))
# ren_df["renewables"] = ren_df["wind"] + ren_df["Solar"] + ren_df["hydro"]


# data_el["ВИЭ"] = ren_df["renewables"]


# data_h["ТЭЦ"] = data_h.pop((('E_CHP_Heat_Water', 'heat_water'), 'flow'))
# data_h["Электрокотлы"] = data_h.pop((('F_El_Boiler', 'heat_water'), 'flow'))


# data_el["Мощность без ЭК"] = data_el.pop((( 'electricity','El_demand'), 'flow'))


# order_el = ["БелАЭС","Новая АЭС","Блок-станции","ТЭЦ","ПГУ","Турбина 'К'", "ВИЭ"]
# order_h = ["ТЭЦ","Электрокотлы"]




# data_el[order_el].to_excel(current_folder+"\output_el.xlsx", header = True)
# data_h[order_h].to_excel(current_folder+"\output_h.xlsx", header = True)
# data_el["Мощность без ЭК"].to_excel(current_folder+"\output_el_load.xlsx", header = True)




# ax1 = data_el[order_el].plot(kind="area", ylim=(0,7000),ax = fig.add_subplot(1,2,1) , color = color_dict, legend = 'reverse' )
# # ax2 = data_el["Мощность без ЭК"].plot(kind="line", ax = ax1, color = color_dict , legend = 'reverse'  )
# # ax3 = data_h[order_h].plot(kind="area", ylim=(0,7000),ax = fig.add_subplot(1,2,2), color = color_dict,)
# # ax1.title = 'asdfasd'
# ax1.set_xlabel("Дата")
# ax1.set_ylabel("Мощность, МВт (э)")
# ax3.set_xlabel("Дата")
# ax3.set_ylabel("Мощность, МВт (т)")
# plt.show()  


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





