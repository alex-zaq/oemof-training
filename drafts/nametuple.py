from collections import namedtuple

group_options = namedtuple("group_options", "station_name turb_name")

g = group_options("минская тэц-4","Т-250")

print(g.station_name)