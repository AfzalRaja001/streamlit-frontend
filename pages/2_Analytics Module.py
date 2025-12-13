import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import check_api_health

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Check API (optional for analytics)
api_status = check_api_health()
if not api_status:
    st.warning("⚠️ API is offline. Analytics will use cached data only.")

st.title('🏘️ Real Estate Analytics Dashboard')

# Load data from the Streamlit app folder (analytics uses historical data)
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'data_viz1.csv')

try:
    new_df = pd.read_csv(data_path)
except:
    st.error("❌ Cannot load analytics data. Please ensure data files are available.")
    st.stop()

# Sidebar filters
st.sidebar.header('Filters')
selected_property_type = st.sidebar.multiselect(
    'Property Type',
    options=new_df['property_type'].unique(),
    default=new_df['property_type'].unique()
)
price_range = st.sidebar.slider(
    'Price Range (Cr)',
    float(new_df['price'].min()),
    float(new_df['price'].max()),
    (float(new_df['price'].min()), float(new_df['price'].max()))
)

# Filter data
filtered_df = new_df[
    (new_df['property_type'].isin(selected_property_type)) &
    (new_df['price'].between(price_range[0], price_range[1]))
]

# KPI Metrics
st.header('📊 Key Metrics')
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Properties", len(filtered_df))
with col2:
    st.metric("Avg Price", f"₹{filtered_df['price'].mean():.2f} Cr")
with col3:
    st.metric("Avg Price/Sqft", f"₹{filtered_df['price_per_sqft'].mean():.0f}")
with col4:
    st.metric("Avg Area", f"{filtered_df['built_up_area'].mean():.0f} sqft")

# Geomap
group_df = filtered_df.groupby('sector').mean(numeric_only=True)[
    ['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']
]

st.header('🗺️ Sector Price per Sqft Geomap')
fig = px.scatter_mapbox(
    group_df,
    lat="latitude",
    lon="longitude",
    color="price_per_sqft",
    size='built_up_area',
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=10,
    mapbox_style="open-street-map",
    width=1200,
    height=700,
    hover_name=group_df.index
)
st.plotly_chart(fig, use_container_width=True)

# Top 10 Most Expensive Sectors
st.header('💰 Top 10 Most Expensive Sectors')
top_sectors = filtered_df.groupby('sector')['price_per_sqft'].mean().sort_values(ascending=False).head(10)
fig_top = px.bar(
    top_sectors,
    x=top_sectors.values,
    y=top_sectors.index,
    orientation='h',
    labels={'x': 'Avg Price per Sqft (₹)', 'y': 'Sector'},
    color=top_sectors.values,
    color_continuous_scale='Reds'
)
st.plotly_chart(fig_top, use_container_width=True)

# Price Distribution by BHK
st.header('🏠 Price Distribution by BHK Configuration')
col1, col2 = st.columns(2)
with col1:
    fig_bhk_box = px.box(
        filtered_df[filtered_df['bedRoom'] <= 5],
        x='bedRoom',
        y='price',
        color='property_type',
        title='Price Range by BHK'
    )
    st.plotly_chart(fig_bhk_box, use_container_width=True)
with col2:
    fig_bhk_violin = px.violin(
        filtered_df[filtered_df['bedRoom'] <= 5],
        x='bedRoom',
        y='price_per_sqft',
        color='property_type',
        title='Price/Sqft Distribution by BHK',
        box=True
    )
    st.plotly_chart(fig_bhk_violin, use_container_width=True)

# Property Age Analysis
st.header('📅 Property Age vs Price Analysis')
age_price = filtered_df.groupby('agePossession').agg({
    'price': 'mean',
    'price_per_sqft': 'mean',
    'property_type': 'count'
}).rename(columns={'property_type': 'count'}).sort_values('price', ascending=False).head(10)

fig_age = go.Figure()
fig_age.add_trace(go.Bar(
    x=age_price.index,
    y=age_price['price'],
    name='Avg Price (Cr)',
    yaxis='y'
))
fig_age.add_trace(go.Scatter(
    x=age_price.index,
    y=age_price['price_per_sqft'],
    name='Avg Price/Sqft',
    yaxis='y2',
    mode='lines+markers'
))
fig_age.update_layout(
    title='Price Comparison by Property Age',
    yaxis=dict(title='Avg Price (Cr)'),
    yaxis2=dict(title='Avg Price/Sqft', overlaying='y', side='right'),
    hovermode='x unified'
)
st.plotly_chart(fig_age, use_container_width=True)

