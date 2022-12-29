from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from modules.custom_blocks import *
 

# создать турбину типа Т
# создать турбину типа Р
# создать турбину типа ПТ
# создать электрокотел
# создать метод быстрого построения графиков
# сделать метод создания станции
#  (добавить в э все турбины,электрокотлы, станции со всеми настройками)


def get_station_method_by_energysystem(energy_system, block_collection):
	def create_Minskay_tec_4(input_fuel_flow, output_el_flow, heat_water_profile, shut_down_options):
		name = 'Минская ТЭЦ-4'
		[create_buses] = get_buses_method_by_energy_system(energy_system)
		[create_pt_turbine] = get_chp_method_by_energy_system(energy_system, block_collection)
		Minskay_tec_4_buses = create_buses(name +'_Отопление+ГВС')
		 
		pt_60 = create_pt_turbine('ПТ-60_'+ name, nominal_el_value = 60, min_power_fraction = 0.4, input_flow = input_fuel_flow,  )
	
		print("использование метода create_generic_station")


		print("настройка плановых ремонтов")
		print("создание спросов для станции")

		return [Minskay_tec_4_blocks, Minskay_tec_4_buses]
  
  

	
 		
    
	
    
  


  
  

  
    
  
  
  
 