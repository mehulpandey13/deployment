import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import networkx as nx
import osmnx as ox
import folium
import math
from streamlit_folium import folium_static

def calculate_distance(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

# Load the road network for a given place
@st.cache
def load_road_network(place_name):
    G = ox.graph_from_place(place_name, network_type='all')
    nodes, edges = ox.graph_to_gdfs(G)
    return G, nodes, edges

# Placeholder function to detect road conditions
def detect_road_conditions(roads):
    roads['condition'] = ['good' if i % 2 == 0 else 'poor' for i in range(len(roads))]
    return roads

# Function to visualize road network with Folium
def plot_road_network_folium(roads, place_name):
    center_coords = ox.geocode(place_name)
    m = folium.Map(location=center_coords, zoom_start=12)
    for _, road in roads.iterrows():
        coords = [(point[1], point[0]) for point in road['geometry'].coords]
        if road['condition'] == 'good':
            color = 'green'
        else:
            color = 'red'
        folium.PolyLine(coords, color=color, weight=2.5).add_to(m)
    return m

# Load data
st.title("Road Network Analysis Dashboard")

place_name = st.text_input("Enter the place name:", "Durg, Chhattisgarh, India")

if place_name:
    # Load the road network data
    G, nodes, edges = load_road_network(place_name)
    
    st.subheader(f"Road Network of {place_name}")
    # Display basic information
    st.write(f"Total number of roads: {edges.shape[0]}")
    
    # Detect road conditions
    edges = detect_road_conditions(edges)
    
    # Calculate and display road condition statistics
    num_good_condition = edges[edges['condition'] == 'good'].shape[0]
    num_poor_condition = edges[edges['condition'] == 'poor'].shape[0]
    
    st.subheader("Road Condition Statistics")
    st.write(f"Number of roads in good condition: {num_good_condition}")
    st.write(f"Number of roads in poor condition: {num_poor_condition}")
    
    # Filter for one-way and poor condition roads
    oneway_poor_condition_roads = edges[(edges['oneway'] == True) & (edges['condition'] == 'poor')]
    
    # Visualize road network using folium
    st.subheader("Visualizing Road Network with Conditions")
    map_road_network = plot_road_network_folium(edges, place_name)
    folium_static(map_road_network)

    # Identify dead-end and isolated nodes
    degrees = dict(G.degree())
    dead_end_nodes = [node for node, degree in degrees.items() if degree == 1]
    isolated_nodes = [node for node, degree in degrees.items() if degree == 0]
    
    st.subheader("Node Statistics")
    st.write(f"Number of dead-end nodes: {len(dead_end_nodes)}")
    st.write(f"Number of isolated nodes: {len(isolated_nodes)}")
    
    # Display dead-end and isolated nodes
    if len(dead_end_nodes) > 0:
        st.write("Dead-end nodes:", dead_end_nodes)
    if len(isolated_nodes) > 0:
        st.write("Isolated nodes:", isolated_nodes)
