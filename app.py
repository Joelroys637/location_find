import streamlit as st
import pydeck as pdk
from geopy.distance import geodesic

st.set_page_config(layout="wide", page_title="St.Joseph's College Campus 3D View")
st.markdown(
    """<center><h1 style="color:red;">St. Joseph's College - 3D Campus Navigator</h1></center>""",
    unsafe_allow_html=True
)

st.write("### Steps:")
st.write("1️⃣ Click on the map to select your start location.")
st.write("2️⃣ Choose your destination from the menu.")
st.write("3️⃣ Click **Find Destination** to draw your 3D path.")

# ---- Predefined Locations ----
locations = {
    "CS Department": (10.8291, 78.6916),
    "Library": (10.8285, 78.6908),
    "Main Gate": (10.8298, 78.6928),
    "Play Ground": (10.829873, 78.690455),
    "IT Department": (10.828345052338351, 78.69291733750346),
}

st.sidebar.header("Controls")

# ---- Search and Selection ----
query = st.sidebar.text_input("🔍 Search place (e.g. 'CS')", "")
suggestions = [loc for loc in locations if query.lower() in loc.lower()] if query else []

if suggestions:
    st.sidebar.write("Did you mean:")
    for s in suggestions:
        st.sidebar.write(f"- {s}")

selected_destination = st.sidebar.selectbox(
    "🎯 Select Destination",
    [""] + list(locations.keys()),
    index=0,
    format_func=lambda x: "Select destination" if x == "" else x
)

# ---- Initialize State ----
if "start_point" not in st.session_state:
    st.session_state.start_point = None
if "path_drawn" not in st.session_state:
    st.session_state.path_drawn = False

# ---- Map Settings ----
campus_center = [10.8293, 78.6919]
mapbox_token = "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndjJ6eGZ3N3gifQ._fPjv3ZJUw7Y5zDf9e5zZw"
# (You can replace this with your free Mapbox token)

# ---- Draw 3D Map ----
def create_3d_map(start_point=None, destination=None):
    layers = []

    # Add destination markers
    for name, coords in locations.items():
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=[{"name": name, "lat": coords[0], "lon": coords[1]}],
            get_position='[lon, lat]',
            get_color='[0, 255, 0, 160]',
            get_radius=5,
        ))

    # Start point marker
    if start_point:
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": start_point[0], "lon": start_point[1]}],
            get_position='[lon, lat]',
            get_color='[255, 0, 0, 200]',
            get_radius=10,
        ))

    # Path line
    if start_point and destination:
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": [ [start_point[1], start_point[0]], [destination[1], destination[0]] ]}],
            get_path="path",
            get_color=[0, 0, 255],
            width_scale=10,
            width_min_pixels=2,
        ))

        dist = geodesic(start_point, destination).meters
        st.sidebar.success(f"Path drawn to {selected_destination} ({dist:.2f} meters)")

    # 3D camera view
    view_state = pdk.ViewState(
        latitude=campus_center[0],
        longitude=campus_center[1],
        zoom=18,
        pitch=60,   # tilt for 3D
        bearing=30
    )

    # ✅ No mapbox_key or mapbox_api_key here
    return pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-streets-v12",
        initial_view_state=view_state,
        layers=layers
    )
# ---- User Interactions ----
if not st.session_state.path_drawn:
    st.info("🗺️ Click anywhere on the map to choose your start point.")
    st.session_state.start_point = (10.8295, 78.6915)  # Default

    if st.sidebar.button("Find Destination") and selected_destination:
        st.session_state.path_drawn = True
        st.rerun()

    st.pydeck_chart(create_3d_map(st.session_state.start_point))
else:
    dest_coords = locations[selected_destination]
    st.pydeck_chart(create_3d_map(st.session_state.start_point, dest_coords))

    if st.sidebar.button("🔄 Reset"):
        st.session_state.path_drawn = False
        st.session_state.start_point = None
        st.rerun()
