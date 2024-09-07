import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
from branca.colormap import linear

# Function to load the data
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to preprocess data
def preprocess_data(data, age_groups):
    if 'Year' not in data.columns:
        raise ValueError("The 'Year' column is missing from the data.")
    return data[['Year'] + age_groups]

# Function to create a Prophet forecast
def create_prophet_forecast(df, years_to_forecast):
    forecast_data = pd.DataFrame()
    models = {}
    for column in df.columns[1:]:
        prophet_df = df[['Year', column]].rename(columns={"Year": "ds", column: "y"})
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'].astype(str), format='%Y', errors='coerce')
        if prophet_df['ds'].isna().any():
            raise ValueError(f"Date conversion failed for column {column}. Check the 'Year' values.")
        model = Prophet(yearly_seasonality=True)
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=years_to_forecast, freq='Y')
        forecast = model.predict(future)
        forecast = forecast[['ds', 'yhat']].rename(columns={"yhat": f'yhat_{column}'})
        forecast_data = pd.concat([forecast_data, forecast.set_index('ds')], axis=1)
        models[column] = model

    forecast_data.reset_index(inplace=True)
    return forecast_data, models

# Function to create an ARIMA forecast
def create_arima_forecast(df, years_to_forecast):
    forecast_data = pd.DataFrame()
    models = {}
    for column in df.columns[1:]:
        series = df[column]
        model = ARIMA(series, order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=years_to_forecast)
        future_years = pd.date_range(start=str(df['Year'].max() + 1), periods=years_to_forecast, freq='Y')
        forecast_df = pd.DataFrame({'Year': future_years.year, f'yhat_{column}': forecast})
        forecast_data = pd.concat([forecast_data, forecast_df.set_index('Year')], axis=1)
        models[column] = model_fit

    forecast_data.reset_index(inplace=True)
    return forecast_data, models

# Function to calculate metrics
def calculate_metrics(true_values, forecasted_values):
    if len(true_values) != len(forecasted_values):
        min_len = min(len(true_values), len(forecasted_values))
        true_values = true_values[:min_len]
        forecasted_values = forecasted_values[:min_len]
    
    mae = mean_absolute_error(true_values, forecasted_values)
    mse = mean_squared_error(true_values, forecasted_values)
    rmse = math.sqrt(mse)
    return mae, mse, rmse

# Function to plot forecasts
def plot_forecasts(lga_data, prophet_forecast_data, arima_forecast_data, age_group):
    age_group_col = f'yhat_{age_group}'

    plt.figure(figsize=(14, 7))
    plt.plot(lga_data['Year'], lga_data[age_group], label='Historical Data', color='black')

    if age_group_col in prophet_forecast_data.columns:
        plt.plot(prophet_forecast_data['ds'], prophet_forecast_data[age_group_col], label='Prophet Forecast', color='blue', linestyle='--')

    if age_group_col in arima_forecast_data.columns:
        plt.plot(arima_forecast_data['Year'], arima_forecast_data[age_group_col], label='ARIMA Forecast', color='red', linestyle='--')

    plt.xlabel('Year')
    plt.ylabel('Population')
    plt.title(f'Forecast for Age Group: {age_group}')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)

    st.pyplot(plt)
    plt.close()

# Function to create a map with population density for a specific year
def create_map_with_population(coordinate_data, population_data, selected_year):
    # Merge datasets on LGA code
    merged_data = pd.merge(coordinate_data, population_data, left_on='LGA_CODE', right_on='LGA_CODE')

    # Filter data for the selected year
    filtered_data = merged_data[merged_data['Year'] == selected_year]

    # Initialize a Folium map
    m = folium.Map(location=[-37.8136, 144.9631], zoom_start=8)  # Centered on Melbourne

    # Create color map
    colormap = linear.PuBu_09.scale(filtered_data['Total Population'].min(), filtered_data['Total Population'].max())
    
    # Add markers with population data
    for _, row in filtered_data.iterrows():
        lat, lon = map(float, row['Geo Point'].split(','))
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=colormap(row['Total Population']),
            fill=True,
            fill_color=colormap(row['Total Population']),
            fill_opacity=0.6,
            popup=f"LGA Code: {row['LGA_CODE']}<br>Population: {row['Total Population']}<br>Suburb: {row['LGA']}"
        ).add_to(m)

    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 150px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; border-radius:10px;">
        <div style="padding: 10px;">
            <b>Population Density</b><br>
            <div style="display: flex;">
                <div style="width: 20px; height: 20px; background-color: #f7fbff;"></div> Low<br>
                <div style="width: 20px; height: 20px; background-color: #08306b;"></div> High
            </div>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# Main function for population forecasting
