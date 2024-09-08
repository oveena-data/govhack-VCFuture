import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load the data
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to preprocess data
def preprocess_data(data, selected_ages):
    # Melt the data to long format for easier plotting
    melted_data = pd.melt(data, id_vars=['Sex', 'Age'], var_name='Year', value_name='Population')
    
    # Convert 'Year' to numeric, coerce errors, and drop rows where conversion fails
    melted_data['Year'] = pd.to_numeric(melted_data['Year'], errors='coerce')
    melted_data = melted_data.dropna(subset=['Year'])
    
    # Convert 'Population' to numeric, removing any non-numeric characters
    melted_data['Population'] = pd.to_numeric(melted_data['Population'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
    
    # If selected_ages is not empty, filter and aggregate data
    if selected_ages:
        melted_data = melted_data[melted_data['Age'].isin(selected_ages)]
        
        # Group by Year and Sex and sum the populations for the selected ages
        aggregated_data = melted_data.groupby(['Sex', 'Year'])['Population'].sum().reset_index()
        return aggregated_data
    else:
        return melted_data

# Function to create interactive visualizations
def plot_interactive_visuals(data):
    # Streamlit UI elements
    st.sidebar.header("Filters")

    # Filter by Sex
    selected_sexes = st.sidebar.multiselect("Select Sex", options=data['Sex'].unique(), default=data['Sex'].unique())

    # Filter by Age
    selected_ages = st.sidebar.multiselect("Select Age", options=data['Age'].unique(), default=['20'])

    # Apply filters to the data
    filtered_data = data[data['Sex'].isin(selected_sexes)]
    processed_data = preprocess_data(filtered_data, selected_ages)

    # Display the filtered data
    st.write("Processed Data", processed_data.head())

    # Plot the line chart with the aggregated population values
    fig = px.line(processed_data, x='Year', y='Population', color='Sex', 
                  title=f"Population Trends Over Years (Ages: {', '.join(selected_ages)})", 
                  labels={'Population': 'Total Population Count'})
    
    st.plotly_chart(fig)

# Main function to run the Streamlit app
def run():
    st.title("Population Analysis")

    # Load and preprocess data
    data = load_data("Data/population_data.csv")
    
    # Create interactive visualizations
    plot_interactive_visuals(data)

if __name__ == "__main__":
    run()