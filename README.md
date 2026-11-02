# VitalClusters

VitalClusters automatically groups communities by health risk profile so public health teams can see who needs help first and why.

## Inspiration

Health risks are not distributed evenly across a country, leaving different regions with different needs. However, survey data is typically delivered in massive tables that require domain expertise to interpret. VitalClusters translates complex demographic and health survey data into accessible population profiles.

## What it does

VitalClusters takes demographic and health survey data and automatically:

- Filters and handles missing values and mixed data types.
- Finds the optimal number of clusters automatically.
- Groups populations into distinct health risk profiles.
- Explains each cluster in plain language, detailing key drivers.
- Displays results on an interactive Streamlit dashboard.

## How I built it

- **Pipeline & Clustering:** Python, scikit-learn (K-Means, Silhouette analysis, PCA).
- **Visualization:** Plotly, Streamlit.
