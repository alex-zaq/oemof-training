from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt

 

# быстрая отрисовка графиков
# быстрая запись в эксель


def get_dataframe_by_commodity(results, node_collection, target_bus):
	res = pd.DataFrame()
	results_by_commodity = solph.views.node(results, target_bus.label)["sequences"].dropna()
	print(results_by_commodity)
	for node in node_collection:
		outputs_node = [str(output) for output in node.outputs]  
		if target_bus.label in outputs_node:
			res[node.label] = results_by_commodity[((node.label, target_bus.label),'flow')]
	return res
    


	
    
  


  
  

  
    
  
  
  
 