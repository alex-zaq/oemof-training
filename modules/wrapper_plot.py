from oemof import solph
from oemof.solph import views
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt



def get_dataframe_by_output_bus(results, node_collection, output_bus):
	res = pd.DataFrame()
	results_by_commodity = solph.views.node(results, output_bus.label)["sequences"].dropna()
	print(results_by_commodity)
	for node in node_collection:
		outputs_node = [str(output) for output in node.outputs]  
		if output_bus.label in outputs_node:
			res[node.label] = results_by_commodity[((node.label, output_bus.label),'flow')]
	return res

def get_dataframe_by_input_bus(results, node_collection, input_bus):
	res = pd.DataFrame()
	results_by_commodity = solph.views.node(results, input_bus.label)["sequences"].dropna()
	print(results_by_commodity)
	for node in node_collection:
		inputs_node = [str(output) for output in node.inputs]  
		if input_bus.label in inputs_node:
			res[node.label] = results_by_commodity[((input_bus.label, node.label),'flow')]
	return res
    


	
    
  


  
  

  
    
  
  
  
 