# Furnishing Analysis
st.header('🛋️ Furnishing Type Impact on Price')
col1, col2 = st.columns(2)
with col1:
    furnish_stats = filtered_df.groupby('furnishing_type')['price'].mean().sort_values(ascending=False)
    fig_furnish = px.bar(
        furnish_stats,
        x=furnish_stats.index,
        y=furnish_stats.values,
        labels={'x': 'Furnishing Type', 'y': 'Avg Price (Cr)'},
        color=furnish_stats.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_furnish, use_container_width=True)
with col2:
    furnish_count = filtered_df['furnishing_type'].value_counts()
    fig_furnish_pie = px.pie(
        values=furnish_count.values,
        names=furnish_count.index,
        title='Distribution of Furnishing Types'
    )
    st.plotly_chart(fig_furnish_pie, use_container_width=True)

# Area vs Price Scatter
st.header('📈 Area vs Price Relationship')
property_type_select = st.selectbox(
    'Select Property Type',
    ['flat', 'house', 'both'],
    key='area_price'
)

if property_type_select == 'both':
    plot_df = filtered_df
else:
    plot_df = filtered_df[filtered_df['property_type'] == property_type_select]

fig_scatter = px.scatter(
    plot_df,
    x="built_up_area",
    y="price",
    color="bedRoom",
    size="price_per_sqft",
    hover_data=['sector'],
    title="Area vs Price with BHK Classification",
    trendline="ols",
    trendline_scope="overall"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Price Heatmap
st.header('🔥 Price Heatmap: BHK vs Top Sectors')
top_20_sectors = filtered_df.groupby('sector')['price'].mean().sort_values(ascending=False).head(20).index
heatmap_data = filtered_df[filtered_df['sector'].isin(top_20_sectors)].pivot_table(
    values='price_per_sqft',
    index='sector',
    columns='bedRoom',
    aggfunc='mean'
)
fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="BHK", y="Sector", color="Price/Sqft"),
    title="Average Price per Sqft by Sector and BHK",
    color_continuous_scale='RdYlGn_r'
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Sector Analysis
st.header('📍 Sector-wise Analysis')
sector_analysis = filtered_df.groupby('sector').agg({
    'price': 'mean',
    'price_per_sqft': 'mean',
    'property_type': 'count'
}).rename(columns={'property_type': 'property_count'}).sort_values('property_count', ascending=False).head(15)

fig_sector = go.Figure()
fig_sector.add_trace(go.Bar(
    x=sector_analysis.index,
    y=sector_analysis['property_count'],
    name='Property Count',
    yaxis='y'
))
fig_sector.add_trace(go.Scatter(
    x=sector_analysis.index,
    y=sector_analysis['price'],
    name='Avg Price',
    yaxis='y2',
    mode='lines+markers'
))
fig_sector.update_layout(
    title='Top 15 Sectors: Property Count vs Average Price',
    yaxis=dict(title='Property Count'),
    yaxis2=dict(title='Avg Price (Cr)', overlaying='y', side='right'),
    hovermode='x unified'
)
st.plotly_chart(fig_sector, use_container_width=True)

# BHK Distribution
st.header('🏠 BHK Distribution')
sector_options = ['overall'] + filtered_df['sector'].unique().tolist()
selected_sector = st.selectbox('Select Sector', sector_options)

if selected_sector == 'overall':
    fig_bhk_pie = px.pie(filtered_df, names='bedRoom', title='Overall BHK Distribution')
else:
    fig_bhk_pie = px.pie(
        filtered_df[filtered_df['sector'] == selected_sector],
        names='bedRoom',
        title=f'BHK Distribution in {selected_sector}'
    )
st.plotly_chart(fig_bhk_pie, use_container_width=True)

# Property Type Comparison
st.header('🏘️ Flat vs House Comparison')
comparison_df = filtered_df.groupby('property_type').agg({
    'price': ['mean', 'median', 'min', 'max'],
    'price_per_sqft': 'mean',
    'built_up_area': 'mean',
    'bedRoom': 'mean',
    'bathroom': 'mean'
}).round(2)
st.dataframe(comparison_df, use_container_width=True)

st.info("📊 All analytics are computed from historical data for fast visualization.")
