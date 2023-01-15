import pandas as pd
import os
import matplotlib.pyplot as plt


data_folder = os.getcwd() + "/data_excel"
data1 = pd.read_excel(os.path.join(data_folder,'el_boilers_lukomol_2021.xlsx'), sheet_name='2')
data2 = pd.read_excel(os.path.join(data_folder,'el_boilers_lukomol_2021.xlsx'), sheet_name='3')

el_bolers_lukomol = data1['ЭК Лукомльская ГРЭС']
heat_lukomol = data2['Лукомольская грэс']
# 95

el_day = pd.DataFrame()

i = 0
el_data = []

step = 96
end= 0
length = len(el_bolers_lukomol)
while end < length:
    start = end
    end = start + step
    if end > length:
        break
    day_energy = sum(el_bolers_lukomol[start:end])
    el_data.append(day_energy)


el_day_df = pd.DataFrame(el_data)
el_day_df.columns = ['Электрокотлы']
hw_day_df = heat_lukomol[0:len(el_day_df)]
    

ax2 = hw_day_df.plot(kind="area", ylim=(0, 6000),  legend = 'reverse')
ax1 = el_day_df.plot(kind="line", ylim=(0, 6000), ax=ax2, color= 'black' ,  legend = 'reverse', title = 'Лукомольская ГРЭС - выработка тепла')


# ax1.set_ylabel("Мощность, МВт (э)")



plt.show()


print('')