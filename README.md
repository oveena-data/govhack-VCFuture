# VCFuture: Predictive Urban Planning for Victoria: AI-Driven Community Forecasting

## Project Description

### 🚨 Problem Statement

Victoria is the fastest-growing state in Australia, with a projected population of 10.3 million by 2051. The economy has surged by 9.1% in the past two years, and business investment has grown by 11.3%, significantly outpacing the national average. This rapid expansion, driven by population growth, overseas migration, and increased infrastructure demands, places immense pressure on housing, transportation, and public services.

To address these growing needs, we must transition from reactive to **predictive urban planning**. Our challenge is to forecast trends in population, housing demand, traffic patterns, and infrastructure development so that policymakers can make data-driven, forward-looking decisions.

---

## 🌐 Solution Overview

We developed a **web-based application** powered by **AI and Machine Learning** to help urban planners, policymakers, and community stakeholders anticipate community growth patterns across Victoria. This tool uses historical data from Victorian government sources to forecast key indicators like:

- Population growth
- Housing demand
- Vehicle registration trends
- Building permits
- Public service needs

It empowers users to simulate different urban planning scenarios and evaluate their long-term impact—laying the foundation for liveable, inclusive, and sustainable communities.

---

## Goals

1. **Historical Insight**: Use planning permit data to visualize historical growth and land-use patterns.
2. **Forecasting Future Demand**: Train AI models to predict future shifts in population, infrastructure, and public services.
3. **Scenario Visualizations**: Present predictive visualizations for stakeholders to experience potential urban futures.

---

## Mission

To enable Victoria to build **liveable, sustainable, and equitable communities** through AI-driven predictive modeling—helping planners learn from the past to shape the future.

---

## Data Story

Our analysis combines a diverse range of public datasets to build predictive models of urban dynamics:

### 📥 Data Sources

- **Traffic Count Locations (1985–2020)**: Identifying congestion hotspots across Victoria.
- **VIC LGA Administrative Boundaries**: For accurate mapping and regional analysis.
- **Vehicle Registrations (1900–2021)**: Assessing mobility trends over time.
- **Geelong Housing Development (2012–2019)**: Used as a proxy for forecasting due to availability.
- **Building Permits**: Cost estimations, type distributions, and growth analysis.
- **Population Datasets**: Granular insights by LGA, age, gender, and year.

### 🔧 Data Transformation

Raw data was cleaned, normalised, and merged across domains to form comprehensive and unified datasets. For instance, traffic flow data was combined with population density to visualise the correlation between urbanisation and congestion.

---

## Forecasting Techniques

We utilised the following forecasting models:

### 1. **ARIMA (AutoRegressive Integrated Moving Average)**

- Ideal for short-term, stationary time series forecasting.
- Equation: `ARIMA(p,d,q) = AR(p) + I(d) + MA(q)`

### 2. **Prophet**

- Built by Facebook, handles seasonality and holiday effects with minimal configuration.
- Suitable for non-stationary datasets with missing data.
- Equation: `y(t) = trend(t) + seasonality(t) + holidays(t) + ε(t)`

---

## Technical Stack

| Tool/Library | Purpose |
|--------------|---------|
| **Streamlit** | Web app interface |
| **Pandas & NumPy** | Data cleaning and manipulation |
| **Prophet** | Time series forecasting |
| **Statsmodels** | Statistical modeling |
| **Scikit-learn** | Machine learning and prediction |
| **Matplotlib & Seaborn** | Static visualisations |
| **Plotly** | Interactive data visuals |
| **Folium & Geopandas** | Geospatial analysis |
| **Shapely & Branca** | Map rendering and spatial data integration |

---

## Challenges

The greatest hurdle is the **limited availability of time-series, real-time datasets**, especially for traffic and housing trends. While historical permit data is rich, dynamic real-world changes are often not captured.

### 🛠️ Mitigation

We addressed this by:
- Leveraging available datasets like **Geelong housing** as a proof of concept.
- Designing a modular framework that can integrate future real-time data sources.
- Treating this as a **work-in-progress** with scalable potential.

---

## Strategic Deployment

Our application is designed to be **user-friendly and modular**, allowing city planners to simulate cause-and-effect dynamics in urban systems. The platform can plug into planning tools and help decision-makers gain foresight into urban challenges.

---

## ✅ Conclusion

By predicting community dynamics, this AI-powered tool equips Victoria with the insights needed for **sustainable growth**, **data-informed decisions**, and **resilient urban planning**. From identifying traffic hotspots to forecasting population booms, our project turns raw data into future-ready strategy.

> 🔗 **More Information & Project Space**:  
> Visit the GovHack Hackerspace → [https://hackerspace.govhack.org/projects/vcfuture](https://hackerspace.govhack.org/projects/vcfuture)

---

*Built with ❤️ by a passionate team of data scientists: Amish, Harsh, Tapan, Shefali, Sheikha & Oveena*

