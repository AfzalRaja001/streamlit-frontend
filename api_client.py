"""
API client utilities for making requests to the FastAPI backend.
"""
import os
import requests
import streamlit as st
from typing import Optional, Dict, Any, List

DEFAULT_API_URL = "https://real-estate-fastapi-latest.onrender.com"

def get_api_url() -> str:
    """Resolve the backend URL from env var (Render/Docker) then Streamlit secrets."""
    if "API_URL" in os.environ:
        return os.environ["API_URL"]
    try:
        return st.secrets.get("API_URL", DEFAULT_API_URL)
    except Exception:
        return DEFAULT_API_URL

def get_headers() -> Dict[str, str]:
    """
    Return auth headers if an API key is configured.
    When API_KEY is absent (local dev without auth), returns an empty dict
    so all existing requests continue to work unchanged.
    """
    api_key = ""
    if "API_KEY" in os.environ:
        api_key = os.environ["API_KEY"]
    else:
        try:
            api_key = st.secrets.get("API_KEY", "")
        except Exception:
            pass
    if api_key:
        return {"X-API-Key": api_key}
    return {}

@st.cache_data(ttl=300)
def get_options() -> Optional[Dict[str, Any]]:
    """Get all dropdown options from the API."""
    try:
        response = requests.get(
            f"{get_api_url()}/options",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching options: {e}")
        return None

@st.cache_data(ttl=300)
def get_properties() -> Optional[List[str]]:
    """Get list of all properties."""
    try:
        response = requests.get(
            f"{get_api_url()}/properties",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("properties", [])
        return None
    except Exception as e:
        st.error(f"Error fetching properties: {e}")
        return None

@st.cache_data(ttl=300)
def get_locations() -> Optional[List[str]]:
    """Get list of all searchable locations."""
    try:
        response = requests.get(
            f"{get_api_url()}/locations",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("locations", [])
        return None
    except Exception as e:
        st.error(f"Error fetching locations: {e}")
        return None

def predict_price(property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Predict property price."""
    try:
        response = requests.post(
            f"{get_api_url()}/predict-price",
            json=property_data,
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
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
    weight_location: float = 8.0,
) -> Optional[Dict[str, Any]]:
    """Get property recommendations."""
    try:
        response = requests.post(
            f"{get_api_url()}/recommend",
            json={
                "property_name": property_name,
                "top_n": top_n,
                "weight_facilities": weight_facilities,
                "weight_price": weight_price,
                "weight_location": weight_location,
            },
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"Recommendation failed: {response.text}")
        return None
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return None

def search_by_location(location: str, radius_km: float) -> Optional[Dict[str, Any]]:
    """Search properties by location and radius."""
    try:
        response = requests.post(
            f"{get_api_url()}/search-by-location",
            json={"location": location, "radius_km": radius_km},
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"Location search failed: {response.text}")
        return None
    except Exception as e:
        st.error(f"Error searching by location: {e}")
        return None

@st.cache_data(ttl=600)
def get_analytics_data() -> Optional[List[Dict[str, Any]]]:
    """
    Fetch the full visualization dataset from the API (backed by PostgreSQL).
    Returns None when the endpoint is unavailable (503 = DATABASE_URL not set
    on the backend) so the caller can fall back to the local bundled CSV.
    Cached for 10 minutes to avoid re-fetching on every page interaction.
    """
    try:
        response = requests.get(
            f"{get_api_url()}/analytics/data",
            headers=get_headers(),
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def check_api_health() -> bool:
    """Check if the API is reachable. Does NOT require auth (/healthz is open)."""
    try:
        response = requests.get(f"{get_api_url()}/healthz", timeout=2)
        return response.status_code == 200
    except Exception:
        return False
