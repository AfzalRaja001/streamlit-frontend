import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import (
    get_properties,
    get_locations,
    get_recommendations,
    search_by_location,
    check_api_health
)

st.set_page_config(page_title="Recommend Apartments", layout="wide")

# Check API health
if not check_api_health():
    st.error("🚨 Cannot connect to API backend. Please ensure the FastAPI server is running.")
    st.code("cd FastAPIs\nuvicorn app:app --reload", language="bash")
    st.stop()

st.title('🏘️ Recommend Apartments')
st.markdown("Find similar properties or search by location using our API-powered recommendations.")
st.markdown("---")

# Create tabs for different features
tab1, tab2 = st.tabs(["🔍 Property Recommendations", "📍 Location Search"])

# Tab 1: Property Recommendations
with tab1:
    st.header('Find Similar Properties')
    
    # Load properties from API
    with st.spinner("Loading properties from API..."):
        properties = get_properties()
    
    if not properties:
        st.error("Failed to load properties from API.")
    else:
        # Create columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_apartment = st.selectbox(
                'Select an apartment',
                sorted(properties)
            )
        
        with col2:
            num_recommendations = st.slider(
                'Number of recommendations',
                min_value=3,
                max_value=20,
                value=5
            )
        
        # Preference settings
        with st.expander("⚙️ Customize Recommendation Preferences", expanded=False):
            st.markdown("**Quick Presets:**")
            preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
            
            preset_selected = None
            with preset_col1:
                if st.button("🎯 Balanced", use_container_width=True):
                    preset_selected = "balanced"
            with preset_col2:
                if st.button("💎 Luxury Focus", use_container_width=True):
                    preset_selected = "luxury"
            with preset_col3:
                if st.button("💵 Budget Focus", use_container_width=True):
                    preset_selected = "budget"
            with preset_col4:
                if st.button("📍 Location Focus", use_container_width=True):
                    preset_selected = "location"
            
            # Set weights based on preset
            if preset_selected == "balanced":
                default_facilities, default_price, default_location = 30, 20, 8
            elif preset_selected == "luxury":
                default_facilities, default_price, default_location = 45, 10, 5
            elif preset_selected == "budget":
                default_facilities, default_price, default_location = 10, 40, 5
            elif preset_selected == "location":
                default_facilities, default_price, default_location = 10, 10, 30
            else:
                default_facilities = st.session_state.get('weight_facilities', 30)
                default_price = st.session_state.get('weight_price', 20)
                default_location = st.session_state.get('weight_location', 8)
            
            st.markdown("---")
            st.markdown("**Adjust the importance of each factor:**")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("🏊 **Luxury Facilities**")
                st.caption("Swimming pool, gym, clubhouse, etc.")
                weight_facilities = st.slider(
                    'Facilities Weight',
                    min_value=0,
                    max_value=50,
                    value=default_facilities,
                    key='weight_facilities'
                )
            
            with col_b:
                st.markdown("💰 **Price & Area**")
                st.caption("Similar price range and area")
                weight_price = st.slider(
                    'Price/Area Weight',
                    min_value=0,
                    max_value=50,
                    value=default_price,
                    key='weight_price'
                )
            
            with col_c:
                st.markdown("📍 **Nearby Locations**")
                st.caption("Proximity to amenities")
                weight_location = st.slider(
                    'Location Weight',
                    min_value=0,
                    max_value=50,
                    value=default_location,
                    key='weight_location'
                )
            
            # Show weight distribution
            total_weight = weight_facilities + weight_price + weight_location
            if total_weight > 0:
                st.markdown("**Current Weight Distribution:**")
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    st.metric("Facilities", f"{(weight_facilities/total_weight*100):.0f}%")
                with col_y:
                    st.metric("Price/Area", f"{(weight_price/total_weight*100):.0f}%")
                with col_z:
                    st.metric("Location", f"{(weight_location/total_weight*100):.0f}%")
        
        if st.button('🔍 Get Recommendations', type="primary"):
            if weight_facilities == 0 and weight_price == 0 and weight_location == 0:
                st.error("⚠️ Please set at least one weight greater than 0!")
            else:
                with st.spinner('🔄 Fetching recommendations from API...'):
                    result = get_recommendations(
                        property_name=selected_apartment,
                        top_n=num_recommendations,
                        weight_facilities=weight_facilities,
                        weight_price=weight_price,
                        weight_location=weight_location
                    )
                
                if result:
                    recommendations = result.get('items', [])
                    st.success(f"✅ Found {len(recommendations)} similar properties!")
                    
                    st.markdown(f"### Recommendations for **{selected_apartment}**")
                    
                    # Calculate max score for percentage
                    max_score = max([r['score'] for r in recommendations]) if recommendations else 1
                    
                    # Display recommendations
                    for idx, rec in enumerate(recommendations, 1):
                        similarity_pct = (rec['score'] / max_score * 100) if max_score > 0 else 0
                        
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{idx}. {rec['property_name']}**")
                            with col2:
                                st.metric("Match", f"{similarity_pct:.1f}%")
                            st.progress(similarity_pct / 100)
                            st.markdown("---")

# Tab 2: Location Search
with tab2:
    st.header('Search by Location & Radius')
    
    # Load locations from API
    with st.spinner("Loading locations from API..."):
        locations = get_locations()
    
    if not locations:
        st.error("Failed to load locations from API.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_location = st.selectbox(
                'Location',
                sorted(locations)
            )
        
        with col2:
            radius = st.number_input(
                'Radius (km)',
                min_value=0.1,
                max_value=50.0,
                value=5.0,
                step=0.5
            )
        
        if st.button('🔍 Search', type="primary", key="location_search"):
            with st.spinner('🔄 Searching properties via API...'):
                result = search_by_location(
                    location=selected_location,
                    radius_km=radius
                )
            
            if result:
                items = result.get('items', [])
                count = result.get('count', 0)
                
                if count > 0:
                    st.success(f"✅ Found {count} properties within {radius} km of {selected_location}")
                    
                    # Display results
                    st.markdown("### Search Results")
                    for item in items:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.text(f"📍 {item['property_name']}")
                        with col2:
                            st.text(f"{item['distance_km']} km")
                else:
                    st.info(f"No properties found within {radius} km of {selected_location}")

st.markdown("---")
st.info("💡 All recommendations are powered by our FastAPI backend for optimal performance!")
