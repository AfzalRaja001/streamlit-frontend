import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api_client import get_options, predict_price, check_api_health

# Page configuration
st.set_page_config(
    page_title="Price Sensitivity Analyzer",
    page_icon="📊",
    layout="wide"
)

# Check API health
if not check_api_health():
    st.error("🚨 Cannot connect to API backend. Please ensure the FastAPI server is running.")
    st.code("cd FastAPIs\nuvicorn app:app --reload", language="bash")
    st.stop()

st.title("📊 Price Sensitivity & What-If Analysis")
st.markdown("""
Understand how changing a single feature impacts the predicted price. Start by defining your baseline property,
then adjust one parameter to see the estimated percentage change.
""")
st.markdown("---")

# Fetch options from API
with st.spinner("Loading options from API..."):
    options_data = get_options()

if not options_data:
    st.error("Failed to load options from API. Please try again.")
    st.stop()

# Feature configuration
feature_config = {
    "property_type": {
        "label": "Property Type",
        "type": "categorical",
        "options": options_data['property_types']
    },
    "sector": {
        "label": "Sector",
        "type": "categorical",
        "options": options_data['sectors']
    },
    "bedRoom": {
        "label": "Bedrooms",
        "type": "categorical",
        "options": options_data['bedrooms'],
        "format_func": lambda x: f"{int(x)} BHK" if isinstance(x, (int, float)) and float(x).is_integer() else f"{x} BHK"
    },
    "bathroom": {
        "label": "Bathrooms",
        "type": "categorical",
        "options": options_data['bathrooms'],
        "format_func": lambda x: f"{int(x)}" if isinstance(x, (int, float)) and float(x).is_integer() else f"{x}"
    },
    "balcony": {
        "label": "Balconies",
        "type": "categorical",
        "options": options_data['balconies'],
        "format_func": lambda x: str(x)
    },
    "agePossession": {
        "label": "Property Age / Possession",
        "type": "categorical",
        "options": options_data['age_possession']
    },
    "built_up_area": {
        "label": "Built Up Area (sq.ft)",
        "type": "numeric",
        "min": 100.0,
        "max": 10000.0,
        "step": 50.0
    },
    "servant_room": {
        "label": "Servant Room",
        "type": "binary",
        "options": [0.0, 1.0],
        "format_func": lambda x: "Yes" if x == 1.0 else "No"
    },
    "store_room": {
        "label": "Store Room",
        "type": "binary",
        "options": [0.0, 1.0],
        "format_func": lambda x: "Yes" if x == 1.0 else "No"
    },
    "furnishing_type": {
        "label": "Furnishing Type",
        "type": "categorical",
        "options": options_data['furnishing_types']
    },
    "luxury_category": {
        "label": "Luxury Category",
        "type": "categorical",
        "options": options_data['luxury_categories']
    },
    "floor_category": {
        "label": "Floor Category",
        "type": "categorical",
        "options": options_data['floor_categories']
    }
}

# Form for baseline property
with st.form("price_sensitivity_form"):
    st.subheader("1️⃣ Define Baseline Property")
    baseline = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        baseline["property_type"] = st.selectbox(
            feature_config["property_type"]["label"],
            feature_config["property_type"]["options"],
            key="baseline_property_type"
        )
        baseline["sector"] = st.selectbox(
            feature_config["sector"]["label"],
            feature_config["sector"]["options"],
            key="baseline_sector"
        )
        baseline["built_up_area"] = float(st.number_input(
            feature_config["built_up_area"]["label"],
            min_value=feature_config["built_up_area"]["min"],
            max_value=feature_config["built_up_area"]["max"],
            value=2000.0,
            step=feature_config["built_up_area"]["step"],
            key="baseline_built_up_area"
        ))
        baseline["furnishing_type"] = st.selectbox(
            feature_config["furnishing_type"]["label"],
            feature_config["furnishing_type"]["options"],
            key="baseline_furnishing"
        )
        baseline["luxury_category"] = st.selectbox(
            feature_config["luxury_category"]["label"],
            feature_config["luxury_category"]["options"],
            key="baseline_luxury"
        )
        baseline["floor_category"] = st.selectbox(
            feature_config["floor_category"]["label"],
            feature_config["floor_category"]["options"],
            key="baseline_floor"
        )
    
    with col2:
        baseline["bedRoom"] = st.selectbox(
            feature_config["bedRoom"]["label"],
            feature_config["bedRoom"]["options"],
            key="baseline_bedroom",
            format_func=feature_config["bedRoom"].get("format_func")
        )
        baseline["bathroom"] = st.selectbox(
            feature_config["bathroom"]["label"],
            feature_config["bathroom"]["options"],
            key="baseline_bathroom",
            format_func=feature_config["bathroom"].get("format_func")
        )
        baseline["balcony"] = st.selectbox(
            feature_config["balcony"]["label"],
            feature_config["balcony"]["options"],
            key="baseline_balcony",
            format_func=feature_config["balcony"].get("format_func")
        )
        baseline["agePossession"] = st.selectbox(
            feature_config["agePossession"]["label"],
            feature_config["agePossession"]["options"],
            key="baseline_age"
        )
        baseline["servant_room"] = st.selectbox(
            feature_config["servant_room"]["label"],
            feature_config["servant_room"]["options"],
            key="baseline_servant",
            format_func=feature_config["servant_room"].get("format_func")
        )
        baseline["store_room"] = st.selectbox(
            feature_config["store_room"]["label"],
            feature_config["store_room"]["options"],
            key="baseline_store",
            format_func=feature_config["store_room"].get("format_func")
        )
    
    st.markdown("---")
    st.subheader("2️⃣ Choose the Feature to Adjust")
    
    parameter_key = st.selectbox(
        "Which parameter would you like to modify?",
        list(feature_config.keys()),
        format_func=lambda x: feature_config[x]["label"],
        key="parameter_choice"
    )
    
    parameter_cfg = feature_config[parameter_key]
    baseline_value = baseline[parameter_key]
    
    # Input for new value based on type
    if parameter_cfg["type"] == "numeric":
        new_value = float(st.number_input(
            f"New value for {parameter_cfg['label']}",
            min_value=parameter_cfg["min"],
            max_value=parameter_cfg["max"],
            value=float(baseline_value),
            step=parameter_cfg.get("step", 50.0),
            key="new_value_numeric"
        ))
    elif parameter_cfg["type"] == "binary":
        options = parameter_cfg["options"]
        format_func = parameter_cfg.get("format_func", lambda x: str(x))
        default_index = options.index(baseline_value) if baseline_value in options else 0
        new_value = st.selectbox(
            f"New value for {parameter_cfg['label']}",
            options,
            index=default_index,
            format_func=format_func,
            key="new_value_binary"
        )
    else:  # categorical
        options = parameter_cfg["options"]
        format_func = parameter_cfg.get("format_func", lambda x: str(x))
        try:
            default_index = options.index(baseline_value)
        except ValueError:
            default_index = 0
        new_value = st.selectbox(
            f"New value for {parameter_cfg['label']}",
            options,
            index=default_index,
            format_func=format_func,
            key="new_value_categorical"
        )
    
    submitted = st.form_submit_button("Run Sensitivity Analysis", type="primary")

