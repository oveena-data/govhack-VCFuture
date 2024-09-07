import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_permit_data(file_path):
    permit_data = pd.read_csv(file_path)

    # Handle out-of-bounds dates and missing values
    for date_column in ['issue_date', 'commence_by_date', 'completed_by_date']:
        permit_data[date_column] = pd.to_datetime(permit_data[date_column], errors='coerce')
    
    # Drop rows with NaT values in critical date columns
    permit_data = permit_data.dropna(subset=['issue_date'])
    
    return permit_data

def visualize_data(df):
    # Plot 1: Estimated Cost of Works by Year
    fig, ax = plt.subplots(figsize=(12, 8))
    df['year'] = df['issue_date'].dt.year
    df.groupby('year')['estimated_cost_of_works'].sum().plot(kind='bar', ax=ax)
    ax.set_title('Estimated Cost of Works by Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Estimated Cost ($)')
    st.pyplot(fig)

    # Plot 2: Monthly Estimated Cost of Works
    df['month'] = df['issue_date'].dt.to_period('M').astype(str)
    monthly_cost = df.groupby('month')['estimated_cost_of_works'].sum()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    monthly_cost.plot(kind='line', marker='o', ax=ax, color='blue')
    ax.set_title('Monthly Estimated Cost of Works')
    ax.set_xlabel('Month')
    ax.set_ylabel('Estimated Cost ($)')
    
    # Rotate x-tick labels for better readability
    ax.set_xticks(range(0, len(monthly_cost), max(1, len(monthly_cost) // 12)))
    ax.set_xticklabels(monthly_cost.index[::max(1, len(monthly_cost) // 12)], rotation=45)
    
    st.pyplot(fig)

    # Plot 3: Permit Counts by Type
    permit_counts = df['permit_certificate_type'].value_counts()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    permit_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=sns.color_palette('Set2'))
    ax.set_title('Permit Counts by Type')
    
    # Remove labels to avoid clutter
    ax.set_ylabel('')
    
    st.pyplot(fig)

    # Plot 4: Distribution of Estimated Costs
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.histplot(df['estimated_cost_of_works'], bins=30, kde=True, ax=ax)
    ax.set_title('Distribution of Estimated Costs')
    ax.set_xlabel('Estimated Cost ($)')
    ax.set_ylabel('Frequency')
    
    # Optionally adjust x-ticks to avoid clutter
    ticks = ax.get_xticks()
    ax.set_xticks(ticks[::max(1, len(ticks) // 10)])
    
    st.pyplot(fig)

# Main function for the Building Permit Analysis page
def run():
    st.header("Building Permit Data Analysis")

    # Load data
    df = load_permit_data("data/building-permits.csv")
    st.write("Building Permit Data", df.head())

    # Data Preprocessing
    df['issue_date'] = pd.to_datetime(df['issue_date'])
    df['year'] = df['issue_date'].dt.year

    # Visualization
    st.write("**Estimated Cost of Works by Year:**")
    visualize_data(df)

    # Option to download the data as CSV
    csv = df.to_csv(index=False)
    st.download_button(label="Download Building Permits Data as CSV", data=csv, file_name="building_permits.csv", mime="text/csv")
