import streamlit as st

# Set the page configuration
st.set_page_config(page_title="Forecasting and Visualization", layout="wide")

# Main function
def main():
    st.sidebar.title("Navigation")
    options = st.sidebar.radio("Choose a page:", ["Population Forecasting", "Building Permit Analysis", "Population Analysis", "Vehicle Registration Forecasting", "Vicmap Property", "Housing Development"])

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
        
    elif options == "Vicmap Property":
        import vicmap_property
        vicmap_property.run()

    elif options == "Housing Development":
        import housing_development
        housing_development.run()

if __name__ == "__main__":
    main()
