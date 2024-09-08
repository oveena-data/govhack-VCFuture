import streamlit as st

# Set the page configuration
st.set_page_config(page_title="Forecasting and Visualization", layout="wide")

# Main function
def main():
    st.sidebar.title("Navigation")
    options = st.sidebar.radio("Choose a page:", [
        "Population Forecasting", 
        "Building Permit Analysis", 
        "Population Analysis", 
        "Vehicle Registration Forecasting", 
        "Housing Development",
        "Traffic Forecasting"  # New Page Option
    ])

    if options == "Population Forecasting":
        import population_forecasting
        population_forecasting.run()

    elif options == "Building Permit Analysis":
        import building_permit_analysis
        building_permit_analysis.run()

    elif options == "Population Analysis":
        import population_analysis
        population_analysis.run()
    
    elif options == "Vehicle Registration Forecasting":
        import vehicle_forecasting
        vehicle_forecasting.run()

    elif options == "Housing Development":
        import housing_development
        housing_development.run()
    
    elif options == "Traffic Forecasting":  
        import traffic_forecasting
        traffic_forecasting.run()  # Use the correct function name

if __name__ == "__main__":
    main()