if submitted:
    if parameter_key == "built_up_area" and new_value <= 0:
        st.error("Built up area must be greater than zero.")
    elif baseline_value == new_value:
        st.warning("Please choose a different value to see the impact.")
    else:
        with st.spinner("🔄 Computing price impact via API..."):
            # Prepare baseline data for API
            baseline_data = {
                "property_type": baseline["property_type"],
                "sector": baseline["sector"],
                "bedRoom": float(baseline["bedRoom"]),
                "bathroom": float(baseline["bathroom"]),
                "balcony": str(baseline["balcony"]),
                "agePossession": baseline["agePossession"],
                "built_up_area": float(baseline["built_up_area"]),
                "servant_room": float(baseline["servant_room"]),
                "store_room": float(baseline["store_room"]),
                "furnishing_type": baseline["furnishing_type"],
                "luxury_category": baseline["luxury_category"],
                "floor_category": baseline["floor_category"]
            }
            
            # Get baseline price
            baseline_result = predict_price(baseline_data)
            
            if not baseline_result:
                st.error("Failed to get baseline prediction from API.")
                st.stop()
            
            base_price = baseline_result['price_cr']
            
            # Prepare updated data
            updated_data = baseline_data.copy()
            if parameter_key == "built_up_area":
                updated_data[parameter_key] = float(new_value)
            elif parameter_key in ["bedRoom", "bathroom", "servant_room", "store_room"]:
                updated_data[parameter_key] = float(new_value)
            elif parameter_key == "balcony":
                updated_data[parameter_key] = str(new_value)
            else:
                updated_data[parameter_key] = new_value
            
            # Get updated price
            updated_result = predict_price(updated_data)
            
            if not updated_result:
                st.error("Failed to get updated prediction from API.")
                st.stop()
            
            new_price = updated_result['price_cr']
        
        absolute_change = new_price - base_price
        percent_change = (absolute_change / base_price) * 100 if base_price else 0.0
        
        st.markdown("---")
        st.subheader("📈 Impact Summary")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Baseline Price", f"₹{base_price:.2f} Cr")
        with col_b:
            st.metric(
                "Updated Price",
                f"₹{new_price:.2f} Cr",
                delta=f"{percent_change:+.2f}% vs baseline"
            )
        with col_c:
            st.metric(
                "Absolute Change",
                f"₹{absolute_change:+.2f} Cr"
            )
        
        st.markdown(f"""
**Change applied:** `{feature_config[parameter_key]['label']}` from `{baseline_value}` → `{new_value}`.

• Estimated price change is **{percent_change:+.2f}%** (₹{absolute_change:+.2f} Cr).
• New predicted price stands at **₹{new_price:.2f} Cr** compared to baseline **₹{base_price:.2f} Cr**.
        """)
        
        comparison_df = pd.DataFrame({
            "Scenario": ["Baseline", "Updated"],
            "Price (Cr)": [round(base_price, 2), round(new_price, 2)],
            feature_config[parameter_key]["label"]: [baseline_value, new_value]
        })
        st.table(comparison_df)
        
        st.info("🔍 This analysis keeps all other features constant and only modifies the selected parameter via API predictions.")
else:
    st.info("👆 Configure the baseline property, pick a parameter to adjust, and click **Run Sensitivity Analysis** to view the impact.")
