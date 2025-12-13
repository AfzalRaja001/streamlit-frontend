import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import get_options, predict_price, check_api_health

# Page configuration
st.set_page_config(
    page_title="Price Predictor | Gurgaon Real Estate",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .prediction-box {
        background-color: transparent;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #ddd;
        margin-top: 2rem;
    }
    .price-range {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .price-label {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Check API health
if not check_api_health():
    st.error("🚨 Cannot connect to API backend. Please ensure the FastAPI server is running.")
    st.code("cd FastAPIs\nuvicorn app:app --reload", language="bash")
    st.stop()

# Header
st.title('🏠 Gurgaon Real Estate Price Predictor')
st.markdown('### Get an instant AI-powered estimate for your property')
st.info("👋 Welcome! Fill in the details below to get a price prediction from our API.")
st.markdown('---')

# Fetch options from API
with st.spinner("Loading options from API..."):
    options = get_options()

if not options:
    st.error("Failed to load options from API. Please try again.")
    st.stop()

# Create form
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏢 Basic Details")
    property_type = st.selectbox(
        'Property Type',
        options['property_types'],
        help="Select the type of property"
    )
    sector = st.selectbox(
        'Sector',
        options['sectors'],
        help="Choose the sector in Gurgaon"
    )
    built_up_area = st.number_input(
        'Built Up Area (sq.ft)',
        min_value=100.0,
        max_value=10000.0,
        value=1000.0,
        step=50.0,
        help="Enter the total built-up area"
    )

with col2:
    st.markdown("#### 🛏️ Room Configuration")
    bedrooms = st.selectbox('Bedrooms', options['bedrooms'])
    bathrooms = st.selectbox('Bathrooms', options['bathrooms'])
    balcony = st.selectbox('Balconies', options['balconies'])

# Second row
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🏗️ Property Features")
    property_age = st.selectbox(
        'Property Age',
        options['age_possession'],
        help="Age or possession status"
    )
    furnishing_type = st.selectbox(
        'Furnishing Type',
        options['furnishing_types'],
        help="Level of furnishing"
    )
    floor_category = st.selectbox(
        'Floor Category',
        options['floor_categories'],
        help="Floor level category"
    )

with col4:
    st.markdown("#### ✨ Additional Amenities")
    luxury_category = st.selectbox(
        'Luxury Category',
        options['luxury_categories'],
        help="Luxury level of the property"
    )
    servant_room = st.selectbox(
        'Servant Room',
        [0.0, 1.0],
        format_func=lambda x: 'Yes' if x == 1.0 else 'No'
    )
    store_room = st.selectbox(
        'Store Room',
        [0.0, 1.0],
        format_func=lambda x: 'Yes' if x == 1.0 else 'No'
    )

st.markdown("---")

# Predict button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    predict_button = st.button(
        '🔮 Predict Property Price',
        type="primary",
        use_container_width=True
    )

if predict_button:
    if built_up_area <= 0:
        st.error("⚠️ Please enter a valid built-up area!")
    else:
        # Prepare request data
        property_data = {
            "property_type": property_type,
            "sector": sector,
            "bedRoom": float(bedrooms),
            "bathroom": float(bathrooms),
            "balcony": str(balcony),  # API expects string
            "agePossession": property_age,
            "built_up_area": float(built_up_area),
            "servant_room": float(servant_room),
            "store_room": float(store_room),
            "furnishing_type": furnishing_type,
            "luxury_category": luxury_category,
            "floor_category": floor_category
        }

        # Make API call
        with st.spinner('🔄 Analyzing property details via API...'):
            result = predict_price(property_data)

        if result:
            base_price = result['price_cr']
            low = base_price - 0.22
            high = base_price + 0.22

            # Display prediction
            st.markdown(f"""
                <div class="prediction-box">
                    <div class="price-label">Estimated Price Range</div>
                    <div class="price-range">₹{round(low, 2)} Cr - ₹{round(high, 2)} Cr</div>
                    <div class="price-label">Average: ₹{round(base_price, 2)} Cr</div>
                </div>
            """, unsafe_allow_html=True)

            # Additional information
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric(
                    label="Price per Sq.Ft",
                    value=f"₹{round((base_price * 10000000) / built_up_area):,}"
                )
            
            with col_b:
                st.metric(
                    label="Property Type",
                    value=property_type.title()
                )
            
            with col_c:
                st.metric(
                    label="Location",
                    value=sector.title()
                )

            
