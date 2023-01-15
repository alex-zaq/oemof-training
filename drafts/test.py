import sys
sys.path.insert(0, './')
from collections import namedtuple
from custom_modules.helpers import *
# from wrapper_excel_operations import *
# group_options = namedtuple("group_options", "station_name turb_name")

step = 2.5
energy_list = [37.73 + i * step for i in range(10)]

for energy in energy_list:
    print(energy,'------',get_peak_load_by_energy_2020(energy))





# a = Custom_counter()

# a.popod = 'fsdaf'

# print(a.popod)

# def set_group(*items, separator = '_'):
#   return separator.join(items)


# print(set_group('aad', 'sasdf'))


# g = group_options("минская тэц-4","Т-250")

# print(g.station_name)


# reader = get_reader_by_folder('./drafts', '1.xlsx')

# res = reader('hw')[:24]


# print(res)




# def counter():
# 	i = 0
# 	while True:
# 		i+=1
# 		yield i
  
# a = counter()

# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))