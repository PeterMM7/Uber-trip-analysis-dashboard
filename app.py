import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import hmac
import hashlib
import numpy as np

st.set_page_config(
    page_title="Uber Trip Analysis - NYC",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with collapsed sidebar
)

# Optimize data loading with aggressive caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(file_path):
    # Read only necessary columns
    columns_to_use = [
        'pickup_datetime', 'dropoff_datetime', 'trip_miles',
        'base_passenger_fare', 'dispatching_base_num'
    ]
    df = pd.read_parquet(file_path, columns=columns_to_use)
    
    # Convert to smaller data types where possible
    df['trip_miles'] = df['trip_miles'].astype('float32')
    df['base_passenger_fare'] = df['base_passenger_fare'].astype('float32')
    
    return df

# Cache filtered data
@st.cache_data
def filter_data(df, start_date, end_date):
    mask = (df['pickup_datetime'].dt.date >= start_date) & \
           (df['pickup_datetime'].dt.date <= end_date)
    return df[mask]

# Cache aggregations
@st.cache_data
def aggregate_daily_trips(df):
    return df.resample('D', on='pickup_datetime').size()


# Initialize session state if not exists
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False


# Security function with explicit error handling
def check_password():
    if not hasattr(st, 'secrets') or 'password' not in st.secrets:
        st.error("Password not configured in secrets.toml")
        return False
    
    def password_entered():
        if 'password' in st.session_state:
            if st.session_state["password"] == st.secrets["password"]:
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    
    return st.session_state["password_correct"]

# Custom CSS (keeping your existing CSS)
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .stTitle {
        color: #0066cc;
        font-size: 3rem !important;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main application
if check_password():
    st.title("🚗 Uber Trip Analysis - NYC")
    
    # Data loading function with explicit error handling
    @st.cache_data
    def load_parquet_data(file_path):
        try:
            return pd.read_parquet(file_path)
        except Exception as e:
            st.error(f"Error reading parquet file: {str(e)}")
            return None

    # Load data
    try:
        file_path = os.path.join("data", "Uber_cleaned_data.parquet")
        
        if not os.path.exists(file_path):
            st.error(f"Data file not found at: {file_path}")
            st.write("Current working directory:", os.getcwd())
            uploaded_file = st.file_uploader("Upload your Uber dataset (Parquet format)", type=["parquet"])
            if uploaded_file:
                df = pd.read_parquet(uploaded_file)
            else:
                st.stop()
        else:
            df = load_parquet_data(file_path)
            
        if df is not None:
            st.session_state['data_loaded'] = True
            st.success("Data loaded successfully!")
            st.write("Data shape:", df.shape)
            
            # Convert datetime columns
            datetime_cols = ["pickup_datetime", "dropoff_datetime"]
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

            # Basic data validation
            required_cols = ["pickup_datetime", "dropoff_datetime", "trip_miles", "base_passenger_fare"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"Missing required columns: {missing_cols}")
                st.write("Available columns:", df.columns.tolist())
                st.stop()

            # Filters
            st.sidebar.header("📊 Filters")
            
            # Date range filter
            min_date = df["pickup_datetime"].min().date()
            max_date = df["pickup_datetime"].max().date()
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            # Apply filters
            mask = (df["pickup_datetime"].dt.date >= date_range[0]) & \
                   (df["pickup_datetime"].dt.date <= date_range[1])
            filtered_df = df[mask].copy()

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Trips", f"{len(filtered_df):,}")
            with col2:
                st.metric("Avg Distance", f"{filtered_df['trip_miles'].mean():.2f} miles")
            with col3:
                st.metric("Avg Fare", f"${filtered_df['base_passenger_fare'].mean():.2f}")
            with col4:
                st.metric("Total Revenue", f"${filtered_df['base_passenger_fare'].sum():,.2f}")

            # Create visualizations only if we have data
            if not filtered_df.empty:
                # Trip distribution plot
                st.subheader("Trip Distance Distribution")
                fig = px.histogram(filtered_df, x="trip_miles", nbins=50)
                st.plotly_chart(fig, use_container_width=True)
                
                # Time series plot
                st.subheader("Trips Over Time")
                daily_trips = filtered_df.resample('D', on='pickup_datetime').size()
                fig2 = px.line(x=daily_trips.index, y=daily_trips.values)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("No data available for the selected filters.")

        else:
            st.error("Failed to load data.")
            st.stop()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Debug info:")
        st.write("Current directory:", os.getcwd())
        st.write("Python version:", sys.version)
        st.write("Pandas version:", pd.__version__)
        st.stop()

else:
    st.warning("Please enter the correct password to view the dashboard.")