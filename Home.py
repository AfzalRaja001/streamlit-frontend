import streamlit as st

st.set_page_config(
    page_title="Gurgaon Real Estate Analytics App",
    page_icon="👋",
    layout="wide"
)

st.title("🏘️ Gurgaon Real Estate Analytics App")
st.markdown("---")

st.markdown("""
### Welcome to the Real Estate Analytics Platform

This application provides comprehensive real estate analytics and predictions for Gurgaon properties.

#### 🎯 Features Available:

1. **💰 Price Predictor** - Get instant AI-powered property price predictions
2. **📊 Analytics Module** - Explore detailed market analytics and insights
3. **🏠 Recommend Apartments** - Find similar properties based on your preferences
4. **📈 Price Sensitivity** - Analyze how different features impact property prices

#### 🚀 Getting Started

Select any feature from the sidebar to begin your analysis.

#### ⚙️ Configuration

Make sure your FastAPI backend is running at: `https://real-estate-fastapi-latest.onrender.com`

To start the backend:
```bash
cd FastAPIs
uvicorn app:app --reload
```

""")

st.markdown("---")

# Quick stats from API
st.subheader("📊 Quick Stats")

import requests

import os
    
# Robust API URL loading
if "API_URL" in os.environ:
    API_URL = os.environ["API_URL"]
else:
    try:
        API_URL = st.secrets.get("API_URL", "https://real-estate-fastapi-latest.onrender.com")
    except Exception:
        API_URL = "https://real-estate-fastapi-latest.onrender.com"

try:
    # Try to get data from API
    response = requests.get(f"{API_URL}/healthz", timeout=2)
    if response.status_code == 200:
        st.success("✅ API Connected Successfully!")
        
        # Get properties count
        props_response = requests.get(f"{API_URL}/properties", timeout=2)
        if props_response.status_code == 200:
            props_data = props_response.json()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Properties", props_data.get('count', 0))
            with col2:
                sectors_response = requests.get(f"{API_URL}/sectors", timeout=2)
                if sectors_response.status_code == 200:
                    sectors_data = sectors_response.json()
                    st.metric("Available Sectors", sectors_data.get('count', 0))
            with col3:
                locations_response = requests.get(f"{API_URL}/locations", timeout=2)
                if locations_response.status_code == 200:
                    locations_data = locations_response.json()
                    st.metric("Searchable Locations", locations_data.get('count', 0))
    else:
        st.error("❌ Cannot connect to API. Please make sure the backend is running.")
except requests.exceptions.RequestException:
    st.warning("⚠️ API is not available. Please start the FastAPI backend.")
    st.code("cd FastAPIs\nuvicorn app:app --reload", language="bash")

