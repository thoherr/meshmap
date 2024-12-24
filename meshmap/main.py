import os
import json
from types import SimpleNamespace
import folium
import datetime

now_in_seconds = int(datetime.datetime.now().timestamp())
fadeout = datetime.timedelta(hours=10).total_seconds()


def age_color(timestamp):
    opacity = int(100 * (fadeout - int(now_in_seconds - timestamp / 1000)) / fadeout)
    if opacity > 90:
        color = 'black'
    elif opacity > 80:
        color = 'gray'
    elif opacity > 60:
        color = 'cadetblue'
    elif opacity > 50:
        color = 'lightgray'
    elif opacity > 30:
        color = 'darkblue'
    elif opacity > 0:
        color = 'blue'
    else:
        return 'lightblue'
    return color



def get_node(node_list, node_id):
    for node in node_list:
        if node.id == node_id:
            return node
    return None


def node_tooltip(n):
    name = "{longName} ({shortName})".format(longName=n.longName, shortName=n.shortName)
    battery = " {batteryLevel}%".format(batteryLevel=n.batteryLevel) if n.batteryLevel else ""
    return name + battery


def add_node_to_map(mymap, node):
    if node.lat and node.lon:
        (folium.Marker(location=[node.lat, node.lon],
                       tooltip=node_tooltip(node),
                       icon=folium.Icon(icon='info-sign', color=age_color(node.lastHeard))).
         add_to(mymap))


def add_nodes_to_map(mymap, nodes):
    for node in nodes:
        add_node_to_map(mymap, node)


def get_links(meshdata):
    for route in meshdata.traceroutes:
        pass  # TODO: Implement
    return None


data_folder = 'data'
data_file_name = 'meshdata.json'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

data_file = os.path.join(data_folder, data_file_name)

mesh_data = json.load(open(data_file), object_hook=lambda d: SimpleNamespace(**d))

known_nodes = mesh_data.knownNodes

my_node_id = mesh_data.info.infoFrom
my_node = get_node(known_nodes, my_node_id)

meshmap = folium.Map(location=[my_node.lat, my_node.lon], zoom_start=12)

add_nodes_to_map(meshmap, known_nodes)

links = get_links(mesh_data)

map_file_name = "meshmap.{id}.html".format(id=my_node.id)
map_file = os.path.join(output_folder, map_file_name)
meshmap.save(map_file)
