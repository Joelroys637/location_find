import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.distance import geodesic



st.set_page_config(layout="wide", page_title="3D Campus Navigator")
st.markdown("""<center><h1 style="color:red;">Details for Finding the places</h1></center>""",unsafe_allow_html=True)
st.write("steps:")
st.write("1)Select the map where you are in the college")
st.write("2)Go to the menu bar top of left side")
st.write("3)Select your destination or type your destination")
st.write("4)click Find Destination button")
st.sidebar.header("Controls")
st.sidebar.write("Click on the map to select your start location.")

# ---- Predefined Locations ----
locations = {
    "CS Department": (10.8291, 78.6916),
    "Library": (10.8285, 78.6908),
    "Main Gate": (10.8298, 78.6928),
    "Play Ground": (10.829873, 78.690455),
    "IT Department": (10.828345052338351, 78.69291733750346),
}

# ---- Autocomplete Search Box ----
query = st.sidebar.text_input("🔍 Type place name (e.g. 'CS')", "")
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

# ---- Initialize Session State ----
if "start_point" not in st.session_state:
    st.session_state.start_point = None
if "path_drawn" not in st.session_state:
    st.session_state.path_drawn = False

# ---- Function to Create Map ----
def create_map(start_point=None, destination=None):
    campus_center = [10.8293, 78.6919]
    m = folium.Map(location=campus_center, zoom_start=18, tiles="Esri.WorldImagery")

    for name, coords in locations.items():
        folium.Marker(
            coords,
            popup=name,
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m)

    # Add start point if available
    if start_point:
        folium.Marker(
            start_point,
            popup="Start Point",
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(m)

    # Draw path if both selected
    if start_point and destination:
        folium.PolyLine([start_point, destination], color="blue", weight=3.5).add_to(m)
        dist = geodesic(start_point, destination).meters
        st.sidebar.success(f"Path drawn to {selected_destination} ({dist:.2f} meters)")
        st.session_state.path_drawn = True

    return m

# ---- Map Interaction ----
if not st.session_state.path_drawn:
    st.sidebar.write("🗺️ Click on the map to select your start location.")

    campus_map = create_map()
    map_data = st_folium(campus_map, width=850, height=500)

    if map_data and map_data["last_clicked"]:
        st.session_state.start_point = (
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"]
        )
        st.sidebar.write(f"✅ Start Point: {st.session_state.start_point}")

    if st.sidebar.button("Find Destination") and selected_destination and st.session_state.start_point:
        dest_coords = locations[selected_destination]
        st.session_state.path_drawn = True
        st.rerun()

# ---- Show Only the Path Map ----
else:
    dest_coords = locations[selected_destination]
    path_map = create_map(st.session_state.start_point, dest_coords)
    st_folium(path_map, width=850, height=500)

    if st.sidebar.button("🔄 Reset"):
        st.session_state.start_point = None
        st.session_state.path_drawn = False
        st.rerun()
