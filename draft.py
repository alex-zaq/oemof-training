

from oemof import solph
import pandas as pd
import matplotlib.pyplot as plt
import os
import pylab
import seaborn as sns


##################################################
number_of_time_steps = 24 * 7
current_folder = os.getcwd()
demands_power = pd.read_excel(os.path.join(current_folder,'demands_power.xlsx'))
tech_fix = pd.read_excel(os.path.join(current_folder,"Tech_Fix.xlsx"))
tech_max = pd.read_excel(os.path.join(current_folder,"Tech_max.xlsx"))


date_time_index = pd.date_range("06/11/2035",periods=number_of_time_steps,freq="H")
energysystem = solph.EnergySystem(timeindex=date_time_index)
##################################################



# options
##################################################
Bel_NPP_fix_lst = ["Bel_NPP_July_December","Bel_NPP_April_December","Full_Power"]
NEW_NPP_TOI_fix_lst = ["New_NPP_June","New_NPP_February","Full_Power"]
Bel_NPP_fix = tech_fix[Bel_NPP_fix_lst[2]]
NEW_NPP_Toi = tech_fix[NEW_NPP_TOI_fix_lst[2]]
###################################################


Bel_NPP_fix=Bel_NPP_fix[150:600]

buf = Bel_NPP_fix.reset_index(drop=True)


print(buf[0])