import streamlit as st
import pandas as pd
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# Function to load the data
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to preprocess data
def preprocess_data(data, selected_fuel_types):
    # Convert the year column to numeric
    data['NB_YEAR_MFC_VEH'] = pd.to_numeric(data['NB_YEAR_MFC_VEH'], errors='coerce')

    # Drop rows with missing or invalid years
    data = data.dropna(subset=['NB_YEAR_MFC_VEH'])
    
    # Filter data based on selected fuel types
    if selected_fuel_types:
        data = data[data['CD_CL_FUEL_ENG'].isin(selected_fuel_types)]
    
    # Exclude year 2024 if present
    data = data[data['NB_YEAR_MFC_VEH'] != 2024]
    
    # Group by Year and sum the total registrations
    aggregated_data = data.groupby('NB_YEAR_MFC_VEH')['TOTAL1'].sum().reset_index()
    
    # Rename columns for clarity
    aggregated_data.columns = ['Year', 'Total_Registrations']
    
    return aggregated_data

# Function to create interactive visualizations
def plot_interactive_visuals(data):
    # Streamlit UI elements
    st.title("Vehicle Registration Forecasting")
    
    # Display the data
    st.write("Aggregated Vehicle Registration Data", data)
    
    # Plot the line chart with the aggregated vehicle registrations
    fig = px.line(data, x='Year', y='Total_Registrations', 
                  title="Vehicle Registrations Over Years", 
                  labels={'Total_Registrations': 'Total Registrations'})
    
    # Set x-axis range to start from 1900
    fig.update_xaxes(range=[1900, data['Year'].max() + 5])
    
    st.plotly_chart(fig)
    
    # Forecasting
    st.subheader("Forecasting Future Vehicle Registrations")

    # Get the number of years to forecast from the user
    num_years = st.number_input("Number of Years to Forecast", min_value=1, max_value=20, value=10)

    # Prepare data for forecasting
    data = data.set_index('Year')
    model = ARIMA(data['Total_Registrations'], order=(5, 1, 0))  # Adjust the order as needed
    model_fit = model.fit()
    
    # Forecast the next years
    future_years = np.arange(data.index[-1] + 1, data.index[-1] + num_years + 1)
    forecast = model_fit.get_forecast(steps=num_years).predicted_mean
    
    # Create a DataFrame for future data
    future_data = pd.DataFrame({
        'Year': future_years,
        'Total_Registrations': np.nan,
        'Predicted_Registrations': forecast
    })

    # Combine past and forecasted data
    combined_data = pd.concat([data.reset_index(), future_data])
    
    # Plot both actual and forecasted values
    fig2 = px.line(combined_data, x='Year', y=['Total_Registrations', 'Predicted_Registrations'],
                   title="Actual and Forecasted Vehicle Registrations",
                   labels={'value': 'Registrations', 'variable': 'Type'})
    
    # Set x-axis range to start from 1900
    fig2.update_xaxes(range=[1900, combined_data['Year'].max() + 5])
    
    st.plotly_chart(fig2)
    
    # Calculate and display error metrics
    st.subheader("Model Evaluation")

    # Split the data into train and test sets
    train_data = data['Total_Registrations']
    test_data = data[-num_years:]
    
    # Forecast for the test period
    test_forecast = model_fit.get_forecast(steps=len(test_data)).predicted_mean
    
    # Calculate error metrics
    mse = mean_squared_error(test_data, test_forecast)
    mae = mean_absolute_error(test_data, test_forecast)
    
    st.write(f"Mean Squared Error (MSE): {mse:.2f}")
    st.write(f"Mean Absolute Error (MAE): {mae:.2f}")

    # Justification for Fuel Types
    st.subheader("Fuel Types Justification")
    
    fuel_types_justification = {
        'D': 'Diesel',
        'G': 'Gasoline',
        'O': 'Other',
        'M': 'Methanol',
        'P': 'Propane',
        'R': 'Electric',
        'S': 'Hybrid',
        'E': 'Ethanol'
    }
    
    st.write("Justification for Fuel Types:")
    for code, description in fuel_types_justification.items():
        st.write(f"{code}: {description}")

# Main function to run the Streamlit app
def run():
    st.title("Vehicle Registration Forecasting")

    # Load and preprocess data
    data = load_data("Data/vehicle_registration_data.csv")

    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # Filter by Fuel Type
    fuel_types = data['CD_CL_FUEL_ENG'].unique()
    selected_fuel_types = st.sidebar.multiselect("Select Fuel Types", options=fuel_types, default=fuel_types)

    # Preprocess data with selected filters
    processed_data = preprocess_data(data, selected_fuel_types)
    
    # Create interactive visualizations
    plot_interactive_visuals(processed_data)

if __name__ == "__main__":
    run()
