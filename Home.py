import requests
import streamlit as st
from api_client import get_api_url, get_headers

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

st.subheader("📊 Quick Stats")

API_URL = get_api_url()
headers = get_headers()

try:
    response = requests.get(f"{API_URL}/healthz", timeout=2)
    if response.status_code == 200:
        st.success("✅ API Connected Successfully!")

        props_response = requests.get(f"{API_URL}/properties", headers=headers, timeout=2)
        if props_response.status_code == 200:
            props_data = props_response.json()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Properties", props_data.get("count", 0))
            with col2:
                sectors_response = requests.get(f"{API_URL}/sectors", headers=headers, timeout=2)
                if sectors_response.status_code == 200:
                    st.metric("Available Sectors", sectors_response.json().get("count", 0))
            with col3:
                locations_response = requests.get(f"{API_URL}/locations", headers=headers, timeout=2)
                if locations_response.status_code == 200:
                    st.metric("Searchable Locations", locations_response.json().get("count", 0))
    else:
        st.error("❌ Cannot connect to API. Please make sure the backend is running.")
except requests.exceptions.RequestException:
    st.warning("⚠️ API is not available. Please start the FastAPI backend.")
    st.code("cd FastAPIs\nuvicorn app:app --reload", language="bash")
