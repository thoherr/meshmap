import os
import json
from types import SimpleNamespace
import folium

def get_node(node_list, node_id):
    for node in node_list:
        if node.id == node_id:
            return node
    return None

def node_tooltip(node):
    name = "{longName} ({shortName})".format(longName=node.longName, shortName=node.shortName)
    battery = " {batteryLevel}%".format(batteryLevel=node.batteryLevel) if node.batteryLevel else ""
    return name + battery

data_folder = 'data'
data_file_name = 'meshdata.json'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

data_file = os.path.join(data_folder, data_file_name)

mesh_data = json.load(open(data_file), object_hook=lambda d: SimpleNamespace(**d))

nodes = mesh_data.knownNodes

my_node_id = mesh_data.info.infoFrom
my_node = get_node(nodes, my_node_id)

meshmap = folium.Map(location=[my_node.lat, my_node.lon], zoom_start=12)

for node in nodes:
    if node.lat and node.lon:
        (folium.Marker(location=[node.lat, node.lon],
                       tooltip=node_tooltip(node),
                       icon=folium.Icon(icon='info-sign')).
         add_to(meshmap))

map_file_name = "meshmap.{short_name}.html".format(short_name=my_node.shortName)
map_file = os.path.join(output_folder, map_file_name)
meshmap.save(map_file)
