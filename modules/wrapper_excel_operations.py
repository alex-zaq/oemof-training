from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
from oemof_visio import ESGraphRenderer
 

# создать турбину типа Т
# создать турбину типа Р
# создать турбину типа ПТ
# создать электрокотел
# создать метод быстрого построения графиков
# сделать метод создания станции
#  (добавить в э все турбины,электрокотлы, станции со всеми настройками)


def get_reader_by_folder(folder_data, src_file_name):
	def get_sheet_name_by_work_book(sheet_name):
		return pd.read_excel(os.path.join(folder_data, src_file_name + '.xlsx'), sheet_name= sheet_name)
	return get_sheet_name_by_work_book

def __get_local_path(folders_options):
		(cwd, folder_cases, folder_case) = folders_options
		path_results = os.path.join(cwd, folder_cases)
		path_local_result = os.path.join(path_results, folder_case)
		if not os.path.isdir(path_results):
			os.makedirs(path_results)
		if not os.path.isdir(path_local_result):
			os.makedirs(path_local_result)
		return path_local_result
 
def import_dataframe_to_excel(df, folders_options, excel_name):
		path_local_result = __get_local_path(folders_options)
		df.to_excel(path_local_result + '/'+ excel_name+'.xlsx')
 
def create_res_scheme(energy_system, folders_options):
		path_local_result = __get_local_path(folders_options)
		gr = ESGraphRenderer(energy_system=energy_system, filepath=path_local_result+'/res' , img_format="png", txt_fontsize=10, txt_width=10)
		gr.view()			

  



  
  

	
 		
    
	
    
  


  
  

  
    
  
  
  
 