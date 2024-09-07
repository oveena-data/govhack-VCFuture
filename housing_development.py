import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
import geopandas as gpd
from shapely.geometry import shape
import json
from sklearn.linear_model import LinearRegression
import numpy as np

# Function to convert JSON geometry to Shapely shape
def json_to_geometry(json_str):
    try:
        geom = json.loads(json_str)
        return shape(geom)
    except Exception as e:
        st.error(f"Error parsing geometry: {e}")
        return None

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Data/housing_development.csv')
    df['geometry'] = df['geo_shape'].apply(json_to_geometry)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    return gdf

# Forecasting function
def forecast_development(gdf):
    years = np.arange(2012, 2020)
    forecasts = []

    for suburb in gdf['suburb'].unique():
        suburb_data = gdf[gdf['suburb'] == suburb]

        for attr in ['shape_area', 'dwelling_c']:
            if attr in suburb_data.columns:
                X = suburb_data['consyear'].values.reshape(-1, 1)
                y = suburb_data[attr].values

                model = LinearRegression()
                model.fit(X, y)
                future_years = np.arange(2020, 2041).reshape(-1, 1)
                future_values = model.predict(future_years)

                for year, value in zip(range(2020, 2041), future_values):
                    forecasts.append({
                        'suburb': suburb,
                        'year': year,
                        'forecasted_' + attr: value
                    })
            else:
                st.warning(f"Attribute {attr} not found in the dataset for suburb {suburb}.")

    return pd.DataFrame(forecasts)

def run():
    st.title("Housing Development Visualization and Forecasting")

    # Load data
    gdf = load_data()

    # Check if 'consyear' column exists
    if 'consyear' not in gdf.columns:
        st.error("The dataset does not contain 'consyear' column.")
        return

    # Sidebar for year selection
    year = st.sidebar.slider("Select Year", min_value=2012, max_value=2040, value=2018)

    if year <= 2019:
        filtered_gdf = gdf[gdf['consyear'] == year]
        forecast_data_available = False
    else:
        forecast_df = forecast_development(gdf)
        filtered_gdf = forecast_df[forecast_df['year'] == year]
        forecast_data_available = True

    # Initialize the map
    m = folium.Map(location=[-38.0, 144.0], zoom_start=10)

    if filtered_gdf.empty:
        st.warning(f"No data available for the year {year}.")
        return

    # Ensure 'suburb' column exists
    if 'suburb' not in filtered_gdf.columns:
        st.error("The dataset does not contain 'suburb' column.")
        return

    # Aggregate data by suburb
    aggregation_cols = ['forecasted_shape_area', 'forecasted_dwelling_c'] if forecast_data_available else ['shape_area', 'dwelling_c']
    
    aggregated_data = filtered_gdf.groupby('suburb').agg({
        col: 'sum' for col in aggregation_cols
    }).reset_index()

    # Prepare data for heatmap
    heat_data = []
    for _, row in aggregated_data.iterrows():
        suburb_geom = gdf[gdf['suburb'] == row['suburb']]['geometry']
        if not suburb_geom.empty:
            suburb_geom = suburb_geom.iloc[0]
            centroid = suburb_geom.centroid
            value_col = 'forecasted_shape_area' if forecast_data_available else 'shape_area'
            heat_data.append([centroid.y, centroid.x, row[value_col]])

    if heat_data:
        HeatMap(heat_data, radius=15, blur=10).add_to(m)
        st.subheader(f"Heatmap of Housing Developments for the Year {year}")
    else:
        st.warning(f"No heatmap data available for the year {year}.")

    # Add map to Streamlit
    st.components.v1.html(m._repr_html_(), height=600)
