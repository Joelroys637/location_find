import streamlit as st
from streamlit_folium import st_folium
import folium
import networkx as nx
from geopy.distance import geodesic

# ------------------ Streamlit Page Setup ------------------
st.set_page_config(layout="wide", page_title="Smart Campus Logical Path Navigator")

st.markdown(
    """<center><h1 style="color:red;">SJC Campus navigate system</h1></center>""",
    unsafe_allow_html=True
)

st.sidebar.header("Controls")
st.sidebar.write("Click anywhere on the map to select your start location.")

# ------------------ Predefined Locations ------------------
locations = {
    "CS Department": (10.8291, 78.6916),
    "Library": (10.8285, 78.6908),
    "Main Gate": (10.8298, 78.6928),
    "Play Ground": (10.829873, 78.690455),
    "IT Department": (10.828345052338351, 78.69291733750346),
    "Jubile hall":(10.829380, 78.689414),
}

# ------------------ Junction Points ------------------
junctions = {
    "J1": (10.829923, 78.692432),
    "J2": (10.830122, 78.691991),
    "J3": (10.829842, 78.692010),
    "J4": (10.829463, 78.691986),
    "J5": (10.829221, 78.691987),
    "J6": (10.828979, 78.691971),
    "J7": (10.828760, 78.691952),
    "J8": (10.828516, 78.691952),

    "J9":(10.828724, 78.691590),
    "J10":(10.828764, 78.690925),
    "J11":(10.829056, 78.691175),
    "J12":(10.829412, 78.691148),
    "J13":(10.829760, 78.691145),
    "J14":(10.830186, 78.691142),
    "J15":(10.830645, 78.691118),
    "J16":(10.828786, 78.690773),
    "J17":(10.828844, 78.690263),
    "J18":(10.828905, 78.689850),
    "J19":(10.829037, 78.689630),
    "J20":(10.829240, 78.689671),
    
}

# ------------------ Junction Connectivity ------------------
edges = [
    ("J1", "J2"), ("J2", "J3"), ("J3", "J4"), ("J4", "J5"),
    ("J5", "J6"), ("J6", "J7"), ("J7", "J8"), ("J8", "J9"),
    ("J9", "J10"), ("J10", "J16"),("J10","J11"), ("J11", "J12"), ("J12", "J13"),
    ("J13", "J14"), ("J14", "J15"), ("J15", "J16"), ("J16", "J17"),
    ("J17", "J18"), ("J18", "J19"), ("J19", "J20")
]

# ------------------ Build Graph ------------------
G = nx.Graph()
for j, coord in junctions.items():
    G.add_node(j, pos=coord)
for u, v in edges:
    G.add_edge(u, v, weight=geodesic(junctions[u], junctions[v]).meters)

# ------------------ Helper Functions ------------------
def nearest_junction(point):
    return min(junctions, key=lambda j: geodesic(point, junctions[j]).meters)

def create_map(start_point=None, destination=None, path_nodes=None, total_dist=None):
    m = folium.Map(location=[10.8293, 78.6919], zoom_start=18, tiles="Esri.WorldImagery")

    # Add markers
    for name, coords in locations.items():
        folium.Marker(coords, popup=name, icon=folium.Icon(color="green")).add_to(m)
    for j, coord in junctions.items():
        folium.CircleMarker(coord, radius=4, color="yellow", fill=True).add_to(m)

    if start_point:
        folium.Marker(start_point, popup="Start", icon=folium.Icon(color="red", icon="flag")).add_to(m)
    if destination:
        folium.Marker(destination, popup="Destination", icon=folium.Icon(color="blue", icon="star")).add_to(m)

    # Draw path
    if path_nodes:
        coords_list = [junctions[n] for n in path_nodes]
        if start_point:
            coords_list.insert(0, start_point)
        if destination:
            coords_list.append(destination)

        folium.PolyLine(coords_list, color="red", weight=5).add_to(m)

        if total_dist:
            mid_idx = len(coords_list) // 2
            folium.Marker(
                coords_list[mid_idx],
                popup=f"Total Distance: {total_dist:.2f} meters",
                icon=folium.Icon(color="purple", icon="info-sign")
            ).add_to(m)

    return m

# ------------------ Streamlit Logic ------------------
if "start_point" not in st.session_state:
    st.session_state.start_point = None
if "path_drawn" not in st.session_state:
    st.session_state.path_drawn = False

query = st.sidebar.text_input("🔍 Type place name", "")
suggestions = [loc for loc in locations if query.lower() in loc.lower()] if query else []
if suggestions:
    st.sidebar.write("Did you mean:")
    for s in suggestions:
        st.sidebar.write(f"- {s}")

selected_destination = st.sidebar.selectbox(
    "Select your destination",
    [""] + list(locations.keys()),
    index=0,
    format_func=lambda x: "Select destination" if x == "" else x
)

#-----------destination


# ------------------ Main Path Logic ------------------
if not st.session_state.path_drawn:
    map_data = st_folium(create_map(), width=850, height=500)

    if map_data and map_data["last_clicked"]:
        st.session_state.start_point = (
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"]
        )
        st.sidebar.write(f"✅ Start Point: {st.session_state.start_point}")

    if st.sidebar.button("Show Logical Path") and selected_destination and st.session_state.start_point:
        
        
        dest_coords = locations[selected_destination]

        start_j = nearest_junction(st.session_state.start_point)
        dest_j = nearest_junction(dest_coords)

        # Get path that follows logical connection order (not shortest)
        path_nodes = nx.shortest_path(G, start_j, dest_j)
        total_dist = sum(
            geodesic(junctions[path_nodes[i]], junctions[path_nodes[i+1]]).meters
            for i in range(len(path_nodes)-1)
        )

        st.session_state.path_drawn = True
        st.session_state.path_nodes = path_nodes
        st.session_state.destination = dest_coords
        st.session_state.total_dist = total_dist
        
        st.sidebar.success(f"✅ Path drawn logically ({total_dist:.2f} meters)")
        st.rerun()
        text = f"Welcome to SJC! Your destination is {selected_destination}. The path is shown on the map. Thank you for visiting SJC."
        rate = 0.9
        pitch = 1.0

        st.components.v1.html(f"""
            <script>
            var msg = new SpeechSynthesisUtterance("{text}");
            msg.rate = {rate};
            msg.pitch = {pitch};
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

else:
    dest_coords = st.session_state.destination
    path_nodes = st.session_state.path_nodes
    total_dist = st.session_state.total_dist

    path_map = create_map(st.session_state.start_point, dest_coords, path_nodes, total_dist)
    st_folium(path_map, width=850, height=500)

    if st.sidebar.button("🔄 Reset"):
        st.session_state.start_point = None
        st.session_state.path_drawn = False
        st.session_state.destination = None
        st.session_state.path_nodes = None
        st.session_state.total_dist = None
        st.rerun()
