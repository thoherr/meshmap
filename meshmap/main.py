import os
import json
from types import SimpleNamespace
import folium
import datetime

now_in_seconds = int(datetime.datetime.now().timestamp())
fadeout_interval_seconds = datetime.timedelta(hours=18).total_seconds()
traceroute_interval_seconds = datetime.timedelta(hours=18).total_seconds()
age_thresholds_percent_of_interval = [0, 30, 50, 65, 80, 90, 100]


def age_group(timestamp, interval):
    value = int(100 * (interval - int(now_in_seconds - timestamp / 1000)) / interval)
    for i, t in enumerate(age_thresholds_percent_of_interval):
        if value <= t:
            return i


def age_color(timestamp, interval):
    return ['lightblue', 'blue', 'darkblue',
            'lightgray', 'cadetblue', 'gray', 'black'][age_group(timestamp, interval)]


def get_node(node_list, node_id):
    for node in node_list:
        if node.id == node_id:
            return node
    return None


def node_tooltip(n):
    name = "{longName} ({shortName})".format(longName=n.longName, shortName=n.shortName)
    battery = " {batteryLevel}%".format(batteryLevel=n.batteryLevel) if n.batteryLevel else ""
    lastHeard = "<br/>{lastHeard}".format(lastHeard=datetime.datetime.fromtimestamp(int(n.lastHeard / 1000)))
    return name + battery + lastHeard


def node_location(node):
    return [node.lat, node.lon]


def add_node_to_map(mymap, node):
    if node.lat and node.lon:
        (folium.Marker(location=node_location(node),
                       tooltip=node_tooltip(node),
                       icon=folium.Icon(icon='info-sign', color=age_color(node.lastHeard, fadeout_interval_seconds))).
         add_to(mymap))


def add_nodes_to_map(mymap, nodes):
    for node in nodes:
        add_node_to_map(mymap, node)


def add_route_to_map(mymap, nodes, timestamp, route):
    coords = [ c for c in list(map(lambda n: node_location(get_node(nodes, n)), route)) if c != [None, None] ]
    color = age_color(timestamp, traceroute_interval_seconds)
    tooltip = "{route}<br/>{timestamp}".format(route=route, timestamp=datetime.datetime.fromtimestamp(int(timestamp / 1000)))
    folium.PolyLine(coords, tooltip=tooltip, smooth_factor=0.5, color=color).add_to(mymap)


def add_routes_to_map(mymap, nodes, traceroutes):
    for traceroute in traceroutes:
        add_route_to_map(mymap, nodes, traceroute.timeStamp, traceroute.nodeTraceTo)
        add_route_to_map(mymap, nodes, traceroute.timeStamp, traceroute.nodeTraceFrom)


def get_latest_trace(route):
    timestamp = 0
    latest_trace = None
    for trace in route.traces:
        if trace.timeStamp > timestamp:
            latest_trace = trace
            timestamp = latest_trace.timeStamp
    return latest_trace


def get_latest_traceroutes(meshdata):
    traceroutes = []
    for route in meshdata.traceroutes:
        trace = get_latest_trace(route)
        if trace:
            traceroutes.append(trace)
    return traceroutes


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

traceroutes = get_latest_traceroutes(mesh_data)
add_routes_to_map(meshmap, known_nodes, traceroutes)

map_file_name = "meshmap.{id}.html".format(id=my_node.id)
map_file = os.path.join(output_folder, map_file_name)
meshmap.save(map_file)
