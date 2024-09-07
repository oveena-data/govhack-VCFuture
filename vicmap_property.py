import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Function to load the shapefile
def load_shapefile(file_path):
    try:
        gdf = gpd.read_file(file_path)
        st.write("Shapefile loaded successfully!")
        return gdf
    except Exception as e:
        st.error(f"Error loading shapefile: {e}")
        return None

# Function to simplify geometries
def simplify_geometries(gdf, tolerance=0.01):
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

# Function to create interactive visualizations
def plot_interactive_visuals(gdf):
    if gdf is None or gdf.empty:
        st.error("No data to display.")
        return

    st.title("Vicmap Property Visualization")

    # Display the GeoDataFrame
    st.write("Vicmap Property Data", gdf.head())

    # Simplify geometries to reduce data size
    gdf = simplify_geometries(gdf)

    # Ensure 'geometry' column is in the correct format
    gdf = gdf.to_crs(epsg=4326)  # Convert CRS to WGS84 (lat/lon)

    # Create a map visualization
    st.subheader("Map Visualization")

    # Convert GeoDataFrame to GeoJSON format
    try:
        geojson = gdf.to_json()
    except Exception as e:
        st.error(f"Error converting GeoDataFrame to GeoJSON: {e}")
        return

    # Create a Deck.gl map
    deck_map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=gdf.geometry.centroid.y.mean(),
            longitude=gdf.geometry.centroid.x.mean(),
            zoom=10,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                data=geojson,
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                extruded=False,
                line_width_min_pixels=1,
                get_line_color=[255, 0, 0],
                get_fill_color=[200, 200, 200],
                get_line_width=2,
            ),
        ],
    )

    st.pydeck_chart(deck_map)

    # Data insights
    st.subheader("Data Insights")

    # Display some basic statistics
    st.write("Basic Statistics:")
    st.write(gdf.describe(include='all'))

def run():
    st.title("Vicmap Property Data")

    # Load the shapefile data
    file_path = "/Users/Jasmin/Documents/GitHub/GovHack/Order_EJSMH3/ll_gda94/esrishape/lga_polygon/GREATER GEELONG-2000/VMPLAN/PLAN_ZONE_HISTORY.shp"
    data = load_shapefile(file_path)

    # Create interactive visualizations
    plot_interactive_visuals(data)

if __name__ == "__main__":
    run()
