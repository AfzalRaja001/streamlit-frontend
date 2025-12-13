"""
API client utilities for making requests to FastAPI backend
"""
import requests
import streamlit as st
from typing import Optional, Dict, Any, List

# Default API URL
DEFAULT_API_URL = "https://real-estate-fastapi-latest.onrender.com"

import os

def get_api_url() -> str:
    """Get API URL from env vars (Docker) or secrets (Local)"""
    # 1. Check environment variable (Render/Docker)
    if "API_URL" in os.environ:
        return os.environ["API_URL"]
    
    # 2. Check Streamlit secrets (Local development)
    try:
        return st.secrets.get("API_URL", DEFAULT_API_URL)
    except Exception:
        # 3. Fallback
        return DEFAULT_API_URL

@st.cache_data(ttl=300)
def get_options() -> Optional[Dict[str, Any]]:
    """Get all dropdown options from API"""
    try:
        response = requests.get(f"{get_api_url()}/options", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching options: {e}")
        return None

@st.cache_data(ttl=300)
def get_properties() -> Optional[List[str]]:
    """Get list of all properties"""
    try:
        response = requests.get(f"{get_api_url()}/properties", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('properties', [])
        return None
    except Exception as e:
        st.error(f"Error fetching properties: {e}")
        return None

@st.cache_data(ttl=300)
def get_locations() -> Optional[List[str]]:
    """Get list of all searchable locations"""
    try:
        response = requests.get(f"{get_api_url()}/locations", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('locations', [])
        return None
    except Exception as e:
        st.error(f"Error fetching locations: {e}")
        return None

def predict_price(property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Predict property price"""
    try:
        response = requests.post(
            f"{get_api_url()}/predict-price",
            json=property_data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Prediction failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error predicting price: {e}")
        return None

def get_recommendations(
    property_name: str,
    top_n: int = 10,
    weight_facilities: float = 30.0,
    weight_price: float = 20.0,
    weight_location: float = 8.0
) -> Optional[Dict[str, Any]]:
    """Get property recommendations"""
    try:
        response = requests.post(
            f"{get_api_url()}/recommend",
            json={
                "property_name": property_name,
                "top_n": top_n,
                "weight_facilities": weight_facilities,
                "weight_price": weight_price,
                "weight_location": weight_location
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Recommendation failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return None

def search_by_location(location: str, radius_km: float) -> Optional[Dict[str, Any]]:
    """Search properties by location and radius"""
    try:
        response = requests.post(
            f"{get_api_url()}/search-by-location",
            json={
                "location": location,
                "radius_km": radius_km
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Location search failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error searching by location: {e}")
        return None

def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{get_api_url()}/healthz", timeout=2)
        return response.status_code == 200
    except:
        return False
