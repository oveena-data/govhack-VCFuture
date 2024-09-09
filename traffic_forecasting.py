import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import HeatMap
from branca.colormap import LinearColormap
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime
from shapely import wkt 

# Function to load traffic data from GeoJSON
@st.cache_data
def load_traffic_data(file_path):
    gdf = gpd.read_file(file_path)
    
    # Ensure the CRS is correct
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    
    # Drop rows where 'AADT_ALLVE' is NaN
    gdf = gdf.dropna(subset=['AADT_ALLVE'])
    
    # Ensure 'AADT_ALLVE' is numeric
    gdf['AADT_ALLVE'] = pd.to_numeric(gdf['AADT_ALLVE'], errors='coerce')
    
    return gdf

# Function to preprocess traffic data
def preprocess_traffic_data(data, selected_year):
    data = data.copy()
    
    # Filter data for the selected year
    filtered_data = data[data['LAST_YEAR'] == selected_year]
    
    if filtered_data.empty:
        st.warning("No data available for the selected year.")
        return None
    
    # Drop rows with NaN values in critical columns
    filtered_data.dropna(subset=['geometry', 'AADT_ALLVE'], inplace=True)
    
    return filtered_data

def create_traffic_map(traffic_data):
    # Initialize a Folium map centered on Victoria
    m = folium.Map(location=[-37.8136, 144.9631], zoom_start=8)
    
    # Define color scale for heatmap
    min_value = traffic_data['AADT_ALLVE'].min()
    max_value = traffic_data['AADT_ALLVE'].max()
    
    # Ensure the min and max values are in proper order
    colormap = LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=min_value, vmax=max_value)
    
    # Create heatmap
    heat_data = [[row.geometry.y, row.geometry.x, row['AADT_ALLVE']] for idx, row in traffic_data.iterrows()]
    
    HeatMap(
        heat_data,
        radius=15,
        blur=10,
        max_zoom=1,
        gradient={0.4: 'blue', 0.65: 'lime', 0.90: 'yellow', 1: 'red'}
    ).add_to(m)
    
    # Add colormap legend
    colormap.caption = 'AADT ALL VEHICLE'
    colormap.add_to(m)
    
    return m

# Function to forecast traffic data for each location
def forecast_traffic_data(data, forecast_years):
    # Group data by geometry
    grouped_data = data.groupby(data.geometry.apply(lambda geom: geom.wkt))
    
    forecasted_data = []
    
    for geom_wkt, group in grouped_data:
        # Prepare data for forecasting
        historical_data = group.groupby('LAST_YEAR')['AADT_ALLVE'].mean().reset_index()
        
        if len(historical_data) > 1:  # Ensure we have enough data points for regression
            # Create a linear regression model for forecasting
            model = LinearRegression()
            X = historical_data[['LAST_YEAR']]
            y = historical_data['AADT_ALLVE']
            model.fit(X, y)
            
            # Predict future values
            future_years = pd.DataFrame({'LAST_YEAR': forecast_years})
            future_data = future_years.copy()
            future_data['AADT_ALLVE'] = model.predict(future_years[['LAST_YEAR']])
            future_data['geometry'] = geom_wkt
            
            forecasted_data.append(future_data)
    
    if forecasted_data:
        forecasted_df = pd.concat(forecasted_data, ignore_index=True)
        forecasted_df['geometry'] = forecasted_df['geometry'].apply(wkt.loads)
        return gpd.GeoDataFrame(forecasted_df, geometry='geometry', crs=data.crs)
    else:
        return None

def run():
    st.title("Traffic Data Analysis and Visualization (1985-2041)")

    # Load data
    traffic_data = load_traffic_data("Data/Traffic Count Locations_ GeoJSON.geojson")

    st.write("Traffic Data Sample:", traffic_data[['geometry', 'LAST_YEAR', 'AADT_ALLVE']].head())

    # Sidebar inputs
    available_years = sorted(traffic_data['LAST_YEAR'].unique())
    min_year = int(min(available_years))
    max_year = int(max(available_years))
    
    # Extend years to include forecast period
    extended_years = list(range(min_year, 2042))
    selected_year = st.sidebar.slider("Select Year", min_value=min_year, max_value=2041, value=min_year, format="%d")

    if selected_year > max_year:
        forecast_years = list(range(max_year + 1, selected_year + 1))
        forecasted_data = forecast_traffic_data(traffic_data, forecast_years)
        
        if forecasted_data is not None:
            # Combine historical and forecasted data
            extended_traffic_data = pd.concat([traffic_data, forecasted_data], ignore_index=True)
            extended_traffic_data = gpd.GeoDataFrame(extended_traffic_data, geometry='geometry', crs=traffic_data.crs)
        else:
            st.warning("Unable to generate forecast. Using historical data only.")
            extended_traffic_data = traffic_data
    else:
        extended_traffic_data = traffic_data

    # Preprocess and filter traffic data for the selected year
    filtered_traffic_data = preprocess_traffic_data(extended_traffic_data, selected_year)
    
    if filtered_traffic_data is not None:
        # Create map with traffic data
        traffic_map = create_traffic_map(filtered_traffic_data)
        
        # Display map
        st.subheader(f"Traffic Heatmap for {selected_year}")
        st.components.v1.html(traffic_map._repr_html_(), height=600)
        
        # Display data summary
        st.subheader("Data Summary")
        summary = filtered_traffic_data[['LAST_YEAR', 'AADT_ALLVE']].describe()
        summary['LAST_YEAR'] = summary['LAST_YEAR'].apply(lambda x: f"{x:.1f}")
        st.write(summary)
        
        # Display top 10 busiest locations
        st.subheader(f"Top 10 Busiest Locations in {selected_year}")
        top_locations = filtered_traffic_data.nlargest(10, 'AADT_ALLVE')
        st.bar_chart(top_locations['AADT_ALLVE'])

if __name__ == "__main__":
    run()