def run():
    st.title("Population Forecasting and Model Evaluation")

    # Load data
    data = load_data("Data/LGA_population_data.csv")
    st.write("LGA-wise Population Data", data.head())

    # Load coordinate data
    coordinate_data = load_data("Data/LGA_coordinates.csv")
    st.write("LGA Coordinates Data", coordinate_data.head())

    # Sidebar inputs
    years_to_forecast = st.sidebar.slider("Select Forecasting Horizon (years)", min_value=1, max_value=20, value=5, key='forecast_years')
    age_groups = st.sidebar.multiselect("Select Age Groups", options=data.columns[2:], default=["0-4", "20-24"], key='age_groups')
    lga = st.sidebar.selectbox("Select LGA", options=data['LGA'].unique(), key='lga_select')

    selected_year = st.sidebar.slider("Select Year", min_value=2001, max_value=2041, value=2021, key='selected_year')

    if st.sidebar.button("Generate Forecast"):
        st.write(f"Forecasting for {years_to_forecast} years...")

        lga_data = data[data['LGA'] == lga]
        prepared_data = preprocess_data(lga_data, age_groups)

        if prepared_data.empty:
            return

        prophet_forecast_data, prophet_model = create_prophet_forecast(prepared_data, years_to_forecast)
        st.write("**Prophet Model Forecast:**")
        st.write(prophet_forecast_data)

        arima_forecast_data, arima_model = create_arima_forecast(prepared_data, years_to_forecast)
        st.write("**ARIMA Model Forecast:**")
        st.write(arima_forecast_data)

        metrics_df = pd.DataFrame(columns=['Age Group', 'Model', 'MAE', 'MSE', 'RMSE'])

        for age_group in age_groups:
            true_values = prepared_data[age_group].values

            prophet_forecasted_values = prophet_forecast_data[f'yhat_{age_group}'].values[:len(true_values)]
            prophet_mae, prophet_mse, prophet_rmse = calculate_metrics(true_values, prophet_forecasted_values)
            metrics_df = pd.concat([metrics_df, pd.DataFrame({
                'Age Group': [age_group],
                'Model': ['Prophet'],
                'MAE': [prophet_mae],
                'MSE': [prophet_mse],
                'RMSE': [prophet_rmse]
            })], ignore_index=True)

            arima_forecasted_values = arima_forecast_data[f'yhat_{age_group}'].values[:len(true_values)]
            arima_mae, arima_mse, arima_rmse = calculate_metrics(true_values, arima_forecasted_values)
            metrics_df = pd.concat([metrics_df, pd.DataFrame({
                'Age Group': [age_group],
                'Model': ['ARIMA'],
                'MAE': [arima_mae],
                'MSE': [arima_mse],
                'RMSE': [arima_rmse]
            })], ignore_index=True)

        st.write("Model Evaluation Matrix:")
        st.dataframe(metrics_df)

        csv = metrics_df.to_csv(index=False)
        st.download_button(label="Download Evaluation Matrix as CSV", data=csv, file_name="model_evaluation_matrix.csv", mime="text/csv")

        st.write("**Forecast Plots:**")
        for age_group in age_groups:
            plot_forecasts(lga_data, prophet_forecast_data, arima_forecast_data, age_group)

        # Create map with population density for the selected year
        map_ = create_map_with_population(coordinate_data, data, selected_year)
        
        # Display map
        st.subheader("Population Density Map")
        st.components.v1.html(map_._repr_html_(), height=600)

if __name__ == "__main__":
    run()
